from kubernetes.client import V1Secret, V1ObjectMeta
from kubernetes.client.rest import ApiException
from unittest.mock import MagicMock, patch, Mock
from kubernetes.client.models.v1_delete_options import V1DeleteOptions

from controller import CredStashController


def test_update_secret_empty():
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    credstash_secret = {}
    cont.update_secret(credstash_secret, None)
    cont.v1core.patch_namespaced_secret.assert_not_called()
    cont.v1core.create_namespaced_secret.assert_not_called()


def test_update_secret_empty_spec():
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    cont.v1core.read_namespaced_secret = MagicMock(
        side_effect=ApiException(status=404)
    )
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": {},
    }
    cont.update_secret(credstash_secret, resource_version=1)

    assert (
        cont.v1core.create_namespaced_secret.call_args_list[0][0][0] == "test"
    )
    assert cont.v1core.create_namespaced_secret.call_args_list[0][0][
        1
    ].to_dict() == {
        "api_version": "v1",
        "data": {},
        "kind": "Secret",
        "metadata": {
            "annotations": {
                "credstash-fully-managed": "true",
                "credstash-resourceversion": "1",
            },
            "cluster_name": None,
            "creation_timestamp": None,
            "deletion_grace_period_seconds": None,
            "deletion_timestamp": None,
            "finalizers": None,
            "generate_name": None,
            "generation": None,
            "initializers": None,
            "labels": None,
            "name": "boom",
            "namespace": "test",
            "owner_references": None,
            "resource_version": None,
            "self_link": None,
            "uid": None,
        },
        "string_data": None,
        "type": None,
    }


def test_update_secret_invalid_keys():
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    credstash_secret = {
        "metadata": {"namespace": "test"},
        "spec": {"boom": [{"boom": "ba"}]},
    }
    cont.update_secret(credstash_secret, resource_version=1)
    cont.v1core.patch_namespaced_secret.assert_not_called()
    cont.v1core.create_namespaced_secret.assert_not_called()


@patch("controller.credstash.getSecret", return_value="123")
def test_update_secret_valid_key(credstash_get_secret_mock):
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    cont.v1core.read_namespaced_secret = MagicMock(
        side_effect=ApiException(status=404)
    )
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": [{"from": "ba", "name": "lala", "version": "0001"}],
    }
    cont.update_secret(credstash_secret, resource_version=1)

    assert (
        cont.v1core.create_namespaced_secret.call_args_list[0][0][0] == "test"
    )
    assert cont.v1core.create_namespaced_secret.call_args_list[0][0][
        1
    ].to_dict() == {
        "api_version": "v1",
        "data": {"lala": "MTIz"},
        "kind": "Secret",
        "metadata": {
            "annotations": {
                "credstash-fully-managed": "true",
                "credstash-resourceversion": "1",
            },
            "cluster_name": None,
            "creation_timestamp": None,
            "deletion_grace_period_seconds": None,
            "deletion_timestamp": None,
            "finalizers": None,
            "generate_name": None,
            "generation": None,
            "initializers": None,
            "labels": None,
            "name": "boom",
            "namespace": "test",
            "owner_references": None,
            "resource_version": None,
            "self_link": None,
            "uid": None,
        },
        "string_data": None,
        "type": None,
    }

    credstash_get_secret_mock.assert_called_once_with(
        aws_access_key_id="none",
        aws_secret_access_key="none",
        name="ba",
        region="none",
        table="none",
        version="0001",
    )


@patch("controller.credstash.getSecret", return_value="123")
def test_update_secret_valid_key_different_table(credstash_get_secret_mock):
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    cont.v1core.read_namespaced_secret = MagicMock(
        side_effect=ApiException(status=404)
    )
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": [
            {
                "from": "ba",
                "name": "lala",
                "version": "0001",
                "table": "development",
            }
        ],
    }
    cont.update_secret(credstash_secret, resource_version=1)

    assert (
        cont.v1core.create_namespaced_secret.call_args_list[0][0][0] == "test"
    )
    assert cont.v1core.create_namespaced_secret.call_args_list[0][0][
        1
    ].to_dict() == {
        "api_version": "v1",
        "data": {"lala": "MTIz"},
        "kind": "Secret",
        "metadata": {
            "annotations": {
                "credstash-fully-managed": "true",
                "credstash-resourceversion": "1",
            },
            "cluster_name": None,
            "creation_timestamp": None,
            "deletion_grace_period_seconds": None,
            "deletion_timestamp": None,
            "finalizers": None,
            "generate_name": None,
            "generation": None,
            "initializers": None,
            "labels": None,
            "name": "boom",
            "namespace": "test",
            "owner_references": None,
            "resource_version": None,
            "self_link": None,
            "uid": None,
        },
        "string_data": None,
        "type": None,
    }

    credstash_get_secret_mock.assert_called_once_with(
        aws_access_key_id="none",
        aws_secret_access_key="none",
        name="ba",
        region="none",
        table="development",
        version="0001",
    )


@patch("controller.credstash.getSecret", return_value="123")
def test_update_secret_valid_key_multiple(credstash_get_secret_mock):
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    cont.v1core.read_namespaced_secret = MagicMock(
        side_effect=ApiException(status=404)
    )
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": [
            {"from": "ba", "name": "lala", "version": "0001"},
            {"from": "bo", "name": "lala2", "version": "0001"},
        ],
    }
    cont.update_secret(credstash_secret, resource_version=None)

    assert (
        cont.v1core.create_namespaced_secret.call_args_list[0][0][0] == "test"
    )
    assert cont.v1core.create_namespaced_secret.call_args_list[0][0][
        1
    ].to_dict() == {
        "api_version": "v1",
        "data": {"lala": "MTIz", "lala2": "MTIz"},
        "kind": "Secret",
        "metadata": {
            "annotations": {
                "credstash-fully-managed": "true",
                "credstash-resourceversion": "-1",
            },
            "cluster_name": None,
            "creation_timestamp": None,
            "deletion_grace_period_seconds": None,
            "deletion_timestamp": None,
            "finalizers": None,
            "generate_name": None,
            "generation": None,
            "initializers": None,
            "labels": None,
            "name": "boom",
            "namespace": "test",
            "owner_references": None,
            "resource_version": None,
            "self_link": None,
            "uid": None,
        },
        "string_data": None,
        "type": None,
    }

    credstash_get_secret_mock.assert_called_with(
        aws_access_key_id="none",
        aws_secret_access_key="none",
        name="bo",
        region="none",
        table="none",
        version="0001",
    )


@patch("controller.credstash.getSecret", return_value="123")
def test_update_secret_valid_key_existing(credstash_get_secret_mock):
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    metadata = V1ObjectMeta(
        name="bobo",
        namespace="default",
        annotations={"credstash-fully-managed": "true"},
    )
    mock_secret = V1Secret("v1", {}, "Secret", metadata)

    cont.v1core.read_namespaced_secret = MagicMock(return_value=mock_secret)
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": [{"from": "ba", "name": "lala", "version": "0001"}],
    }
    cont.update_secret(credstash_secret, resource_version=10)

    assert (
        cont.v1core.patch_namespaced_secret.call_args_list[0][0][0] == "boom"
    )
    assert cont.v1core.patch_namespaced_secret.call_args_list[0][0][
        2
    ].to_dict() == {
        "api_version": "v1",
        "data": {"lala": "MTIz"},
        "kind": "Secret",
        "metadata": {
            "annotations": {
                "credstash-fully-managed": "true",
                "credstash-resourceversion": "10",
            },
            "cluster_name": None,
            "creation_timestamp": None,
            "deletion_grace_period_seconds": None,
            "deletion_timestamp": None,
            "finalizers": None,
            "generate_name": None,
            "generation": None,
            "initializers": None,
            "labels": None,
            "name": "bobo",
            "namespace": "default",
            "owner_references": None,
            "resource_version": None,
            "self_link": None,
            "uid": None,
        },
        "string_data": None,
        "type": None,
    }

    credstash_get_secret_mock.assert_called_once_with(
        aws_access_key_id="none",
        aws_secret_access_key="none",
        name="ba",
        region="none",
        table="none",
        version="0001",
    )


@patch("controller.credstash.getSecret", return_value="123")
def test_update_secret_bad_resource_version(credstash_get_secret_mock):
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    metadata = V1ObjectMeta(
        name="bobo",
        namespace="default",
        annotations={
            "credstash-fully-managed": "true",
            "credstash-resourceversion": "2",
        },
    )
    mock_secret = V1Secret("v1", {}, "Secret", metadata)

    cont.v1core.read_namespaced_secret = MagicMock(return_value=mock_secret)
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": [{"from": "ba", "name": "lala", "version": "0001"}],
    }
    assert cont.update_secret(credstash_secret, resource_version=1) is None
    credstash_get_secret_mock.assert_not_called()
    cont.v1core.patch_namespaced_secret.assert_not_called()
    cont.v1core.create_namespaced_secret.assert_not_called()


@patch("controller.credstash.getSecret", return_value="123")
def test_update_secret_valid_key_existing_not_managed(
    credstash_get_secret_mock
):
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    metadata = V1ObjectMeta(
        name="bobo",
        namespace="default",
        annotations={"credstash-fully-managed": "false"},
    )
    mock_secret = V1Secret("v1", {"secret": "poo"}, "Secret", metadata)

    cont.v1core.read_namespaced_secret = MagicMock(return_value=mock_secret)
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": [{"from": "ba", "name": "lala", "version": "0001"}],
    }
    cont.update_secret(credstash_secret, resource_version=1)

    assert (
        cont.v1core.patch_namespaced_secret.call_args_list[0][0][0] == "boom"
    )
    assert cont.v1core.patch_namespaced_secret.call_args_list[0][0][
        2
    ].to_dict() == {
        "api_version": "v1",
        "data": {"lala": "MTIz", "secret": "poo"},
        "kind": "Secret",
        "metadata": {
            "annotations": {
                "credstash-fully-managed": "false",
                "credstash-resourceversion": "1",
            },
            "cluster_name": None,
            "creation_timestamp": None,
            "deletion_grace_period_seconds": None,
            "deletion_timestamp": None,
            "finalizers": None,
            "generate_name": None,
            "generation": None,
            "initializers": None,
            "labels": None,
            "name": "bobo",
            "namespace": "default",
            "owner_references": None,
            "resource_version": None,
            "self_link": None,
            "uid": None,
        },
        "string_data": None,
        "type": None,
    }

    credstash_get_secret_mock.assert_called_once_with(
        aws_access_key_id="none",
        aws_secret_access_key="none",
        name="ba",
        region="none",
        table="none",
        version="0001",
    )


def test_delete_secret_empty():
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    credstash_secret = {"metadata": {"namespace": "test", "name": "boom"}}
    cont.delete_secret(credstash_secret, resource_version=1)
    cont.v1core.delete_secret.assert_not_called()


def test_delete_secret_not_managed():
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": [],
    }
    cont.delete_secret(credstash_secret, resource_version=1)
    cont.v1core.delete_secret.assert_not_called()


def test_delete_secret():
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": [],
    }

    metadata = MagicMock()
    metadata.annotations = {"credstash-fully-managed": "true"}
    obj = MagicMock()
    obj.metadata = metadata

    cont.v1core.read_namespaced_secret = MagicMock(return_value=obj)
    cont.delete_secret(credstash_secret, resource_version=1)
    cont.v1core.delete_namespaced_secret.assert_called_once_with(
        "boom", "test", V1DeleteOptions()
    )


def test_process_event_invalid_namespace():
    controller = CredStashController("none", "none", "none", "none", "none")

    event = {
        "object": {
            "spec": [{"name": "lala"}],
            "metadata": {"namespace": "boom", "name": "boom"},
        },
        "type": "DELETED",
    }
    controller.delete_secret = MagicMock()
    controller.process_event(event)
    controller.delete_secret.assert_not_called()


def test_process_event_no_spec():
    controller = CredStashController("none", "none", "none", "none", "none")

    event = {
        "object": {
            "spec": {},
            "metadata": {"namespace": "boom", "name": "boom"},
        },
        "type": "DELETED",
    }
    controller.delete_secret = MagicMock()
    controller.process_event(event)
    controller.delete_secret.assert_not_called()


def test_process_event_delete():
    controller = CredStashController("none", "none", "none", "none", "boom")

    event = {
        "object": {
            "spec": {"boom"},
            "metadata": {"namespace": "boom", "name": "test"},
        },
        "type": "DELETED",
    }
    controller.delete_secret = MagicMock()
    controller.process_event(event)
    controller.delete_secret.assert_called_once_with(event["object"], None)


def test_process_event_delete_wildcard_ns():
    controller = CredStashController("none", "none", "none", "none", "*")

    event = {
        "object": {
            "spec": {"boom"},
            "metadata": {"namespace": "boom", "name": "test"},
        },
        "type": "DELETED",
    }
    controller.delete_secret = MagicMock()
    controller.process_event(event)
    controller.delete_secret.assert_called_once_with(event["object"], None)


def test_process_event_modified():
    controller = CredStashController("none", "none", "none", "none", "boom")

    event = {
        "object": {
            "spec": {"boom"},
            "metadata": {"namespace": "boom", "name": "test"},
        },
        "type": "MODIFIED",
    }
    controller.update_secret = MagicMock()
    controller.process_event(event)
    controller.update_secret.assert_called_once_with(event["object"], None)


def test_process_event_created():
    controller = CredStashController("none", "none", "none", "none", "boom")

    event = {
        "object": {
            "spec": {"boom"},
            "metadata": {"namespace": "boom", "name": "test"},
        },
        "type": "ADDED",
    }
    controller.update_secret = MagicMock()
    controller.process_event(event)
    controller.update_secret.assert_called_once_with(event["object"], None)


@patch("controller.credstash.getSecret", return_value="123")
def test_delete_secret_bad_resource_version(credstash_get_secret_mock):
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    metadata = V1ObjectMeta(
        name="bobo",
        namespace="default",
        annotations={
            "credstash-fully-managed": "true",
            "credstash-resourceversion": "2",
        },
    )
    mock_secret = V1Secret("v1", {}, "Secret", metadata)

    cont.v1core.read_namespaced_secret = MagicMock(return_value=mock_secret)
    credstash_secret = {
        "metadata": {"namespace": "test", "name": "boom"},
        "spec": [{"from": "ba", "name": "lala", "version": "0001"}],
    }
    assert cont.delete_secret(credstash_secret, resource_version=1) is None
    credstash_get_secret_mock.assert_not_called()
    cont.v1core.patch_namespaced_secret.assert_not_called()
    cont.v1core.delete_namespaced_secret.assert_not_called()
