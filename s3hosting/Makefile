.PHONY: upload
upload:
	aws s3 cp cloudformation.json s3://rsysio-cf/s3-hosting.json

.PHONY: run
run:
	@python cloudformation.py | tee cloudformation.json | jq
