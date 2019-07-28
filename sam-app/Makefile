PLATFORM=$(shell uname)
ifeq "$(PLATFORM)" "Darwin"
	CONTAINER_FLAG="-u"
else
	CONTAINER_FLAG="-u"
endif

build:
	cd netatmo; pipenv lock -r > requirements.txt
	sam build $(CONTAINER_FLAG)

package:
	sam package --s3-bucket code.jamesoff.net-lhr --output-template-file output.yml

deploy:
	aws cloudformation deploy --template-file output.yml --stack-name netatmo-cloudwatch --capabilities CAPABILITY_IAM
