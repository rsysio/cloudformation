.PHONY: run
run:
	@cat cloudformation.json | jq
	@aws s3 cp cloudformation.json s3://rsysio-cf/s3-hosting.json
