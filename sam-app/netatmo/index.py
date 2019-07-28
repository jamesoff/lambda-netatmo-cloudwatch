"""Fetch data from Netatmo and send it to CloudWatch."""

import boto3
import lnetatmo
import time


ssm_client = boto3.client("ssm")
parameters = ssm_client.get_parameters_by_path(
    Path="/netatmo", Recursive=True, WithDecryption=True
)
params = {}
print("Loading parameters")
for param in parameters["Parameters"]:
    param_name = param["Name"].split("/")[-1].upper().replace("-", "_")
    print("... {}".format(param_name))
    params[param_name] = param["Value"]

cloudwatch_client = boto3.client("cloudwatch")
auth = lnetatmo.ClientAuth(
    clientId=params["CLIENT_ID"],
    clientSecret=params["CLIENT_SECRET"],
    username=params["NETATMO_USERNAME"],
    password=params["NETATMO_PASSWORD"],
)


def post_metrics(metric_data):
    """Send prepared metric data to CloudWatch"""
    cloudwatch_client.put_metric_data(Namespace="netatmo", MetricData=metric_data)


def post_error_metric():
    post_metrics(
        [
            {
                "MetricName": "apierror",
                "Timestamp": time.time(),
                "Value": 1,
                "Unit": "Count",
            }
        ]
    )


def main():
    """Fetch data from Netatmo and interate through it, posting to CloudWatch
    Metrics"""
    try:
        weather_data = lnetatmo.WeatherStationData(auth)
        last_data = weather_data.lastData(params["NETATMO_STATION"])
    except TypeError:
        print("Caught error from letnatmo, aborting")
        post_error_metric()
        return
    if not last_data:
        # lnetatmo eats the Exception and returns None if there's a problem
        print("Failed to get data from Netatmo, aborting")
        post_error_metric()
        return
    # Init metric_data with our API success status
    metric_data = [
        {
            "MetricName": "apierror",
            "Timestamp": time.time(),
            "Value": 0,
            "Unit": "Count",
        }
    ]
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
            if len(metric_data) > 19:
                post_metrics(metric_data)
                metric_data = []
    if len(metric_data):
        post_metrics(metric_data)


def lambda_handler(event, context):
    """Handle invocation from Lambda. Currently this is the same as being run
    directly, so just call main."""
    main()


if __name__ == "__main__":
    main()
