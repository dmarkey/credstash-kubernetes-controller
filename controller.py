import base64
import credstash
import os
import traceback
from botocore.exceptions import ClientError
from kubernetes import client, config, watch
from kubernetes.client import V1DeleteOptions, V1ObjectMeta
from kubernetes.client.rest import ApiException

DOMAIN = "credstash.local"
api_version = "v1"


class ResourceTooOldException(Exception):
    pass


class CredStashController:
    def __init__(
        self,
        access_key_id,
        secret_access_key,
        default_region,
        default_table,
        namespaces,
    ):

        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.default_region = default_region
        self.default_table = default_table
        if namespaces != "*":
            self.namespaces = namespaces.split(",")
        else:
            self.namespaces = None

    def _init_client(self):
        if "KUBERNETES_PORT" in os.environ:
            config.load_incluster_config()
        else:
            config.load_kube_config()
        api_client = client.api_client.ApiClient()
        self.v1core = client.CoreV1Api(api_client)
        self.crds = client.CustomObjectsApi(api_client)

    def check_resource_version(self, secret_obj, resource_version):
        if resource_version is not None:
            if int(resource_version) <= int(
                secret_obj.metadata.annotations.get(
                    "credstash-resourceversion", -1
                )
            ):
                raise ResourceTooOldException()
            else:
                secret_obj.metadata.annotations[
                    "credstash-resourceversion"
                ] = str(resource_version)

    def update_secret(self, credstash_secret, resource_version):
        try:
            namespace = credstash_secret["metadata"]["namespace"]
            name = credstash_secret["metadata"]["name"]
            spec = credstash_secret["spec"]
        except KeyError:
            print("Missing standard metadata, bailing out!")
            return

        new = True
        try:
            secret_obj = self.v1core.read_namespaced_secret(
                name, namespace=namespace
            )
            new = False
            try:
                self.check_resource_version(secret_obj, resource_version)
            except ResourceTooOldException:
                print("We've already processed this event, skipping")
                return
        except ApiException as e:
            if e.status != 404:
                raise
            if resource_version is None:
                resource_version = -1
            metadata = V1ObjectMeta(
                name=name,
                namespace=namespace,
                annotations={
                    "credstash-fully-managed": "true",
                    "credstash-resourceversion": str(resource_version),
                },
            )
            secret_obj = client.V1Secret(api_version, {}, "Secret", metadata)

        if (
            new
            or secret_obj.metadata.annotations.get(
                "credstash-fully-managed", None
            )
            == "true"
        ):
            secret_obj.data = {}
        for secret_to_process in spec:
            try:
                table = self.default_table
                if "table" in secret_to_process:
                    table = secret_to_process["table"]
                raw_secret = credstash.getSecret(
                    name=secret_to_process["from"],
                    table=table,
                    version=secret_to_process["version"],
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    region=self.default_region,
                )
                secret_obj.data[secret_to_process["name"]] = base64.b64encode(
                    raw_secret.encode()
                ).decode()
            except ClientError:
                traceback.print_exc()
                print("ERROR: Error fetching secret, bailing out!")
                return
            except credstash.ItemNotFound:
                print(
                    "ERROR: {} version {} not found, bailing out!".format(
                        secret_to_process["from"], secret_to_process["version"]
                    )
                )
                return
            except KeyError as e:
                print(
                    "{} is missing for this secret, bailing out!".format(
                        e.args[0]
                    )
                )
                return

        if new:
            print(
                "Creating new secret {}/{} with {} items".format(
                    namespace, name, len(secret_obj.data)
                )
            )
            try:
                self.v1core.create_namespaced_secret(namespace, secret_obj)
            except ApiException as e:
                print("Problem creating this secret - {}".format(e))
                return

        else:
            print(
                "Updating secret {}/{} with {} items".format(
                    namespace, name, len(secret_obj.data)
                )
            )
            try:
                self.v1core.patch_namespaced_secret(
                    name, namespace, secret_obj
                )
            except ApiException as e:
                print("Problem updating this secret - {}".format(e))
                return

    def process_event(self, event, resource_version=None):
        print("Event received. - {}".format(event["type"]))

        obj = event["object"]
        operation = event["type"]
        if operation == "ERROR":
            print("Error Received - {}, giving up".format(event))
            raise Exception("Error event received")
        spec = obj.get("spec")
        if not spec:
            return
        namespace = obj["metadata"]["namespace"]
        if self.namespaces is not None and namespace not in self.namespaces:
            print(
                "Secret requested from an " "unauthorized namespace, skipping."
            )
            return
        metadata = obj.get("metadata")

        name = metadata["name"]
        print("Handling %s on %s/%s" % (operation, namespace, name))
        if operation in ("ADDED", "MODIFIED"):
            self.update_secret(obj, resource_version)
        if operation == "DELETED":
            self.delete_secret(obj, resource_version)

    def main_loop(self):
        while True:
            print("Waiting for credstash secrets to be defined...")
            self._init_client()
            stream = watch.Watch().stream(
                self.crds.list_cluster_custom_object,
                DOMAIN,
                "v1",
                "credstashsecrets"
            )

            for event in stream:
                obj = event["object"]
                metadata = obj.get("metadata")
                spec = obj.get("spec")
                code = obj.get("code")

                if code == 410:
                    print("Received HTTP 410, restarting..")
                    break

                if not metadata or not spec:
                    continue

                if metadata["resourceVersion"] is not None:
                    resource_version = metadata["resourceVersion"]

                self.process_event(event, resource_version)

    def delete_secret(self, credstash_secret, resource_version):
        namespace = credstash_secret["metadata"]["namespace"]
        name = credstash_secret["metadata"]["name"]
        try:
            secret_obj = self.v1core.read_namespaced_secret(
                name, namespace=namespace
            )
            try:
                self.check_resource_version(secret_obj, resource_version)
            except ResourceTooOldException:
                print("We've already processed this event, skipping")
                return
        except ApiException as e:
            if e.status != 404:
                raise
            else:
                "Secret already deleted, returning"
                return

        if (
            secret_obj.metadata.annotations.get(
                "credstash-fully-managed", None
            )
            == "true"
        ):
            print("{} is managed by credstash, deleting it".format(name))
            self.v1core.delete_namespaced_secret(
                name, namespace, V1DeleteOptions()
            )
        else:
            print(
                "{} is NOT managed by credstash, NOT deleting it".format(name)
            )


if __name__ == "__main__":

    main_access_key_id = os.environ["CREDSTASH_AWS_ACCESS_KEY_ID"]
    main_secret_access_key = os.environ["CREDSTASH_AWS_SECRET_ACCESS_KEY"]
    main_default_region = os.environ["CREDSTASH_AWS_DEFAULT_REGION"]
    main_default_table = os.environ.get(
        "CREDSTASH_DEFAULT_TABLE", "credential-store"
    )
    main_namespaces = os.environ.get("namespaces", "*")

    credstash_controller = CredStashController(
        main_access_key_id,
        main_secret_access_key,
        main_default_region,
        main_default_table,
        main_namespaces,
    )

    credstash_controller.main_loop()
