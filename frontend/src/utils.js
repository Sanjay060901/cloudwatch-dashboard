export function aws_cloudwatch_link_for_metric(instanceId, metricName){
  const region = "ap-south-1"; // sync with backend region or change to dynamic
  return `https://console.aws.amazon.com/cloudwatch/home?region=${region}#metricsV2:graph=~(metrics~(~(~'AWS/EC2~'${metricName}~'InstanceId~'${instanceId})))`;
}
