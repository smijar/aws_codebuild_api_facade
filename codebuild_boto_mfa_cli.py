#!/usr/bin/env python3
from app.codebuild import CodeBuildSupport
import logging
import fire
import json
import uuid

from  app.codebuild import CodeBuildSupport


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    codebuild = CodeBuildSupport()

    fire.Fire({
        # query cluster commands
        'list_build_projects': codebuild.list_build_projects,
        'list_deploy_projects': codebuild.list_deploy_projects,
        'list_builds_ids': codebuild.list_build_ids,
        'list_builds_ids_for_project': codebuild.list_build_ids_for_project,
        'current_build_id_for_project': codebuild.get_current_build_id_for_project,
        'build_details': codebuild.get_build_details,
        'list_current_builds': codebuild.list_current_builds,
        'start_build_for_project': codebuild.start_build_for_project,
        'retry_build': codebuild.retry_build,
        "logs_for_build": codebuild.get_logs_for_build
    })


# python codebuild_cli.py list_build_projects
# python codebuild_cli.py list_deploy_projects
# python codebuild_cli.py list_builds_for_project proxy-identifier-service-build
# python codebuild_cli.py start_build_for_project "proxy-identifier-service-build" "develop" "1.0"
# python codebuild_cli.py retry_build "proxy-identifier-service-build:4f4ed7f2-cecb-41ee-8afc-28afc3317f5f" 4c856053-5151-4bfa-8915-c289459f46c3
# python codebuild_cli.py last_build_for_project proxy-identifier-service-build
# python codebuild_cli.py build_details proxy-identifier-service-build:b1fc82d5-5b97-4bf7-8e85-ae483fbe7c5f
# python codebuild_cli.py logs_for_build  "/aws/codebuild/proxy-identifier-service-build" "b1fc82d5-5b97-4bf7-8e85-ae483fbe7c5f"
