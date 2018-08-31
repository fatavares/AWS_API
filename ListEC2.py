"""
Script to relate all the instances with the private AMI
Build to verify which Private AMI migrated for SMS already have an instance deployed
In migrations, AMIs with a already deployed instance can be deleted to decrease the cost with Storage
"""

import boto3
import json

ec2 = boto3.client('ec2')
amilist = ["Add the AMI List here"]
instancelist =[]
a=0

for n in amilist:
    try:
        instance = ec2.describe_instances(
            Filters=[
                {
                    'Name': 'image-id',
                    'Values': [
                        n
                    ]
                 },
             ],
        )
        var1 = instance['Reservations']
        var2 = var1[0]
        var3 = var2['Instances']
        var4 = var3[0]
        var5 = var4['InstanceId']

    except:
        var5 = ''

    instanceFullValue = str(var5) + ',' + str(n)
    print('INSTANCE ' + instanceFullValue)
    instancelist.insert(a, str(instanceFullValue))
    a += 1

print(instancelist)
