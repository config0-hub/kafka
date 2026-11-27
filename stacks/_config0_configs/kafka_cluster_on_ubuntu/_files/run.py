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

# The seven kinds in the original start order
# (.original kafka_cluster_on_ubuntu run.py:178-187): the kind, the playbook
# its nodes run after 20-prereq.yml, and the id variable its role reads
# (index plus 1 in list order), or None.
KAFKA_TIERS = (
    ("zookeeper", "entry_point/30-zookeeper.yml", "zookeeper_id"),
    ("broker", "entry_point/40-broker.yml", "broker_id"),
    ("schema_registry", "entry_point/50-schema.yml", None),
    ("connect", "entry_point/60-connect.yml", None),
    ("ksql", "entry_point/70-ksql.yml", None),
    ("rest", "entry_point/80-rest.yml", "kafka_rest_id"),
    ("control_center", "entry_point/90-control.yml", None),
)


# The CA the ca job of kafka_on_ec2 records through create_mongodb_pem.
def _get_kafka_ca_pem(stack):
    lookup = {
        "must_exists": True,
        "resource_type": "ssl_pem_combined",
        "provider": "openssl",
        "name": f"{stack.kafka_cluster}_ca.pem",
        "serialize_fields": ["contents"]
    }
    return stack.get_resource(**lookup)["contents"]


# Hostname and private IP of each host, in list order. The role ids index
# this same list, so no entry is dropped.
def _get_kafka_hosts(stack, hosts):
    kafka_hosts = []

    lookup = {
        "must_exists": True,
        "must_be_one": True,
        "resource_type": "server"
    }

    for hostname in stack.to_list(hosts):
        lookup["hostname"] = hostname
        host_info = list(stack.get_resource(**lookup))[0]
        kafka_hosts.append((hostname, host_info["private_ip"]))

    return kafka_hosts


def _kafka_env_vars(stack, kafka_ips):
    env_vars = {
        "METHOD": "create",
        "ANS_VAR_kafka_ca_pem": "secret:::kafka_ca_pem"
    }
    for kind, ips in kafka_ips.items():
        env_vars[f"ANS_VAR_kafka_{kind}_ips"] = stack.serialize(ips, b64=False)
    return env_vars


def run(stackargs):
    import json

    stack = newStack(stackargs)

    stack.parse.add_required(key="kafka_cluster")
    stack.parse.add_required(key="aws_default_region")
    # selects the ssm_ec2_exec_eventbridge install the host orders run through
    stack.parse.add_required(key="install_name")

    stack.parse.add_required(key="zookeeper_hosts")
    stack.parse.add_required(key="broker_hosts")
    stack.parse.add_required(key="schema_registry_hosts")
    stack.parse.add_required(key="connect_hosts")
    stack.parse.add_required(key="rest_hosts")
    stack.parse.add_required(key="ksql_hosts")
    stack.parse.add_required(key="control_center_hosts")

    stack.parse.add_optional(key="publish_to_saas", default="null")

    stack.add_hostgroups(
        "config0-hub:::kafka::ubuntu_vendor_setup",
        "ubuntu_vendor_setup"
    )
    stack.add_hostgroups(
        "config0-hub:::kafka::ubuntu_vendor_init_cluster",
        "ubuntu_vendor_init_cluster"
    )

    stack.init_variables()
    stack.init_hostgroups()

    kafka_hosts = {
        "zookeeper": _get_kafka_hosts(stack, stack.zookeeper_hosts),
        "broker": _get_kafka_hosts(stack, stack.broker_hosts),
        "schema_registry": _get_kafka_hosts(stack, stack.schema_registry_hosts),
        "connect": _get_kafka_hosts(stack, stack.connect_hosts),
        "rest": _get_kafka_hosts(stack, stack.rest_hosts),
        "ksql": _get_kafka_hosts(stack, stack.ksql_hosts),
        "control_center": _get_kafka_hosts(stack, stack.control_center_hosts)
    }
    kafka_ips = {
        kind: [private_ip for _, private_ip in hosts]
        for kind, hosts in kafka_hosts.items()
    }

    stack.add_secret(name="kafka_ca_pem", value=_get_kafka_ca_pem(stack))

    base_env_vars = _kafka_env_vars(stack, kafka_ips)
    kafka_groups = [
        stack.ubuntu_vendor_setup,
        stack.ubuntu_vendor_init_cluster
    ]

    # One tier per kind, in order. A kind with count 0 emits no window.
    for kind, exec_yml, id_var in KAFKA_TIERS:
        if not kafka_hosts[kind]:
            continue

        stack.set_parallel()

        for index, (hostname, private_ip) in enumerate(kafka_hosts[kind], start=1):
            env_vars = base_env_vars.copy()
            env_vars["ANS_VAR_kafka_host_ip"] = private_ip
            env_vars["ANS_VAR_exec_ymls"] = f"entry_point/20-prereq.yml,{exec_yml}"
            if id_var:
                env_vars[f"ANS_VAR_{id_var}"] = str(index)

            stack.add_groups_to_host(
                display=True,
                human_description=f"Install Kafka {kind} on {hostname}",
                env_vars=json.dumps(env_vars),
                workspace_id=stack.random_id(size=10),
                automation_phase="infrastructure",
                hostname=hostname,
                install_name=stack.install_name,
                groups=kafka_groups
            )

        stack.unset_parallel(wait_all=True)

    if stack.get_attr("publish_to_saas"):
        publish_vars = {
            "kafka_cluster": stack.kafka_cluster,
            "kafka_zookeeper": kafka_ips["zookeeper"],
            "kafka_broker": kafka_ips["broker"],
            "kafka_schema_registry": kafka_ips["schema_registry"],
            "kafka_connect": kafka_ips["connect"],
            "kafka_rest": kafka_ips["rest"],
            "kafka_ksql": kafka_ips["ksql"],
            "kafka_control_center": kafka_ips["control_center"]
        }
        stack.output_to_ui(publish_vars)

    return stack.get_results()
