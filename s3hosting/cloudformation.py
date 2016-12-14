# Converted from CloudFront_S3.template located at:
# http://aws.amazon.com/cloudformation/aws-cloudformation-templates/

from troposphere import GetAtt, Join, Output
from troposphere import Parameter, Ref, Template
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.cloudfront import ForwardedValues
from troposphere.cloudfront import S3Origin
from troposphere.s3 import Bucket, PublicRead
from troposphere.certificatemanager import Certificate, DomainValidationOption

t = Template()

t.add_description("Hosting static files in S3 with Cloudfront")

##################
#
# Parameters
#
##################
myFqdn = t.add_parameter(
    Parameter(
        "FQDN",
        Description="fully qualified domain name",
        Type="String",
    )
)

##################
#
# Resources
#
##################

# S3 bucket
s3bucket = t.add_resource(
    Bucket("S3Bucket", AccessControl=PublicRead)
)

# Cloudfront distro
myDistribution = t.add_resource(
    Distribution(
        "myDistribution",
        DistributionConfig=DistributionConfig(
            Origins=[
                Origin(
                    Id="Origin1",
                    DomainName=Ref(myFqdn),
                    S3OriginConfig=S3Origin()
                )
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
    )
)

# SSL cert
t.add_resource(
    Certificate(
        'mycert',
        DomainName=Ref(myFqdn),
        DomainValidationOptions=[
            DomainValidationOption(
                DomainName=Ref(myFqdn),
                ValidationDomain=Ref(myFqdn),
            ),
        ],
        Tags=[
            {
                'Key': 'domainName',
                'Value': Ref(myFqdn)
            },
        ],
    )
)

##################
#
# Outputs
#
##################
t.add_output([
    Output("DistributionId", Value=Ref(myDistribution)),
    Output(
        "DistributionName",
        Value=Join("", ["http://", GetAtt(myDistribution, "DomainName")])),
])

print(t.to_json())
