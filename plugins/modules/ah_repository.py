#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2020, Sean Sullivan <@sean-m-sullivan>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {"metadata_version": "1.1", "status": ["preview"], "supported_by": "community"}


DOCUMENTATION = """
---
module: ah_repository
author: "Tom Page (@Tompage1994)"
short_description: Configure a repository.
description:
    - Configure an Automation Hub remote Repository. See
      U(https://www.ansible.com/) for an overview.
options:
    name:
      description:
        - Repository name. Probably one of community ot rh-certified.
      required: True
      type: str
    url:
      description:
        - Remote URL for the repository.
      required: True
      type: str
    auth_url:
      description:
        - Remote URL for the repository authentication if seperate.
      type: str
    token:
      description:
        - Token to authenticate to the remote repository.
      type: str
    username:
      description:
        - Username to authenticate to the remote repository.
      type: str
    password:
      description:
        - Password to authenticate to the remote repository.
      type: str
    requirements:
      description:
        - Requirements to download from remote.
      type: list
    requirements_file:
      description:
        - A yaml requirements file to download from remote.
      type: str
    proxy_url:
      description:
        - Proxy URL to use for the connection
      type: str
    proxy_username:
      description:
        - Proxy URL to use for the connection
      type: str
    proxy_password:
      description:
        - Proxy URL to use for the connection
      type: str
    download_concurrency:
      description:
        - Number of concurrent collections to download.
      type: str
      default: 10

extends_documentation_fragment: redhat_cop.ah_configuration.auth
"""


EXAMPLES = """
- name: Configure rh-certified repo
  ah_repository:
    name: rh-certified
    url: https://cloud.redhat.com/api/automation-hub/
    token: aabbcc
    auth_url: https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token

- name: Configure community repo
  ah_repository:
    name: community
    url: https://galaxy.ansible.com/api/
    requirements:
      - redhat_cop.ah_configuration
      - redhat_cop.tower_configuration

- name: Configure community repo from a file
  ah_repository:
    name: community
    url: https://galaxy.ansible.com/api/
    requirements_file: "/tmp/requirements.yml"
"""

from ..module_utils.ah_module import AHModule


def main():
    # Any additional arguments that are not fields of the item can be added here
    argument_spec = dict(
        name=dict(required=True),
        url=dict(required=True),
        auth_url=dict(),
        token=dict(),
        username=dict(),
        password=dict(no_log=True),
        requirements=dict(type="list", elements="str"),
        requirements_file=dict(),
        proxy_url=dict(),
        proxy_username=dict(),
        proxy_password=dict(no_log=True),
        download_concurrency=dict(default="10"),
    )

    mutually_exclusive = [("requirements", "requirements_file")]

    # Create a module for ourselves
    module = AHModule(argument_spec=argument_spec, mutually_exclusive=mutually_exclusive)

    # Extract our parameters
    name = module.params.get("name")
    new_fields = {}

    requirements = module.params.get("requirements")
    if requirements:
        requirements_content = "\n  - ".join(requirements)
        new_fields["requirements_file"] = "---\ncollections:\n  - " + requirements_content

    requirements_file = module.params.get("requirements_file")
    if requirements_file:
        new_fields["requirements_file"] = module.getFileContent(requirements_file)

    for field_name in (
        "url",
        "auth_url",
        "token",
        "username",
        "password",
        "proxy_url",
        "proxy_username",
        "proxy_password",
        "download_concurrency",
    ):
        field_val = module.params.get(field_name)
        if field_val is not None:
            new_fields[field_name] = field_val

    # If the state was present and we can let the module build or update the existing item, this will return on its own
    endpoint = "api/galaxy/content/{0}/v3/sync/config".format(name)
    existing_item = module.get_only(endpoint, name_or_id=name, key="req_url")
    module.create_or_update_if_needed(existing_item, new_fields, endpoint, "repository config", require_id=False, fixed_url=endpoint)


if __name__ == "__main__":
    main()
