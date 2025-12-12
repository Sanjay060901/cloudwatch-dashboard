import boto3
import os
import datetime

REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
EC2_ID = os.getenv("EC2_ID", "")

ec2 = boto3.client("ec2", region_name=REGION)
cw = boto3.client("cloudwatch", region_name=REGION)

async def fetch_ec2_instances():
    if EC2_ID:
        response = ec2.describe_instances(InstanceIds=[EC2_ID])
    else:
        response = ec2.describe_instances()

    instances = []
    for r in response["Reservations"]:
        for i in r["Instances"]:
            instances.append({
                "InstanceId": i["InstanceId"],
                "Type": i["InstanceType"],
                "State": i["State"]["Name"],
                "AZ": i["Placement"]["AvailabilityZone"]
            })
    return instances

async def fetch_metrics(instance_id):
    now = datetime.datetime.utcnow()
    ago = now - datetime.timedelta(hours=1)

    def metric(Name):
        data = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName=Name,
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=ago,
            EndTime=now,
            Period=300,
            Statistics=["Average"]
        )

        return [d["Average"] for d in data["Datapoints"]]

    return {
        "CPUUtilization": metric("CPUUtilization"),
        "NetworkIn": metric("NetworkIn"),
        "NetworkOut": metric("NetworkOut"),
        "DiskReadBytes": metric("DiskReadBytes"),
        "DiskWriteBytes": metric("DiskWriteBytes"),
    }
