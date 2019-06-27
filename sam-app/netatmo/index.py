import os
import boto3
import lnetatmo


cloudwatch_client = boto3.client("cloudwatch")


def main():
    auth = lnetatmo.ClientAuth(username=os.environ["NETATMO_USERNAME"])
    weather_data = lnetatmo.WeatherStationData(auth)
    last_data = weather_data.lastData("Kingston Road")
    for device in last_data.keys():
        metric_data = []
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
        cloudwatch_client.put_metric_data(Namespace="netatmo", MetricData=metric_data)


def lambda_handler(event, contect):
    main()


if __name__ == "__main__":
    main()
