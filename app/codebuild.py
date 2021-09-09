import boto3
import logging
import fire
import json
import uuid
from datetime import datetime


class CodeBuildSupport:
    def __init__(self, logger):
        self.var = 'hello'
        self.client = boto3.client('codebuild')
        self.logs_client = boto3.client('logs')
        self.logger = logger
        self.idempo_tokens = {}


    def project_name_from_build_id(build_id):
        """
        returns project name from build_id because its a prefix in form - project_name:project_uuid
        """
        project_name = build_id[:build_id.index(':')]
        return project_name


    def list_build_projects(self):
        """
        lists build projects
        """
        self.logger.info(f'query for codebuild projects')
        projects_dict = self.client.list_projects()

        # print(json.dumps(projects_dict, indent=3))
        projects_list = projects_dict['projects']

        self.logger.info(f'found {len(projects_list)} codebuild projects')

        # if projects_dict['nextToken']:
        #     next_token = projects_dict['nextToken']

        build_projects_list = []

        for project in projects_list:
            if(project.endswith('-build')):
                build_projects_list.append(project)

        self.logger.info(f'successfully found {len(build_projects_list)} -build projects')
        # print(build_projects_list)

        return build_projects_list


    def list_deploy_projects(self):
        """
        lists build projects
        """
        self.logger.info(f'querying for deploy projects')
        projects_dict = self.client.list_projects()

        # print(json.dumps(projects_dict, indent=3))
        projects_list = projects_dict['projects']
        self.logger.info(f'found {len(projects_list)} codebuild projects')

        # next_token = projects_dict['nextToken']
        deploy_projects_list = []

        for project in projects_list:
            if(project.endswith('-deploy')):
                deploy_projects_list.append(project)

        self.logger.info(f'successfully found {len(deploy_projects_list)} -deploy projects')

        # print(build_projects_list)
        return deploy_projects_list


    def list_build_ids(self, next_token = None):
        """
        lists the builds for all projects
        """
        self.logger.info(f'query for build ids')
        if(not next_token):
            response_dict = self.client.list_builds()
        else:
            response_dict = self.client.list_builds(nextToken = next_token)

        ids_list = response_dict['ids']
        self.logger.info(f'successfully found {len(ids_list)} ids list')
        # next_token = response_dict['nextToken']

        return ids_list


    def list_build_ids_for_project(self, project_name):
        """
        lists builds for project
        """
        self.logger.info(f'listing builds for project')
        builds_dict = self.client.list_builds_for_project(projectName=project_name)

        # print(json.dumps(builds_dict, indent=3))
        ids_list = builds_dict['ids']
        self.logger.info(f'successfully found {len(ids_list)} ids list for project')

        # print(json.dumps(builds_dict, indent=3))
        return ids_list


    def get_current_build_id_for_project(self, project_name):
        """
        get last build for named project
        """
        self.logger.info(f'query for listing build ids')

        builds_dict = self.client.list_builds_for_project(projectName=project_name)
        # print(json.dumps(builds_dict, indent=3))
        builds_list = builds_dict['ids']
        if(len(builds_list) == 0):
            raise Exception(f"Error: get_last_build_for_project() - no projects were found for project:{project_name}")

        last_build_id = builds_list[0]

        self.logger.info(f'successfully found current build:{last_build_id} for project')
        return { "build_id": last_build_id }


    def get_build_details(self, build_id):
        """
        get build details including status for named project using its build_id
        """
        self.logger.info(f'query for getting build details for project')

        build_details = self.client.batch_get_builds(ids=[build_id])

        # date-time field JSON serialization error with default json.dumps(), hence have to add below
        build_dict = build_details['builds'][0]

        self.logger.info(f'successfully found build details for build id:{build_id}')
        # print( json.dumps(build_dict, indent=3, sort_keys=False, default=str) )

        return build_dict


    def list_current_builds_details(self):
        """
        lists the details of the current builds
        """
        self.logger.info(f'getting build details for last 20 current builds')

        build_ids_list = self.list_build_ids()

        if(len(build_ids_list) > 30):
            build_ids_list = build_ids_list[:30]

        build_details_dict = self.client.batch_get_builds(ids = build_ids_list)

        build_details_list = []

        if( build_details_dict != None and ('builds' in build_details_dict.keys()) ):
            build_details_list = build_details_dict['builds']

        # date time string gives error so have to add the last value for json.dumps()
        # print( json.dumps(build_dict, indent=3, sort_keys=False, default=str) )
        self.logger.info(f'successfully found {len(build_details_list)} build details for last 20 current builds')

        return build_details_list


    def get_logs_for_build(self, log_group_name, log_stream_name):
        """
        gets the build logs
        """
        log_stream_name = log_stream_name.replace(f'{log_group_name.strip()}:', "")
        self.logger.info(f'getting logs for group:{log_group_name} and stream:{log_stream_name}')

        build_logs = self.logs_client.get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name, startFromHead=True)

        self.logger.info(f'successfully retrieved log lines:{len(build_logs)} for group:{log_group_name} and stream:{log_stream_name}')
        return build_logs


    def can_run_throttled_build(self, project_name):
        """
        check to see if a build was launched for the project less than 2 minutes ago, and throttle
        """
        if(not (project_name in self.idempo_tokens.keys())):
            return True
        else:
            dt_before = self.idempo_tokens[project_name]
            run_before_seconds = (datetime.now() - dt_before).total_seconds()

            if(run_before_seconds > 120):
                return True
            else:
                return False


    def start_build_for_project(self, project_name, branch='develop', image_version='1.0'):
        """
        start NEW build for project - returns id string
        """
        if(not project_name):
            raise Exception("Error: start_build_for_project() - please specify a value for the project name")

        if(not branch):
            raise Exception("Error: start_build_for_project() - please specify a value for the branch")

        if(not image_version):
            raise Exception("Error: start_build_for_project() - please specify a value for the image_version")

        environmentVariablesOverride = [
            {
                'name': 'BRANCH',
                'value': branch,
                'type': 'PLAINTEXT'
            },
            {
                'name': 'IMAGE_VERSION',
                'value': str(image_version),
                'type': 'PLAINTEXT'
            }
        ]

        self.logger.info(f'checking if build can be started for {project_name} and branch:{branch} and image version:{image_version}')

        if(self.can_run_throttled_build(project_name)):
            response_dict = self.client.start_build(projectName = project_name, \
                                        environmentVariablesOverride = environmentVariablesOverride)

            build_id = response_dict['build']['id']
            self.idempo_tokens.update({project_name: datetime.now()})
        else:
            self.logger.info(f'Error: cannot run build for {project_name} as build was run less than two minutes ago')
            raise Exception(f"Error: the last build for {project_name} was run less than 120 seconds ago")

        self.logger.info(f'successfully started build:{build_id} started for {project_name} and branch:{branch} and image version:{image_version}')

        return {"build_id": build_id}



    def retry_build(self, build_id, idempotency_token = None):
        """
        retries the build id
        A unique, case sensitive identifier you provide to ensure the idempotency of the RetryBuild request. 
        The token is included in the RetryBuild request and is valid for five minutes. 
        If you repeat the RetryBuild request with the same token, but change a parameter, 
        AWS CodeBuild returns a parameter mismatch error.
        """
        if(not idempotency_token):
            idempotency_token = str(uuid.uuid4())

        project_name = build_id[:build_id.index(':')]
        self.logger.info(f'running retry build for {project_name} and {build_id}')

        # note - below call checks if a build for the project is already running and throws an error run if so
        response_dict = self.client.retry_build(id = build_id, idempotencyToken = idempotency_token)
        build_id = response_dict['build']['id']

        self.logger.info(f'build started for {project_name} with build_id:{build_id}')

        return build_id, idempotency_token