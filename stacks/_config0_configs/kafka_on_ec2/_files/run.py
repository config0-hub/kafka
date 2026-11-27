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


def _vm_create(server_type, count, stack):
    """Create VMs for a specific server type in the Kafka cluster."""
    arguments = stack.get_tagged_vars(tag="create", output="dict")

    if stack.get_attr("ami"):
        arguments["ami"] = stack.ami
    elif stack.get_attr("ami_filter") and stack.get_attr("ami_owner"):
        arguments["ami_filter"] = stack.ami_filter
        arguments["ami_owner"] = stack.ami_owner

    hosts = []

    # Create ec2 instances
    for num in range(int(count)):
        hostname = f"{stack.hostname_base}-{server_type}-num-{num}".replace("_", "-")
        hosts.append(hostname)

        arguments["hostname"] = hostname

        human_description = f"Creating hostname {hostname} on ec2"
        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        stack.aws_ec2_server.insert(display=True, **inputargs)

    return hosts


class Main(newSchedStack):

    def __init__(self, stackargs):
        newSchedStack.__init__(self, stackargs)

        # Add default variables
        self.parse.add_required(key="kafka_cluster", types="str", tags="kafka")
        self.parse.add_required(key="num_of_zookeeper", types="int", default=1)
        self.parse.add_required(key="num_of_broker", types="int", default=1)
        self.parse.add_required(key="num_of_schema_registry", types="int", default=1)
        self.parse.add_required(key="num_of_connect", types="int", default=1)
        self.parse.add_required(key="num_of_rest", types="int", default=1)
        self.parse.add_required(key="num_of_ksql", types="int", default=1)
        self.parse.add_required(key="num_of_control_center", types="int", default=1)

        self.parse.add_required(key="ssh_key_name", types="str", tags="create")
        self.parse.add_required(key="instance_profile_name", types="str", tags="create")
        self.parse.add_required(key="managed_tag_key", types="str", tags="create")
        self.parse.add_required(key="managed_tag_value", types="str", tags="create")

        self.parse.add_optional(key="ami", default="null")
        self.parse.add_optional(key="ami_filter",
                                types="str",
                                default='ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*')
        self.parse.add_optional(key="ami_owner",
                                default='099720109477')

        self.parse.add_optional(key="aws_default_region",
                               types="str",
                               tags="create,kafka",
                               default="us-east-1")

        # selects the ssm_ec2_exec_eventbridge install the host orders run
        # through; tagged so it rides into kafka_cluster_on_ubuntu
        self.parse.add_required(key="install_name", types="str", tags="kafka")

        self.parse.add_optional(key="associate_public_ip_address",
                                types="bool",
                                tags="create",
                                default="false")

        self.parse.add_required(key="sg_id", tags="create", default="null")
        self.parse.add_required(key="vpc_id", types="str", default="null")
        self.parse.add_required(key="subnet_ids", tags="create", default="null")
        self.parse.add_optional(key="instance_type", types="str", tags="create", default="t3.micro")
        self.parse.add_optional(key="disksize", types="int", tags="create", default="20")
        self.parse.add_optional(key="publish_to_saas", types="bool", default=True)
        self.parse.add_optional(key="labels", default="null")
        self.parse.add_optional(key="cloud_tags_hash",
                               types="str",
                               tags="create",
                               default='null')

        # Add substack
        self.stack.add_substack("config0-hub:::aws::aws_ec2_server")
        self.stack.add_substack("config0-hub:::mongodb::create_mongodb_pem")
        self.stack.add_substack("config0-hub:::kafka::kafka_cluster_on_ubuntu")

        self.stack.init_substacks()

    def _set_hostname_base(self):
        self.stack.set_variable("hostname_base",
                              f"{self.stack.kafka_cluster}-config")

    def run_ca(self):
        self.stack.init_variables()

        # the _ca suffix keeps this ssl_pem_combined row apart from a MongoDB
        # cluster of the same name; kafka_cluster_on_ubuntu reads <basename>.pem
        return self.stack.create_mongodb_pem.insert(
            display=True,
            arguments={"basename": f"{self.stack.kafka_cluster}_ca"}
        )

    def run_create(self):
        self.stack.init_variables()

        self._set_hostname_base()

        self.stack.set_parallel()

        # zookeeper_hosts
        # broker_hosts
        # schema_registry_hosts
        # connect_hosts
        # rest_hosts
        # ksql_hosts
        # control_center_hosts

        zookeeper_hosts = _vm_create("zookeeper",
                                     self.stack.num_of_zookeeper,
                                     self.stack)

        broker_hosts = _vm_create("broker",
                                  self.stack.num_of_broker,
                                  self.stack)

        schema_registry_hosts = _vm_create("schema_registry",
                                           self.stack.num_of_schema_registry,
                                           self.stack)

        connect_hosts = _vm_create("connect",
                                   self.stack.num_of_connect,
                                   self.stack)

        rest_hosts = _vm_create("rest",
                                self.stack.num_of_rest,
                                self.stack)

        ksql_hosts = _vm_create("ksql",
                                self.stack.num_of_ksql,
                                self.stack)

        control_center_hosts = _vm_create("control_center",
                                          self.stack.num_of_control_center,
                                          self.stack)

        self.stack.unset_parallel()

        arguments = self.stack.get_tagged_vars(tag="kafka", output="dict")
        arguments["zookeeper_hosts"] = zookeeper_hosts
        arguments["broker_hosts"] = broker_hosts
        arguments["schema_registry_hosts"] = schema_registry_hosts
        arguments["connect_hosts"] = connect_hosts
        arguments["rest_hosts"] = rest_hosts
        arguments["ksql_hosts"] = ksql_hosts
        arguments["control_center_hosts"] = control_center_hosts

        if self.stack.get_attr("publish_to_saas"):
            arguments["publish_to_saas"] = True

        human_description = f"Create Kafka Cluster {self.stack.kafka_cluster}"
        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.kafka_cluster_on_ubuntu.insert(display=True, **inputargs)

    def run(self):
        self.add_job("ca")
        self.add_job("create")

        return self.finalize_jobs()

    def schedule(self):
        sched = self.new_schedule()
        sched.job = "ca"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.human_description = "Create and upload Kafka CA"
        sched.on_success = ["create"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "create"
        sched.archive.timeout = 7200
        sched.archive.timewait = 120
        sched.human_description = "Create Kafka Cluster"
        sched.conditions.dependency = ["ca"]
        self.add_schedule()

        return self.get_schedules()
