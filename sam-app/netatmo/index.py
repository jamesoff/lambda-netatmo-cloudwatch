"""Fetch data from Netatmo and send it to CloudWatch."""

import os
import boto3
import lnetatmo


cloudwatch_client = boto3.client("cloudwatch")
auth = lnetatmo.ClientAuth(username=os.environ["NETATMO_USERNAME"])


def post_metrics(metric_data):
    """Send prepared metric data to CloudWatch"""
    cloudwatch_client.put_metric_data(Namespace="netatmo", MetricData=metric_data)


def main():
    """Fetch data from Netatmo and interate through it, posting to CloudWatch
    Metrics"""
    weather_data = lnetatmo.WeatherStationData(auth)
    last_data = weather_data.lastData(os.environ["NETATMO_STATION"])
    metric_data = []
    for device in last_data.keys():
        device_data = last_data[device]
        when = device_data["When"]
        del device_data["When"]
        for name, value in last_data[device].items():
            if isinstance(value, str):
                continue
            metric = {
                "MetricName": name,
                "Dimensions": [{"Name": "Device", "Value": device}],
                "Timestamp": when,
                "Value": value,
            }
            metric_data.append(metric)
            print("Number of metrics: {}".format(len(metric_data)))
            if len(metric_data) > 19:
                print("Posting")
                post_metrics(metric_data)
                metric_data = []
    print("Loop finished, number of metrics to post: {}".format(metric_data))
    if len(metric_data):
        post_metrics(metric_data)


def lambda_handler(event, context):
    """Handle invocation from Lambda. Currently this is the same as being run
    directly, so just call main."""
    main()


if __name__ == "__main__":
    main()
