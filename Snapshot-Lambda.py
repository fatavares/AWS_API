"""
Lambda script made to create Snapshots from Volumes Tagged with Backup=yes
Create Monthly, Weekly and Daily Snapshots.
"""
import boto3
import datetime
import time


# define the connection
ec2 = boto3.resource('ec2')

# set the snapshot removal offset
cleanDate = datetime.datetime.now() - datetime.timedelta(minutes=3)


def lambda_handler(event, context):

    volList = listBackupVolumes()
    print(volList)
    for vol in volList:
        volume = ec2.Volume(vol)
        tagList = []
        nm = 0
        # Prepare Volume tags to be imported into the snapshot
        for t in volume.tags:
            # pull the name tag
            if t['Key'] == 'Name':
                instanceName = t['Value']
                tagList.append(t)
                nm += 1

            else:
                tagList.append(t)

        # Snapshots of Volumes without a Name tag will receive one
        if nm == 0:
            instanceName = 'Unnamed Volume'

        # Create a tag for each Backup Type
        date = datetime.datetime.today()
        if date.day == 1:
            tagList.append({'Key': 'Type', 'Value': 'Monthly'})
            description = str(datetime.datetime.now()) + "-" + instanceName + "-" + volume.id + "-automated_monthly"


        elif date.weekday() == 6:
            tagList.append({'Key': 'Type', 'Value': 'Weekly'})
            description = str(datetime.datetime.now()) + "-" + instanceName + "-" + volume.id + "-automated_weekly"


        else:
            tagList.append({'Key': 'Type', 'Value': 'Daily'})
            description = str(datetime.datetime.now()) + "-" + instanceName + "-" + volume.id + "-automated_daily"

        takeSnapshot(tagList, volume.id, description)

    print("[LOG] Cleaning out old entries starting on " + str(cleanDate))

    # clean up old snapshots
    for snap in ec2.snapshots.filter(
            Filters=[
                {
                    'Name': 'owner-id',
                    'Values': [
                        'AWS Account number',
                    ]
                },
            ],
    ):
        print(snap.tags)
        # Set snapshot timezone to GMT-3
        snapDate = snap.start_time.replace(tzinfo=None) - datetime.timedelta(hours=3)

        try:
            # Filter snapshots based on Backup Type Tag
            for i in snap.tags:
                # (dateType, dateValue, keyValue)
                if (date.day == 1) and (i['Key'] == 'Type' and i['Value'] == 'Monthly'):
                    cleanSnapshot(snap.id, snapDate, cleanDate)

                elif (date.weekday() == 6) and (i['Key'] == 'Type' and i['Value'] == 'Weekly'):
                    cleanSnapshot(snap.id, snapDate, cleanDate)

                elif i['Key'] == 'Type' and i['Value'] == 'Daily':
                    cleanSnapshot(snap.id, snapDate, cleanDate)
        except:
            print("[INFO] Snapshot: " + snap.id + " has no Tags ")

# List Volumes that are tagged for Backup (Tag Backup=yes)
def listBackupVolumes():
    volumes = ec2.volumes.all()
    backupVol = []
    print("VOLUMES")
    print(volumes)

    for vol in volumes:
        print("VOLUME")
        print(vol)
        if vol.tags is not None:
            print("TAGS")
            print(vol.tags)
            for tag in vol.tags:
                if tag['Key'].lower() == 'backup' and tag['Value'].lower() == 'yes':
                    backupVol.append(vol.id)

    return backupVol


# Create Snapshots with the tags
def takeSnapshot(tagList, volumeId, description):
    # snapshot that server
    snapshot = ec2.create_snapshot(VolumeId=volumeId, Description=description)

    # write the tags to the snapshot
    tags = snapshot.create_tags(
        Tags=tagList
    )
    print("[LOG] " + str(snapshot))


# Delete Snapshots older than cleanDate variable
def cleanSnapshot(snapId, snapDate, cleanDate):
    snap = ec2.Snapshot(snapId)
    # Compare the clean dates
    print(cleanDate > snapDate)
    if cleanDate > snapDate:
        print("[INFO] Deleting: " + snap.id + " - From: " + str(snapDate))
        try:
            snapshot = snap.delete()

        except:
            # if we timeout because of a rate limit being exceeded, give it a rest of a few seconds
            print("[INFO]: Waiting 5 Seconds for the API to Chill")
            time.sleep(5)
            snapshot = snap.delete()
        print("[INFO] " + str(snapshot))


lambda_handler(1,1)
