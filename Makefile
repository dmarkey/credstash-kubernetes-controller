IMAGE := davidjmarkey/credstash-kubernetes-controller

test:
	pytest

image:
	docker build -t $(IMAGE) .

push-image:
	docker push $(IMAGE)


.PHONY: image push-image test
