build:
	sam build -u

package:
	sam package --s3-bucket code.jamesoff.net-lhr --output-template-file output.yml

deploy:
	aws cloudformation deploy --template-file output.yml --stack-name netatmo-cloudwatch --capabilities CAPABILITY_IAM
