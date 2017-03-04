# Converted from CloudFront_S3.template located at:
# http://aws.amazon.com/cloudformation/aws-cloudformation-templates/

from troposphere import GetAtt, Join, Output, Sub
from troposphere import Parameter, Ref, Template
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.cloudfront import ForwardedValues
from troposphere.cloudfront import S3Origin
from troposphere.certificatemanager import Certificate, DomainValidationOption
from troposphere.s3 import Bucket, BucketPolicy


t = Template()

t.add_description(
    "AWS CloudFormation Sample Template CloudFront_S3: Sample template "
    "showing how to create an Amazon CloudFront distribution using an "
    "S3 origin. "
    "**WARNING** This template creates a CloudFront distribution. "
    "You will be billed for the AWS resources used if you create "
    "a stack from this template.")

# www.myawesomesite.com
domain_name = t.add_parameter(Parameter(
    "domainName",
    Description = "Domain name for your site",
    Type        = "String"
))

# awesomesite.com
zone_apex = t.add_parameter(Parameter(
    "zoneApex",
    Description = "Root domain name www.[example.com]",
    Type        = "String"
))

# why is this not in cloudformation AWS ???!
origin_access_id = t.add_parameter(Parameter(
    "originAccessIdentity",
    Description = "Amazon S3 Canonical User ID (79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be)",
    Type        = "String"
))

############
# Resources
############

# SSL cert for CloudFront
ssl_certificate = t.add_resource(Certificate(
    'myCert',
    DomainName              = Ref(domain_name),
    DomainValidationOptions = [
        DomainValidationOption(
            DomainName          = Ref(domain_name),
            ValidationDomain    = Ref(zone_apex),
        ),
    ],
))

s3_bucket = t.add_resource(Bucket(
    'myBucket',
))

bucket_policy = t.add_resource(BucketPolicy(
    "myBucketPolicy",
    Bucket = Ref(s3_bucket),
    PolicyDocument = {
        "Version" : "2012-10-17",
        "Id" : "PolicyForCloudFrontPrivateContent",
        "Statement" : [
            {
               "Sid" : " Grant a CloudFront Origin Identity access to support private content",
               "Effect" : "Allow",
               "Principal" : {"CanonicalUser" : Ref(origin_access_id)},
               "Action" : "s3:GetObject",
               "Resource" : Ref(s3_bucket)
            }
       ]
    }
))

# CloudFront distribution
myDistribution = t.add_resource(Distribution(
    "myDistribution",
    # config object here
    DistributionConfig  = DistributionConfig(
        # list of origins
        Origins = [
            Origin(
                Id              = "Origin1",
                DomainName      = Ref(domain_name),
                S3OriginConfig  = S3Origin())
        ],
        # default cache
        DefaultCacheBehavior = DefaultCacheBehavior(
            TargetOriginId          = "Origin 1",
            ForwardedValues         = ForwardedValues(QueryString=False),
            ViewerProtocolPolicy    = "allow-all"),
        # enable it
        Enabled     = True,
        # we want http2 in 2017
        HttpVersion = 'http2'
    )
))

# Outputs
t.add_output([

    Output("DistributionId", Value=Ref(myDistribution)),

    Output("DistributionName",
        Value=Join("", ["http://", GetAtt(myDistribution, "DomainName")])),

])

print(t.to_json())