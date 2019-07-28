# Netatmo to CloudWatch Metrics

This code will fetch your Netatmo metrics from your weather station and send them to CloudWatch, so you can create a CloudWatch dashboard and alarms.

I put it together because I didn't like the Netatmo dashboard for a few reasons:

* You can't put all the temperatures (humidities, etc) on one graph to compare them.
* It automatically scales the (particularly) lower bound(s) of the graphs, so a couple of units change can look massive on the graph (and you can't compare between different metrics visually)
* It doesn't show a marker on all graphs as you hover on one to let you match up events quickly

## Deploying

You will need:

* An AWS Account
* AWS SAM CLI and AWS CLI with suitable credentials available in your environment
* An S3 bucket (not public) for the deployment process to use
* Netatmo app credentials; set up your account and app on <https://dev.netatmo.com/> and grab your client id and client secret.
* Docker to be installed (used for build process)

Method:

1. Edit the Makefile to set the name of your bucket
2. In SSM Parameter Store, create the following parameters as **SecureString**s with the default KMS key:
    * `netatmo/client-id` and `netatmo/client-secret`, with the values from the Netatmo dev portal.
    * `netatmo/netatmo-username` and `netatmo/netatmo-password`, with your Netatmo credentials
    * `netatmo/netatmo-station`, with the name of your weather station
3. `make build`, which will use a Docker container (downloaded on first use) to build the Lambda deployable
4. `make package`, which will upload the deployable to the S3 bucket and output an updated CloudFormation template referencing it
5. `make deploy`, which will create or update the CloudFormation stack which sets up the environment. On updates, CodeDeploy is used.

The function should then run every 5 minutes and save metrics to CloudWatch in the "Netatmo" namespace.

If you would like to use CodePipeline/CodeBuild to run deployments, a `buildspec.yml` is included.
