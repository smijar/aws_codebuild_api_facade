#!/usr/bin/env python3
from appcli.app_cli_impl import CLISupport
import logging
import fire
import json
import uuid


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    cli = CLISupport(logging)

    fire.Fire({
        # query cluster commands
        'list_build_projects': cli.list_build_projects,
        'list_deploy_projects': cli.list_deploy_projects,
        'list_build_ids': cli.list_build_ids,
        'list_build_ids_for_project': cli.list_build_ids_for_project,
        'list_current_builds_details': cli.list_current_builds_details,
        'current_build_id_for_project': cli.get_current_build_id_for_project,
        'build_id_details': cli.get_build_id_details,
        'start_build_for_project': cli.start_build_for_project,
        'retry_build': cli.retry_build,
        "logs_for_build": cli.get_logs_for_build,
    })
