"""
Script to list current Volumes in a AWS account, list the current Snapshots and verify if the Snapshots were taken from
an existing Volume.
Snapshots that are not related to any Volume can generate an undesirable cost
"""

import boto3


ec2 = boto3.client('ec2')
volumeList = []
snapshotList = []
noVolSnapList = []

instance = ec2.describe_instances()
snapshots = ec2.describe_snapshots(
    Filters=[
        {
            'Name': 'owner-id',
            'Values': [
                'AWS account number'
            ]
        },
    ],
)

def listVol():
    print(instance)
    var1 = instance['Reservations']
    for n in var1:
        var2 = n['Instances']
        var3 = var2[0]
        var4 = var3['BlockDeviceMappings']
        for m in var4:
            var5 = m['Ebs']
            volId = var5['VolumeId']
            volumeList.append(str(volId))

def listSnap():
    var1 = snapshots['Snapshots']
    for n in var1:
        var2 = n['Description']
        var3 = n['SnapshotId']
        var4 = n['VolumeId']
        snapInfo = tuple((var2, var3, var4))
        snapshotList.append(snapInfo)

def noVolSnap():
    for n in snapshotList:
        var1 = 0
        for m in volumeList:
            if n[2] == m:
                var1 = 0
                break
            else:
                var1 += 1
        if var1 > 0:
            noVolSnapList.append(n[2])

listVol()
listSnap()
print(volumeList)
print(snapshotList)
noVolSnap()
print(len(noVolSnapList))
print(noVolSnapList)

