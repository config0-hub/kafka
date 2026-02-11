"""
# Copyright (C) 2025 Gary Leong <gary@config0.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

def _get_ssh_key(stack):
    _lookup = {
        "must_exists": True,
        "resource_type": "ssh_key_pair",
        "name": stack.ssh_key_name,
        "serialize": True,
        "serialize_fields": ["private_key"]
    }
    return stack.get_resource(decrypt=True, **_lookup)["private_key"]

def _get_private_ips_frm_hosts(hosts, stack):
    _lookup = {
        "must_exists": True,
        "must_be_one": True,
        "resource_type": "server"
    }
    private_ips = []

    for host in stack.to_list(hosts):
        _lookup["hostname"] = host
        _host_info = list(stack.get_resource(**_lookup))[0]

        if _host_info["private_ip"] not in private_ips:
            private_ips.append(_host_info["private_ip"])

    return private_ips

def run(stackargs):
    import json

    # instantiate authoring stack
    stack = newStack(stackargs)

    # add default variables
    stack.parse.add_required(key="bastion_hostname")
    stack.parse.add_required(key="kafka_cluster")
    stack.parse.add_required(key="ssh_key_name")
    stack.parse.add_required(key="aws_default_region")

    stack.parse.add_required(key="zookeeper_hosts")
    stack.parse.add_required(key="broker_hosts")
    stack.parse.add_required(key="schema_registry_hosts")
    stack.parse.add_required(key="connect_hosts")
    stack.parse.add_required(key="rest_hosts")
    stack.parse.add_required(key="ksql_hosts")
    stack.parse.add_required(key="control_center_hosts")

    stack.parse.add_optional(key="vm_username", default="ubuntu")
    stack.parse.add_optional(key="publish_to_saas", default="null")
    stack.parse.add_optional(key="tf_runtime", default="tofu:1.9.1")
    stack.parse.add_optional(key="ansible_docker_image", default="config0/ansible-run-env")

    # add host group
    stack.add_hostgroups("config0-publish:::ubuntu::docker", "install_docker")
    stack.add_hostgroups("config0-publish:::ansible::ubuntu", "install_python")
    stack.add_hostgroups("config0-publish:::kafka::ubuntu_vendor_setup", "ubuntu_vendor_setup")
    stack.add_hostgroups("config0-publish:::kafka::ubuntu_vendor_init_cluster", "ubuntu_vendor_init_cluster")

    # Initialize 
    stack.init_variables()
    stack.init_hostgroups()

    # install docker on bastion hosts
    human_description = f"Install Docker on bastion {stack.bastion_hostname}"
    inputargs = {
        "display": True,
        "human_description": human_description,
        "automation_phase": "infrastructure",
        "hostname": stack.bastion_hostname,
        "groups": stack.install_docker
    }
    stack.add_groups_to_host(**inputargs)

    # get ssh_key
    private_key = _get_ssh_key(stack)

    # get ips
    host_ips = []

    kafka_zookeeper_ips = _get_private_ips_frm_hosts(stack.zookeeper_hosts, stack)
    host_ips.extend(kafka_zookeeper_ips)

    kafka_broker_ips = _get_private_ips_frm_hosts(stack.broker_hosts, stack)
    host_ips.extend(kafka_broker_ips)

    kafka_schema_registry_ips = _get_private_ips_frm_hosts(stack.schema_registry_hosts, stack)
    host_ips.extend(kafka_schema_registry_ips)

    kafka_connect_ips = _get_private_ips_frm_hosts(stack.connect_hosts, stack)
    host_ips.extend(kafka_connect_ips)

    kafka_rest_ips = _get_private_ips_frm_hosts(stack.rest_hosts, stack)
    host_ips.extend(kafka_rest_ips)

    kafka_ksql_ips = _get_private_ips_frm_hosts(stack.ksql_hosts, stack)
    host_ips.extend(kafka_ksql_ips)

    kafka_control_center_ips = _get_private_ips_frm_hosts(stack.control_center_hosts, stack)
    host_ips.extend(kafka_control_center_ips)

    # install python on hosts for ansible
    human_description = "Install Python for Ansible"
    env_vars = {
        "METHOD": "create",
        "STATEFUL_ID": stack.random_id(size=10),
        "ANS_VAR_private_key": private_key,
        "ANS_VAR_exec_ymls": "entry_point/10-install-python.yml",
        "ANS_VAR_host_ips": ",".join(host_ips)
    }

    inputargs = {
        "display": True,
        "human_description": human_description,
        "env_vars": json.dumps(env_vars),
        "stateful_id": env_vars["STATEFUL_ID"],
        "automation_phase": "infrastructure",
        "hostname": stack.bastion_hostname,
        "groups": stack.install_python
    }
    stack.add_groups_to_host(**inputargs)

    ###############################################################
    # Main Ansible configs
    ###############################################################
    # base env variables
    stateful_id = stack.random_id(size=10)

    human_description = "Setting up Ansible"

    base_env_vars = {
        "METHOD": "create",
        "DOCKER_IMAGE": stack.ansible_docker_image,
        "STATEFUL_ID": stateful_id,
        "ANS_VAR_private_key": private_key,
        "ANS_VAR_kafka_zookeeper": ",".join(kafka_zookeeper_ips),
        "ANS_VAR_kafka_broker": ",".join(kafka_broker_ips),
        "ANS_VAR_kafka_schema_registry": ",".join(kafka_schema_registry_ips),
        "ANS_VAR_kafka_connect": ",".join(kafka_connect_ips),
        "ANS_VAR_kafka_rest": ",".join(kafka_rest_ips),
        "ANS_VAR_kafka_ksql": ",".join(kafka_ksql_ips),
        "ANS_VAR_kafka_control_center": ",".join(kafka_control_center_ips)
    }

    # deploy Ansible files
    inputargs = {
        "display": True,
        "human_description": human_description,
        "env_vars": json.dumps(base_env_vars.copy()),
        "stateful_id": stateful_id,
        "automation_phase": "infrastructure",
        "hostname": stack.bastion_hostname,
        "groups": stack.ubuntu_vendor_setup
    }
    stack.add_groups_to_host(**inputargs)

    ##############################################################
    # install kafka
    ##############################################################
    human_description = "Install Kafka"

    env_vars = base_env_vars.copy()
    env_vars["ANS_VAR_exec_ymls"] = ",".join([
        "entry_point/20-prereq.yml",
        "entry_point/30-zookeeper.yml",
        "entry_point/40-broker.yml",
        "entry_point/50-schema.yml",
        "entry_point/60-connect.yml",
        "entry_point/70-ksql.yml",
        "entry_point/80-rest.yml",
        "entry_point/90-control.yml"
    ])

    docker_env_fields_keys = env_vars.keys()
    env_vars["DOCKER_ENV_FIELDS"] = ",".join(docker_env_fields_keys)

    inputargs = {
        "display": True,
        "human_description": human_description,
        "env_vars": json.dumps(env_vars),
        "stateful_id": stateful_id,
        "automation_phase": "infrastructure",
        "hostname": stack.bastion_hostname,
        "groups": stack.ubuntu_vendor_init_cluster
    }
    stack.add_groups_to_host(**inputargs)

    ###############################################################
    # publish variables
    ###############################################################
    if stack.publish_to_saas:
        _publish_vars = {
            "kafka_cluster": stack.kafka_cluster,
            "kafka_zookeeper": kafka_zookeeper_ips,
            "kafka_broker": kafka_broker_ips,
            "kafka_schema_registry": kafka_schema_registry_ips,
            "kafka_connect": kafka_connect_ips,
            "kafka_rest": kafka_rest_ips,
            "kafka_ksql": kafka_ksql_ips,
            "kafka_control_center": kafka_control_center_ips
        }
        stack.output_to_ui(_publish_vars)

    return stack.get_results()
