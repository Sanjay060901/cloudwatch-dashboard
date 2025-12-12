from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import boto3
import os
from datetime import datetime, timedelta

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REGION = os.getenv("AWS_REGION", "ap-south-1")
EC2_ID = os.getenv("EC2_ID", "")

ec2 = boto3.client("ec2", region_name=REGION)
cw = boto3.client("cloudwatch", region_name=REGION)

# --------------------------
# GET INSTANCE LIST
# --------------------------
@app.get("/api/instances")
def list_instances():
    try:
        if EC2_ID:
            resp = ec2.describe_instances(InstanceIds=[EC2_ID])
        else:
            resp = ec2.describe_instances()
    except Exception as e:
        return {"instances": [], "error": str(e)}

    instances = []
    for r in resp.get("Reservations", []):
        for i in r.get("Instances", []):
            instances.append({
                "id": i["InstanceId"],
                "type": i.get("InstanceType"),
                "state": i["State"]["Name"],
                "launch_time": str(i["LaunchTime"]),
            })

    return {"instances": instances}

# --------------------------
# GET CLOUDWATCH METRICS
# --------------------------
@app.get("/api/metrics/{instance_id}")
def get_metrics(instance_id: str):

    end = datetime.utcnow()
    start = end - timedelta(hours=1)

    def metric(name, stat="Average"):
        try:
            return cw.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName=name,
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start,
                EndTime=end,
                Period=300,
                Statistics=[stat]
            ).get("Datapoints", [])
        except Exception:
            return []

    return {
        "CPUUtilization": metric("CPUUtilization"),
        "NetworkIn": metric("NetworkIn", "Sum"),
        "NetworkOut": metric("NetworkOut", "Sum"),
        "DiskReadBytes": metric("DiskReadBytes", "Sum"),
        "DiskWriteBytes": metric("DiskWriteBytes", "Sum"),
        "StatusCheckFailed": metric("StatusCheckFailed"),
        "timestamp": datetime.utcnow().isoformat(),
    }
