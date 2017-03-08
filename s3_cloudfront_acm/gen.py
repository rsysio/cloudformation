# Create it in us-east-1 as per
# https://cloudonaut.io/pitfall-acm-certificate-cloudfront-cloudformation/

from troposphere import GetAtt, Join, Output, Condition, Equals, Not
from troposphere import Parameter, Ref, Template
from troposphere.cloudfront import Distribution, DistributionConfig, ViewerCertificate
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.cloudfront import ForwardedValues
from troposphere.cloudfront import S3Origin
from troposphere.certificatemanager import Certificate, DomainValidationOption
from troposphere.s3 import Bucket, BucketPolicy
from troposphere.route53 import RecordSetType, AliasTarget


t = Template()

t.add_description('Serving static content from an S3 bucket with CloudFront')

# www.myawesomesite.com
domain_name = t.add_parameter(Parameter(
    'domainName',
    Description = 'Domain name for your site',
    Type        = 'String'
))

# awesomesite.com
zone_apex = t.add_parameter(Parameter(
    'zoneApex',
    Description = 'Root domain name www.[example.com]',
    Type        = 'String'
))

origin_access_id = t.add_parameter(Parameter(
    'originAccessIdentity',
    Description = 'Origin Access Identity ID',
    Type        = 'String'
))

zone_id = t.add_parameter(Parameter(
    'zoneId',
    Description = 'Route53 zone Id to create cname in',
    Type = 'String',
    Default = ''
))

#############
# Conditions
#############

zone_set_cond = t.add_condition(
    'zoneIdSet',
    Not(Equals(Ref(zone_id), ''))
)

#############
# Resources
#############

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

s3_bucket = t.add_resource(Bucket('myBucket'))

bucket_policy = t.add_resource(BucketPolicy(
    'myBucketPolicy',
    Bucket          = Ref(s3_bucket),
    PolicyDocument  = {
        'Version'   : '2012-10-17',
        'Id'        : 'PolicyForCloudFrontPrivateContent',
        'Statement' : [
            {
               'Sid'        : ' Grant a CloudFront Origin Identity access to support private content',
               'Effect'     : 'Allow',
               'Principal'  : {
                    'AWS' : Join(' ', ['arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity', Ref(origin_access_id)])
                },
               'Action'     : 's3:GetObject',
               'Resource'   : Join('', [ 'arn:aws:s3:::', Ref(s3_bucket), '/*' ])
            }
       ]
    }
))

# CloudFront distribution
my_distribution = t.add_resource(Distribution(
    'myDistribution',
    DependsOn = 'myCert',
    # config object here
    DistributionConfig  = DistributionConfig(
        Aliases = [Ref(domain_name)],
        # list of origins
        Origins = [
            Origin(
                Id              = Ref('AWS::StackName'),
                DomainName      = GetAtt(s3_bucket, 'DomainName'),
                S3OriginConfig  = S3Origin(OriginAccessIdentity=Join('', [
                        'origin-access-identity/cloudfront/',
                        Ref(origin_access_id),
                    ])
                )
            )
        ],
        # default cache
        DefaultCacheBehavior = DefaultCacheBehavior(
            TargetOriginId          = Ref('AWS::StackName'),
            ForwardedValues         = ForwardedValues(QueryString=False),
            ViewerProtocolPolicy    = 'redirect-to-https'
        ),
        # enable it
        Enabled             = True,
        # we want http2 in 2017
        HttpVersion         = 'http2',
        # cheap and cheerful
        PriceClass          = 'PriceClass_200',
        # add SSL
        ViewerCertificate   =  ViewerCertificate(
            AcmCertificateArn   = Ref(ssl_certificate),
            SslSupportMethod    = 'sni-only'
        ),
        DefaultRootObject   = 'index.html'
    )
))

dns_record = t.add_resource(RecordSetType(
    'aliasDnsRecord',
    Condition = 'zoneIdSet',
    HostedZoneId = Ref(zone_id),
    Name = Join('', [Ref(domain_name), '.']),
    Type = 'A',
    AliasTarget = AliasTarget(
        HostedZoneId = GetAtt(Ref(my_distribution), 'CanonicalHostedZoneNameID'),
        DNSName = GetAtt(Ref(my_distribution), 'DomainName'),
        EvaluateTargetHealth = False
    )
))

# Outputs
t.add_output([
    # find by Id in console
    Output('DistributionId', Value=Ref(my_distribution)),
    # Point CNAME here
    Output('DistributionName',
        Value=Join('', ['http://', GetAtt(Ref(my_distribution), 'DomainName')])),

])

print(t.to_json())
