# exports all vars
.EXPORT_ALL_VARIABLES:

# used when wanting to rsync (. hidden) files
#SHELL := bash -O dotglob or extglob

# include environment variables file
ifneq (,$(wildcard ./.env))
    include  .env
    export
endif


#------------------------------------------------
#-------- list codebuild role names
#------------------------------------------------
make_venv:
	python -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt

venv:
	. .venv/bin/activate

build_image:
	# for i in $$nodejs_projs $$py_projs $$scala_aato_projs $$scala_backoffice_projs $$nodejs_projs; do \
	# 	echo "build-$$i-service-role"; \
	# done
	docker build -t sm/fastapi_app .

save_image:
	docker save sm/fastapi_app -o fastapi_app.tgz

push_image:
	rsync -aP -e "ssh -i ~/.ssh/aws.pem" *  ubuntu@10.7.8.5:/mnt/efs/fs1/home/dev/aws/sns/

run_dockermode:
	docker run --rm --name fastapi_app -p 8000:8000 sm/fastapi_app

run_devmode:
	uvicorn app.main:app --workers 1 --host "0.0.0.0" --reload --access-log --port 8000

sync:
    # include the hidden virtual env folder
	# shopt -s dotglob
	rsync -avzrP -e "ssh -i ~/.ssh/aws.pem" *  ubuntu@10.62.21.56:/mnt/efs/fs1/home/dev/cicdctl/

run_remote:
	ssh -q vm2 'cd /mnt/efs/fs1/home/dev/cicdctl/; source .venv/bin/activate; make run_devmode;'

remote_check:
	ssh -q vm2 'curl -s http://localhost:8000/ping'
	ssh -q vm2 'curl -s http://localhost:8000/listbuildprojects'

open_docs:
	open http://localhost:8000/docs


# not needed
# assume_session_test:
# 	set -x
# 	echo "Please enter the token code"
# 	read TOKEN_CODE
# 	echo $$TOKEN_CODE
# 	ROLE_ARN=arn:aws:iam::829018605820:role/teams/VyzeCloudFormationRole
# 	MFA_SERIAL_NUMBER=arn:aws:iam::308921073415:mfa/sanjay.mijar@mastercard.com
# 	#export TOKEN_CODE=$1
# 	AWS_CA_BUNDLE="../certs/ncl.loc.pem"

#     CREDENTIALS=`aws sts assume-role --role-arn $$ROLE_ARN --serial-number $$MFA_SERIAL_NUMBER  --token-code $$TOKEN_CODE  --role-session-name TempSession --duration-seconds 900 --output=json`

# 	echo "AWS_CA_BUNDLE=../certs/ncl.loc.pem"
# 	echo "AWS_ACCESS_KEY=`echo $$CREDENTIALS | jq -r '.Credentials.AccessKeyId'`" > aws_session_vars.env
# 	echo "AWS_SECRET_ACCESS_KEY=`echo $$CREDENTIALS | jq -r '.Credentials.SecretAccessKey'`" >> aws_session_vars.env
# 	echo "AWS_SESSION_TOKEN=`echo $$CREDENTIALS | jq -r '.Credentials.SessionToken'`" >> aws_session_vars.env

# 	# export all the variables to current CLI terminal
# 	set -o allexport
# 	source aws_session_vars.env
# 	set +o allexport
# 	set +x