from genericpath import exists
from inspect import stack
from sys import intern
import requests
import json
import sys
import os
import glob
import fire
from io import StringIO
#from sh import aws
import base64
import logging
import time
import pprint
import urllib.request
import inspect
from prettytable import PrettyTable


class CLISupport:
    def __init__(self, logger):
        self.var = 'hello'
        self.baseurl = 'http://cicdctl:8000/api/projects'
        self.logger = logger


    def client_request(self, function_name, url, headers, payload):
        """
        common function to make request and print json output
        """
        headers = {'Content-Type':'application/json'}
        payload = {}
        # format = 'default' if format == None else 'json'

        # self.logger.info(f'list_build_projects() - format:{format}')
        self.logger.debug(f'{function_name}() - calling {url}')
        r = requests.get(url, headers = headers, data = payload)

        if(r.status_code >= 200 and r.status_code < 299):
            # if(format == 'default'):
            print(json.dumps(r.json(), indent=2, default=str))
        else:
            raise Exception(f"Error! {function_name}() - status code:{r.status_code} and {r.text}")

    def list_build_projects(self, format=None):
        """
        returns list of build projects
        e.g. $ python app_cli.py list_build_projects
        """
        url = f'{self.baseurl}/listbuildprojects'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return

        # format = 'default' if format == None else 'json'

        # self.logger.info(f'list_build_projects() - format:{format}')
        self.logger.info(f'list_build_projects() - calling {url}')
        r = requests.get(url, headers = headers, data = payload)


    def list_deploy_projects(self):
        """
        returns list of deploy projects
        $ python app_cli.py list_deploy_projects
        """
        url = f'{self.baseurl}/listdeployprojects'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return


    def list_build_ids(self):
        """
        lists the build ids
        $ python app_cli.py list_build_ids
        """
        url = f'{self.baseurl}/listbuildids'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return


    def list_build_ids_for_project(self, project_name):
        """
        lists build ids for project
        $ python app_cli.py list_build_ids_for_project --project_name=vyze-identity-provider-build
        """
        url = f'{self.baseurl}/listbuildids/{project_name}'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return


    def get_current_build_id_for_project(self, project_name):
        """
        gets the current build id for project
        $ python app_cli.py current_build_id_for_project  --project_name=vyze-identity-provider-build
        """
        url = f'{self.baseurl}/currentbuildid/{project_name}'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return 


    def get_build_id_details(self, build_id):
        """
        gets build details of build id
        $ python app_cli.py build_id_details  --build_id=vyze-identity-provider-build:f9f13eb8-2d8a-46cd-b6c3-1ace02adc4c9
        """
        url = f'{self.baseurl}/buildiddetails/{build_id}'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return


    def list_current_builds_details(self):
        """
        lists the details of the current builds
        $ python app_cli.py  list_current_builds_details
        """
        url = f'{self.baseurl}/listcurrentbuildsdetails'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return


    def get_logs_for_build(self, project_name, build_id):
        """
        gets the logs in json for the log group name and log_stream_name
        $ python app_cli.py logs_for_build vyze-identity-provider-build vyze-identity-provider-build:f9f13eb8-2d8a-46cd-b6c3-1ace02adc4c9
        """
        url = f'{self.baseurl}/logsforbuild/{project_name}/{build_id}'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return


    def start_build_for_project(self, project_name, branch, image_version):
        """
        starts the build for the project
        $ python app_cli.py start_build_for_project --project_name=vyze-identity-provider-build --branch=develop --image_version=0.0.0
        """
        url = f'{self.baseurl}/startbuild/{project_name}/{branch}/{image_version}'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return


    def retry_build(self, build_id):
        """
        retries the build for the project
        $ python app_cli.py retry_build vyze-identity-provider-build:d39470ec-39b5-48b3-a969-15e273a70aa4
        [
            "vyze-identity-provider-build:71028493-8f53-4348-b06f-c76946d303ca",
            "76e8f5fb-fb7a-4d6b-ae40-447e6a708634"
        ]
        """
        url = f'{self.baseurl}/retrybuild/{build_id}'

        headers = {'Content-Type':'application/json'}
        payload = {}
        myself = lambda: inspect.stack()[1][3]

        self.client_request(myself(), url, headers, payload)
        return
