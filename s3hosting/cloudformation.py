# Converted from CloudFront_S3.template located at:
# http://aws.amazon.com/cloudformation/aws-cloudformation-templates/

from troposphere import GetAtt, Join, Output
from troposphere import Parameter, Ref, Template
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.cloudfront import ForwardedValues
from troposphere.cloudfront import S3Origin


t = Template()

t.add_description("Hosting static files in S3 with Cloudfront")

s3dnsname = t.add_parameter(Parameter(
    "S3DNSName",
    Description="The DNS name of an existing S3 bucket to use as the "
                "Cloudfront distribution origin",
    Type="String",
))

myDistribution = t.add_resource(Distribution(
    "myDistribution",
    DistributionConfig=DistributionConfig(
        Origins=[
            Origin(Id="Origin1", DomainName=Ref(s3dnsname), S3OriginConfig=S3Origin())
            ],
        DefaultCacheBehavior=DefaultCacheBehavior(
            TargetOriginId="Origin1",
            ForwardedValues=ForwardedValues(
                QueryString=False
            ),
            ViewerProtocolPolicy="allow-all"),
        Enabled=True,
        HttpVersion='http2'
    )
))

t.add_output([
    Output("DistributionId", Value=Ref(myDistribution)),
    Output(
        "DistributionName",
        Value=Join("", ["http://", GetAtt(myDistribution, "DomainName")])),
])

print(t.to_json())
