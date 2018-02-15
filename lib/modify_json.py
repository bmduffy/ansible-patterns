#!/usr/bin/python
# -*- coding: utf-8 -*-
""" modify_json ansible module """

import json

# ignore pylint errors related to the module_utils import
# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import
from ansible.module_utils.basic import *  # noqa: F402,F403


DOCUMENTATION = """
---
module: modify_json
short_description: Modify json key value pairs
author: Brian Duffy
requirements: [ ]
"""

EXAMPLES = """
- modify_json:
    dest: /etc/ansible/facts.d/openshift.fact
    json_key: 'node.label'
    json_value: {'region': 'infra', 'country': 'ie'}
"""


def set_key(json_data, json_key, json_value):
    ''' Updates a parsed json structure setting a key to a value.

        :param json_data: json structure to modify.
        :type json_data: dict
        :param json_key: Key to modify.
        :type json_key: mixed
        :param json_value: Value use for json_key.
        :type json_value: mixed
        :returns: Changes to the json_data structure
        :rtype: dict(tuple())
    '''
    changes = []
    ptr = json_data
    final_key = json_key.split('.')[-1]
    for key in json_key.split('.'):
        # Key isn't present and we're not on the final key. Set to empty dictionary.
        if key not in ptr and key != final_key:
            ptr[key] = {}
            ptr = ptr[key]
        # Current key is the final key. Update value.
        elif key == final_key:
            if (key in ptr and module.safe_eval(ptr[key]) != json_value) or (key not in ptr):  # noqa: F405
                ptr[key] = json_value
                changes.append((json_key, json_value))
        else:
            # Next value is None and we're not on the final key.
            # Turn value into an empty dictionary.
            if ptr[key] is None and key != final_key:
                ptr[key] = {}
            ptr = ptr[key]
    return changes


def main():
    ''' Modify key (supplied in jinja2 dot notation) in json file, setting
        the key to the desired value.
    '''

    # disabling pylint errors for global-variable-undefined and invalid-name
    # for 'global module' usage, since it is required to use ansible_facts
    # pylint: disable=global-variable-undefined, invalid-name,
    # redefined-outer-name
    global module

    module = AnsibleModule(  # noqa: F405
        argument_spec=dict(
            dest=dict(required=True),
            json_key=dict(required=True),
            json_value=dict(required=True),
            backup=dict(required=False, default=True, type='bool'),
        ),
        supports_check_mode=True,
    )

    dest = module.params['dest']
    json_key = module.params['json_key']
    json_value = module.safe_eval(module.params['json_value'])
    backup = module.params['backup']

    # # Represent null values as an empty string.
    # # pylint: disable=missing-docstring, unused-argument
    # def none_representer(dumper, data):
    #     return json.ScalarNode(tag=u'tag:json.org,2002:null', value=u'')
    #
    # json.add_representer(type(None), none_representer)

    try:
        with open(dest) as json_file:
            json_data = json.load(json_file)

        changes = set_key(json_data, json_key, json_value)

        if len(changes) > 0:
            if backup:
                module.backup_local(dest)
            with open(dest, 'w') as json_file:
                json.dump(json_data, json_file)

        return module.exit_json(changed=(len(changes) > 0), changes=changes)

    # ignore broad-except error to avoid stack trace to ansible user
    # pylint: disable=broad-except
    except Exception as error:
        return module.fail_json(msg=str(error))


if __name__ == '__main__':
    main()
