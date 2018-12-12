from unittest.mock import MagicMock
from kubernetes.client.models.v1_delete_options import V1DeleteOptions

from controller import CredStashController


def test_delete_secret_empty():
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    credstash_secret = {}
    cont.delete_secret(credstash_secret)
    cont.v1core.assert_not_called()


def test_delete_secret_not_managed():
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    credstash_secret = {"metadata": {"namespace": "test"},
                        "spec": {"boom": {}}}
    cont.delete_secret(credstash_secret)
    cont.v1core.assert_not_called()


def test_delete_secret():
    cont = CredStashController("none", "none", "none", "none", "none")
    cont.v1core = MagicMock()
    credstash_secret = {"metadata": {"namespace": "test"},
                        "spec": {"boom": {}}}

    metadata = MagicMock()
    metadata.annotations = {"credstash-fully-managed": "true"}
    obj = MagicMock()
    obj.metadata = metadata

    cont.v1core.read_namespaced_secret = MagicMock(return_value=obj)
    cont.delete_secret(credstash_secret)
    cont.v1core.delete_namespaced_secret.assert_called_once_with(
        'boom', 'test', V1DeleteOptions())


def test_process_event_invalid_namespace():
    controller = CredStashController("none", "none", "none", "none", "none")

    event = {'object': {
        "spec": {"boo": "ba"

                 },
        "metadata": {
            "namespace": "boom"
        }

    },
        "type": "DELETED"
    }
    controller.delete_secret = MagicMock()
    controller.process_event(event)
    controller.delete_secret.assert_not_called()


def test_process_event_no_spec():
    controller = CredStashController("none", "none", "none", "none", "none")

    event = {'object': {
        "spec": {},
        "metadata": {
            "namespace": "boom"
        }

    },
        "type": "DELETED"
    }
    controller.delete_secret = MagicMock()
    controller.process_event(event)
    controller.delete_secret.assert_not_called()


def test_process_event_delete():
    controller = CredStashController("none", "none", "none", "none", "boom")

    event = {'object': {
        "spec": {"boom"},
        "metadata": {
            "namespace": "boom",
            "name": "test"
        }

    },
        "type": "DELETED"
    }
    controller.delete_secret = MagicMock()
    controller.process_event(event)
    controller.delete_secret.assert_called_once_with(event['object'])


def test_process_event_delete_wildcard_ns():
    controller = CredStashController("none", "none", "none", "none", "*")

    event = {'object': {
        "spec": {"boom"},
        "metadata": {
            "namespace": "boom",
            "name": "test"
        }

    },
        "type": "DELETED"
    }
    controller.delete_secret = MagicMock()
    controller.process_event(event)
    controller.delete_secret.assert_called_once_with(event['object'])


def test_process_event_modified():
    controller = CredStashController("none", "none", "none", "none", "boom")

    event = {'object': {
        "spec": {"boom"},
        "metadata": {
            "namespace": "boom",
            "name": "test"
        }

    },
        "type": "MODIFIED"
    }
    controller.update_secret = MagicMock()
    controller.process_event(event)
    controller.update_secret.assert_called_once_with(event['object'])


def test_process_event_created():
    controller = CredStashController("none", "none", "none", "none", "boom")

    event = {'object': {
        "spec": {"boom"},
        "metadata": {
            "namespace": "boom",
            "name": "test"
        }

    },
        "type": "ADDED"
    }
    controller.update_secret = MagicMock()
    controller.process_event(event)
    controller.update_secret.assert_called_once_with(event['object'])

