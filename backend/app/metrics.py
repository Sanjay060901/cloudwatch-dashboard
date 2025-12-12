import os
from flask import Blueprint, jsonify, request
from .collector import list_instances, get_metric_data_for_instance
from .cache import SimpleTTLCache
from .logger import get_logger
from datetime import datetime, timedelta, timezone

logger = get_logger("metrics")
bp = Blueprint("metrics", __name__)

cache = SimpleTTLCache()
POLL_PERIOD_SECONDS = int(os.getenv("POLL_PERIOD_SECONDS", "60"))
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")

@bp.route("/instances")
def api_instances():
    single_id = request.args.get("instanceId") or os.getenv("EC2_ID") or None
    cache_key = f"instances:{single_id or 'all'}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"instances": cached})

    inst = list_instances(single_instance_id=single_id)
    cache.set(cache_key, inst, POLL_PERIOD_SECONDS)
    return jsonify({"instances": inst})

@bp.route("/metrics")
def api_metrics():
    instance_id = request.args.get("instanceId")
    if not instance_id:
        return jsonify({"error": "instanceId required"}), 400

    # period and range
    period = int(request.args.get("period", 300))
    hours = int(request.args.get("hours", 1))
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)

    cache_key = f"metrics:{instance_id}:{period}:{hours}"
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"instanceId": instance_id, "metrics": cached})

    # prepare MetricDataQueries for a few important metrics
    # CPUUtilization (Average), NetworkIn/Out (Sum), DiskReadBytes (Sum), DiskWriteBytes (Sum)
    metrics_queries = []
    def add_query(id_, name, stat):
        metrics_queries.append({
            "Id": id_,
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/EC2",
                    "MetricName": name,
                    "Dimensions": [{"Name": "InstanceId", "Value": instance_id}]
                },
                "Period": period,
                "Stat": stat
            },
            "ReturnData": True,
            "Label": name
        })

    add_query("m1", "CPUUtilization", "Average")
    add_query("m2", "NetworkIn", "Sum")
    add_query("m3", "NetworkOut", "Sum")
    add_query("m4", "DiskReadBytes", "Sum")
    add_query("m5", "DiskWriteBytes", "Sum")

    results = get_metric_data_for_instance(instance_id, metrics_queries, start, end, period)
    cache.set(cache_key, results, POLL_PERIOD_SECONDS)
    return jsonify({"instanceId": instance_id, "metrics": results})
