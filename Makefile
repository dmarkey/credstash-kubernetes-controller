IMAGE := davidjmarkey/credstash-kubernetes-controller

test:
	pytest

image:
	docker build -t $(IMAGE) .

push-image:
	 [ ! -z "$$TRAVIS_TAG" ] && echo "$$DOCKER_PASSWORD" | docker login -u "$$DOCKER_USERNAME" --password-stdin


.PHONY: image push-image test
