import os
import asyncio
from datetime import datetime, timedelta
import boto3

from .cache import Cache

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
POLL_PERIOD = int(os.getenv("POLL_PERIOD_SECONDS", "60"))

cloudwatch = boto3.client("cloudwatch", region_name=AWS_REGION)

METRICS = [
    {
        "namespace": "AWS/EC2",
        "metric_name": "CPUUtilization",
        "dimensions": lambda: [
            {"Name": "InstanceId", "Value": os.getenv("EC2_ID", "")}
        ],
        "stat": "Average",
        "key": "ec2_cpu"
    },
    {
        "namespace": "AWS/RDS",
        "metric_name": "CPUUtilization",
        "dimensions": lambda: [
            {"Name": "DBInstanceIdentifier", "Value": os.getenv("RDS_ID", "")}
        ],
        "stat": "Average",
        "key": "rds_cpu"
    },
    {
        "namespace": "AWS/S3",
        "metric_name": "BucketSizeBytes",
        "dimensions": lambda: [
            {"Name": "BucketName", "Value": os.getenv("S3_BUCKET", "")},
            {"Name": "StorageType", "Value": "StandardStorage"}
        ],
        "stat": "Average",
        "key": "s3_size"
    }
]

class Collector:
    def __init__(self, cache: Cache):
        self.cache = cache

    def get_metric(self, metric):
        now = datetime.utcnow()
        resp = cloudwatch.get_metric_statistics(
            Namespace=metric["namespace"],
            MetricName=metric["metric_name"],
            Dimensions=[d for d in metric["dimensions"]() if d["Value"]],
            StartTime=now - timedelta(minutes=10),
            EndTime=now,
            Period=60,
            Statistics=[metric["stat"]]
        )
        points = resp.get("Datapoints", [])
        if not points:
            return None

        latest = sorted(points, key=lambda p: p["Timestamp"])[-1]

        return {
            "value": latest.get(metric["stat"], None),
            "timestamp": latest["Timestamp"].isoformat(),
        }

    async def run_once(self):
        data = {"metrics": {}}
        for m in METRICS:
            data["metrics"][m["key"]] = self.get_metric(m)

        await self.cache.set_latest(data)

    async def start(self):
        while True:
            await self.run_once()
            await asyncio.sleep(POLL_PERIOD)
