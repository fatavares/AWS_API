import boto3
import json

client = boto3.client('route53')

response = client.list_health_checks()
# response = client.get_health_check(
#     HealthCheckId=''
)
#response = client.list_hosted_zones()
#response = client.list_hosted_zones_by_name()
#response = client.list_resource_record_sets(
#    HostedZoneId=''
#)

json_str = json.dumps(response, indent=4)
print(json_str)
