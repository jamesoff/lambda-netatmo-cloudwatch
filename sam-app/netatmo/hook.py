import boto3
import os


def lambda_handler(event, context):
    client = boto3.client("lambda")
    result = "Succeeded"
    try:
        response = client.invoke(
            FunctionName=os.environ["NewVersion"], InvocationType="RequestResponse"
        )
        if "FunctionError" in response and response["FunctionError"] != "":
            print("Detected error in invocation: {}".format(response["FunctionError"]))
            result = "Failed"
    except Exception as exception:
        print("Caught exception while invoking function")
        print(exception)
        result = "Failed"

    deployment_id = event["DeploymentId"]
    lifecycle_event_hook_execution_id = event["LifecycleEventHookExecutionId"]
    codedeploy_client = boto3.client("codedeploy")
    codedeploy_client.put_lifecycle_event_hook_execution_status(
        deploymentId=deployment_id,
        lifecycleEventHookExecutionId=lifecycle_event_hook_execution_id,
        status=result,
    )

    return {"statusCode": 200}
