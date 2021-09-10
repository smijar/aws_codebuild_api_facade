# aws_codebuild_api_facade
An simplified API facade for invoking AWS Codebuild in an easier to use manner.

This project includes:
- REST API endpoints for AWS Codebuild with swagger docs automatically generated
- built using FastAPI for Python
- CLI to run the API using Python

Intention was to not have to create IAM AWS accounts for developers to run build jobs and to be able to easily start, stop, query status of build jobs over a secure VPN without everyone needing AWS Access keys.

This interface also includes enough functionality to build a custom UI for AWS Codebuild if needed on top of the API.
