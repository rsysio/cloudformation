.PHONY: run
run:
	@python cloudformation.py > cloudformation.json
	@cat cloudformation.json | jq
	@aws s3 cp cloudformation.json s3://rsysio-cf/s3-hosting.json
