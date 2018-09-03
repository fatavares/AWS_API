"""
Script to list current Volumes in a AWS account, list the current Snapshots and verify if the Snapshots were taken from
an existing Volume.
Snapshots that are not related to any Volume can generate an undesirable cost
"""

import boto3

ec2 = boto3.resource('ec2')
volumeList = []
snapshotList = []
noVolSnapList = []


# If you do not filter this query will return all snapshots from public AMIs
snapshots = ec2.snapshots.filter(
        Filters=[
            {
                'Name': 'owner-id',
                'Values': [
                    '#AWS Account number'
                ]
            },
        ],
    )

# Lists all volumes in your account
def listVol():
    volumes = ec2.volumes.all()
    for vol in volumes:
        volumeList.append(str(vol.id))

# Lists all snapshots in your account
def listSnap():
    for snap in snapshots:
        snapInfo = tuple((snap.snapshot_id, snap.description, snap.volume_id, snap.volume_size))
        snapshotList.append(snapInfo)

# Lists all stored snapshots that have no relation with your current Volumes
def noVolSnap():
    for snap in snapshotList:
        var1 = 0
        for vol in volumeList:
            if snap[2] == vol:
                var1 = 0
                break
            else:
                var1 += 1
        if var1 > 0:
            noVolSnapList.append(tuple((snap[0], snap[1], snap[3])))

listVol()
listSnap()
#print(volumeList)
#print(snapshotList)
noVolSnap()

print("Snapshots of missing volumes = " + str(len(noVolSnapList)))
t = 0
for n in noVolSnapList:
    print(str(n[0]) + " - " + str(n[1]) + " - " + str(n[2]) + "GiB")
    t += n[2]

print("Total of Storage - " + str(t) + "GiB")
