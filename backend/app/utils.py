from datetime import datetime, timezone

def now_utc():
    return datetime.now(timezone.utc)

def aws_cloudwatch_metric_console(region, namespace, metricname, dimension_name, dimension_value):
    # metricsV2 deep link format - works in most console setups
    # returns URL that filters to metricName and dimension
    return (
        f"https://console.aws.amazon.com/cloudwatch/home?region={region}"
        f"#metricsV2:graph=~(metrics~(~(~'{namespace}~'{metricname}~'{dimension_name}~'{dimension_value})))"
    )
