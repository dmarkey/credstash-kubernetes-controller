# Credstash Controller for Kubernetes

[![Build Status](https://travis-ci.org/dmarkey/credstash-kubernetes-controller.svg?branch=master)](https://travis-ci.org/dmarkey/credstash-kubernetes-controller)

*This is still a very early project so may not be stable and probably has bugs.*


## What does it do?
It allows users of kubernetes to use credstash in a more declarative way, but without having to commit your secrets to git (bad!).

Instead a controller runs on your kubernetes cluster and watches for Credstash secret definitions to be added. When they are the controller fetches whatever secrets from credstash and then creates a "real" secret your kubernetes pod can use.

## Why?

I seen the way https://github.com/bitnami-labs/sealed-secrets was implemented and how it allows secret management with GitOps without commiting secrets to git. Unfortunatley the project I was working on is already using credstash so I decided to have a go a creating a controller that would use parts of the sealed secrets design but use Credstash as the backend.

## How does it work?

The controller is installed in the cluster and it has the AWS credentials to access your credstash, it watches for CresStashSecret resources to be created. It then fetches the requested secrets out of CredStash and creates the correct Kubernetes secret.

## Usage

Download all the manifests out of the "yaml" directory. Prepare your AWS KEY ID and SECRET KEY by base64'ing them using something like `echo -n $AWS_ACCESS_KEY_ID | base64`  and adding them to `aws-secrets.yaml`. Do that for the `CREDSTASH_AWS_ACCESS_KEY_ID`, `CREDSTASH_AWS_SECRET_ACCESS_KEY` and `CREDSTASH_AWS_DEFAULT_REGION`. After that apply all the manifests. you may omit the `sample-css.yaml` as this is just an example.

### Creation of secrets
To try it out edit the sample and add a secret definition. The name of the CredStashSecrrt will become the name of the real secret. Add an entry for each secret, with the following:

1. name - Name of the secret as it will be in the real secret
2. key: the name of the secret as it is in credstash
3. version: The version of the secret. This MUST be the "full" version that's usually something like `0000000000000000001`
4. table: this is optional, but in case the secret isnt in the default table configured in the deployment.

Once the CredStashSecret is created after a small delay the "real" secret will be created.

### Deletion of secrets.
If you delete a secret in the CredStashSecret definition is will be deleted in the Secret.

If you delete the entire object the corresponding secret will be deleted as well.

## Security concerns.
By default the controller will accept requests from all namespaces. If the cluster is multi-tenent this may not be acceptable. To tell the contreoller to only accept requests from specific namespaces set the `namespaces` environment variable to a comma seperated list of namespaces and requests from other namespaces will be ignored.

## Troubleshooting

My secret never get created, what gives?

Check that the credstash-controller pod isnt crashing and check its log output with `kubectl logs <pod name> -n kube-system`
