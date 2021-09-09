# project/app/main.py
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

import uvicorn
import logging
import boto3
import traceback
import json


from app.custom_logging import CustomizeLogger
from pathlib import Path

from app.codebuild import CodeBuildSupport
from app.config import get_settings, Settings


#-----
# logger config and app creation lifecycle is here
logger = logging.getLogger(__name__)
logger_config_path = Path(__file__).with_name("logging_config.json")

# old way
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# app = FastAPI()

# new way to override default uvicorn logging
def create_app() -> FastAPI:
    app = FastAPI(title='CustomLogger', debug=False)
    logger = CustomizeLogger.make_logger(logger_config_path)
    app.logger = logger
    app.codebuild = CodeBuildSupport(logger)

    return app

app = create_app()

class ApiException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

    def __init__(self, nested_exception: Exception):
        self.nested_exception = nested_exception


@app.exception_handler(ApiException)
async def unicorn_exception_handler(request: Request, exc: ApiException):
    if(exc.nested_exception):
        return JSONResponse(
            status_code=418,
            content={"message": f"Error! {repr(exc.nested_exception)}"},
        )
    else:
        return JSONResponse(
            status_code=418,
            content={"message": f"Error! {exc.name} occurred with message: {exc.message}"},
        )


# Create an SNS client
# sns_client = boto3.client(
#     "sns",
#     region_name="us-east-2"
# )

# s3_client = boto3.client(
#     "s3",
#     region_name="us-east-2"
# )


#------
@app.get('/custom-logger')
def customize_logger(request: Request):
    request.app.logger.info("Here Is Your Info Log")
    a = 1 / 0
    request.app.logger.error("Here Is Your Error Log")
    return {'data': "Successfully Implemented Custom Log"}



# routes start here
@app.get("/ping")
def pong(request:Request, settings: Settings = Depends(get_settings)):
    request.app.logger.info("received a ping message")
    return {
        "ping": "pong!!!",
        "environment": settings.environment,
        "testing": settings.testing
    }


@app.get('/api/projects/listbuildprojects')
def list_build_projects(request:Request, settings: Settings = Depends(get_settings)):
    """
    lists the build projects
    """
    try:
        request.app.logger.info('retrieving the list of build projects')
        projects_list = request.app.codebuild.list_build_projects()
        request.app.logger.info(f'build projects:{projects_list}')
        return projects_list
    except Exception as e:
       request.app.logger.error(f'Error {e} while listing build projects')
       traceback.print_exc()
       raise ApiException(e)


@app.get('/api/projects/listdeployprojects')
def list_deploy_projects(request:Request, settings: Settings = Depends(get_settings)):
    """
    lists the build projects
    """
    try:
        request.app.logger.info('retrieving the list of deploy projects')
        projects_list = request.app.codebuild.list_deploy_projects()
        request.app.logger.info(f'deploy projects:{projects_list}')
        return projects_list
    except Exception as e:
        request.app.logger.error(f'Error {e} while listing deploy projects')
        traceback.print_exc()
        raise ApiException(e)


@app.get('/api/projects/listbuildids')
def list_build_ids(request:Request, settings: Settings = Depends(get_settings)):
    """
    lists the build projects
    """
    try:
        request.app.logger.info('retrieving the list of build ids')
        ids_list = request.app.codebuild.list_build_ids()
        request.app.logger.info(f'build ids list:{ids_list}')

        return ids_list
    except Exception as e:
        request.app.logger.error(f'Error {e} while listing listing build ids')
        traceback.print_exc()
        raise ApiException(e)


@app.get('/api/projects/listbuildids/{project_name}')
def list_build_ids_for_project(project_name: str, request:Request, settings: Settings = Depends(get_settings)):
    """
    lists the build projects
    """
    try:
        request.app.logger.info('retrieving the list of build ids')
        ids_list = request.app.codebuild.list_build_ids_for_project(project_name = project_name)
        request.app.logger.info(f'build ids list:{ids_list}')
        return ids_list
    except Exception as e:
        request.app.logger.error(f'Error {e} while listing listing build ids for project:{project_name}')
        traceback.print_exc()
        raise ApiException(e)



@app.get('/api/projects/currentbuildid/{project_name}')
def get_current_build_id_for_project(project_name: str, request:Request, settings: Settings = Depends(get_settings)):
    """
    lists the build projects
    """
    try:
        request.app.logger.info(f'retrieving the current build id for project: {project_name}')
        current_build_id = request.app.codebuild.get_current_build_id_for_project(project_name = project_name)
        request.app.logger.info(f'current build id:{current_build_id} for project: {project_name}')
        return current_build_id
    except Exception as e:
        request.app.logger.error(f'Error {e} while listing getting current build id for project:{project_name}')
        traceback.print_exc()
        raise ApiException(e)


def build_id_details_to_summary(build_details_dict):
    """
    converts build details from codebuild to a build summary
    """
    phases = []
    build_phases = build_details_dict['phases']
    # request.app.logger.info(json.dumps(build_phases, indent=3, default=str))
    for build_phase in build_phases:
        # request.app.logger.info(json.dumps(build_phase, indent=3, default=str))

        if('phaseStatus' in build_phase and build_phase['phaseStatus'] == 'FAILED'):
            status_code = build_phase['contexts'][0]['statusCode']
            status_message = build_phase['contexts'][0]['message']

            phase = {
                'phase': build_phase['phaseType'],
                'status': build_phase['phaseStatus'],
                'status_code': status_code,
                'status_message': status_message,
                'durationInSeconds': build_phase['durationInSeconds']
            }
        else:
            if('phaseStatus' in build_phase):
                status = build_phase['phaseStatus']
            else:
                status = None
            
            if('durationInSeconds' in build_phase):
                durationInSeconds = build_phase['durationInSeconds']
            else:
                durationInSeconds = None

            phase = {
                'phase': build_phase['phaseType'],
                'phase_status': status,
                'durationInSeconds': durationInSeconds
            }

        phases.append(phase)

    branch = (build_details_dict['environment']['environmentVariables'][0]['value']) if len(build_details_dict['environment']['environmentVariables']) >= 1 else 'None'
    image_version = (build_details_dict['environment']['environmentVariables'][1]['value']) if len(build_details_dict['environment']['environmentVariables']) >= 2 else 'None'
    # parse and return phase details and error message if any
    build_summary = {
        'project_name': build_details_dict['projectName'],
        'start_time': build_details_dict['startTime'],
        'end_time': build_details_dict['endTime'],
        'build_id': build_details_dict['id'],
        'status': build_details_dict['buildStatus'],
        'build_number': build_details_dict['buildNumber'],
        'branch': branch,
        'image_version': image_version,
        # 'branch': build_details_dict['sourceVersion'],
        # 'ref': build_details_dict['resolvedSourceVersion'],
        'phases': phases
    }

    return build_summary

@app.get("/api/projects/buildiddetails/{build_id}")
def get_build_id_details(build_id: str, request:Request, settings: Settings = Depends(get_settings)):
    """
    gets the build id details
    """
    try:
        request.app.logger.info(f'getting build details for build id: {build_id}')
        build_details_dict = request.app.codebuild.get_build_details(build_id)
        build_summary = build_id_details_to_summary(build_details_dict)
        return build_summary
    except Exception as e:
        request.app.logger.error(f'Error {e} while listing getting build details for build id:{build_id}')
        traceback.print_exc()
        raise ApiException(e)



@app.get("/api/projects/listcurrentbuildsdetails")
def list_current_builds_details(request: Request, settings: Settings = Depends(get_settings)):
    """
    lists the current builds - NOT WORKING YET
    """
    try:
        request.app.logger.info(f'getting current builds')
        current_builds_details_list = request.app.codebuild.list_current_builds_details()
        build_summaries = []
        for build_details_dict in current_builds_details_list:
            build_summaries.append(build_id_details_to_summary(build_details_dict))

        request.app.logger.info(f'current builds are:{current_builds_details_list}')
        return build_summaries
    except Exception as e:
        request.app.logger.error(f'Error {e} while listing current builds')
        traceback.print_exc()
        raise ApiException(e)


@app.get('/api/projects/logsforbuild/{project_name}/{build_id}')
def get_logs_for_build(project_name:str, build_id:str, request:Request, settings: Settings = Depends(get_settings)):
    """
    gets logs for project name and build id specified
    """
    try:
        build_id = build_id[build_id.index(':')+1:]
        logs = []
        build_logs_dict = request.app.codebuild.get_logs_for_build(log_group_name=f'/aws/codebuild/{project_name}', log_stream_name=build_id)
        build_logs_events = build_logs_dict['events']
        for event in build_logs_events:
            logs.append(event['message'])
        return logs
    except Exception as e:
        request.app.logger.error(f'Error {e} while getting logs for build_id:{build_id} and project:{project_name}')
        traceback.print_exc()
        raise ApiException(e)


@app.get('/api/projects/startbuild/{project_name}/{branch}/{image_version}')
def start_build_for_project(project_name:str, branch:str, image_version:str, request:Request, settings: Settings = Depends(get_settings)):
    """
    starts the build given the project, branch, image version
    """
    try:
        build_id = request.app.codebuild.start_build_for_project(project_name=project_name, branch=branch, image_version=image_version)
        return build_id
    except Exception as e:
        request.app.logger.error(f'Error {e} while starting build for project_name:{project_name}, {branch}, {image_version}')
        traceback.print_exc()
        raise ApiException(e)


@app.get('/api/projects/retrybuild/{build_id}')
def retry_build(build_id:str, request:Request, settings: Settings = Depends(get_settings)):
    """
    retries the build given the project, branch, image version
    """
    try:
        build_id = request.app.codebuild.retry_build(build_id=build_id)
        return build_id
    except Exception as e:
        request.app.logger.error(f'Error {e} while starting build for build_id:{build_id}')
        traceback.print_exc()
        raise ApiException(e)


if __name__ == '__main__':
      uvicorn.run(app, port=8000)
