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


def _vm_create(server_type, num, stack):
    """Create VMs for a specific server type in the Kafka cluster."""
    arguments = stack.get_tagged_vars(tag="create", output="dict")
    arguments["ip_key"] = "private_ip"

    if stack.ami:
        arguments["ami"] = stack.ami
    elif stack.ami_filter and stack.ami_owner:
        arguments["ami_filter"] = stack.ami_filter
        arguments["ami_owner"] = stack.ami_owner

    arguments["size"] = stack.instance_type
    hosts = []

    # Create ec2 instances
    for num in range(int(num)):
        hostname = f"{stack.hostname_base}-{server_type}-num-{num}".replace("_", "-")
        hosts.append(hostname)

        arguments["hostname"] = hostname
        arguments["bootstrap_for_exec"] = None

        human_description = f"Creating hostname {hostname} on ec2"
        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        stack.ec2_ubuntu.insert(display=True, **inputargs)

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
        
        self.parse.add_optional(key="ami", default="null")
        self.parse.add_optional(key="ami_filter",
                                types="str",
                                default='ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*')
        self.parse.add_optional(key="ami_owner",
                                default='099720109477')

        self.parse.add_optional(key="bastion_destroy", default="null")

        # bastion configs
        self.parse.add_required(key="bastion_sg_id", default="null")
        self.parse.add_required(key="bastion_subnet_ids", default="null")
        self.parse.add_optional(key="bastion_ami", default="null")

        self.parse.add_optional(key="bastion_ami_filter",
                                types = "str",
                                default="ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*")

        self.parse.add_optional(key="bastion_ami_owner",
                                default='099720109477')

        self.parse.add_optional(key="aws_default_region", 
                               types="str", 
                               tags="create,bastion,kafka", 
                               default="us-east-1")
        
        self.parse.add_required(key="sg_id", tags="create", default="null")
        self.parse.add_required(key="vpc_id", types="str", tags="create,bastion", default="null")
        self.parse.add_required(key="subnet_ids", tags="create", default="null")
        self.parse.add_optional(key="instance_type", types="str", tags="create", default="t3.micro")
        self.parse.add_optional(key="disksize", types="int", tags="create,bastion", default="20")
        self.parse.add_optional(key="publish_to_saas", default="null")
        self.parse.add_optional(key="labels", default="null")
        self.parse.add_optional(key="cloud_tags_hash", 
                               types="str", 
                               tags="create,bastion", 
                               default='null')

        # Add substack
        self.stack.add_substack("config0-publish:::new_ec2_ssh_key")
        self.stack.add_substack("config0-publish:::ec2_ubuntu")
        self.stack.add_substack("config0-publish:::kafka_cluster_on_ubuntu")
        self.stack.add_substack("config0-publish:::delete_resource")

        self.stack.init_substacks()

    def run_sshkey(self):
        self.stack.init_variables()
        self._set_ssh_key_name()

        arguments = {
            "key_name": self.stack.ssh_key_name,
            "clobber": True,
            "aws_default_region": self.stack.aws_default_region
        }

        human_description = f"Create and upload ssh key name {self.stack.ssh_key_name}"
        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.new_ec2_ssh_key.insert(display=True, **inputargs)

    def _set_bastion_hostname(self):
        self.stack.set_variable("bastion_hostname",
                              f"{self.stack.hostname_base}-config",
                              tags="kafka")

    def _set_hostname_base(self):
        self.stack.set_variable("hostname_base",
                              f"{self.stack.kafka_cluster}-config")

    def _set_ssh_key_name(self):
        self.stack.set_variable("ssh_key_name",
                              f"{self.stack.kafka_cluster}-ssh-key",
                              tags="bastion,create,kafka",
                              types="str")

    def run_bastion(self):
        self.stack.init_variables()

        self._set_hostname_base()
        self._set_bastion_hostname()
        self._set_ssh_key_name()

        arguments = self.stack.get_tagged_vars(tag="bastion", output="dict")
        arguments["size"] = self.stack.instance_type
        arguments["hostname"] = self.stack.bastion_hostname
        arguments["subnet_ids"] = self.stack.bastion_subnet_ids
        arguments["sg_id"] = self.stack.bastion_sg_id
        arguments["bootstrap_for_exec"] = True
        arguments["ip_key"] = "public_ip"

        if self.stack.bastion_ami:
            arguments["ami"] = self.stack.bastion_ami
        elif self.stack.bastion_ami_filter and self.stack.bastion_ami_owner:
            arguments["ami_filter"] = self.stack.bastion_ami_filter
            arguments["ami_owner"] = self.stack.bastion_ami_owner

        try:
            self.stack.logger.json(arguments)
        except:
            self.stack.logger.debug(arguments)

        human_description = f"Creating bastion config hostname {self.stack.bastion_hostname} on ec2"
        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.ec2_ubuntu.insert(display=True, **inputargs)

    def run_create(self):
        self.stack.init_variables()

        self._set_hostname_base()
        self._set_bastion_hostname()
        self._set_ssh_key_name()

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

        if self.stack.publish_to_saas:
            arguments["publish_to_saas"] = True

        human_description = f"Create Kafka Cluster {self.stack.kafka_cluster}"
        inputargs = {
            "arguments": arguments,
            "automation_phase": "infrastructure",
            "human_description": human_description
        }

        return self.stack.kafka_cluster_on_ubuntu.insert(display=True, **inputargs)

    def run_cleanup(self):
        self.stack.init_variables()

        self._set_hostname_base()
        self._set_bastion_hostname()

        arguments = {
            "must_exists": True,
            "hostname": self.stack.bastion_hostname,
            "resource_type": "server"
        }

        if self.stack.bastion_destroy:
            human_description = f"Destroying bastion config hostname {self.stack.bastion_hostname} on ec2"
            inputargs = {
                "arguments": arguments,
                "automation_phase": "infrastructure",
                "human_description": human_description
            }

            return self.stack.delete_resource.insert(display=True, **inputargs)

    def run(self):
        self.stack.unset_parallel(sched_init=True)
        self.add_job("sshkey")
        self.add_job("bastion")
        self.add_job("create")
        self.add_job("cleanup")

        return self.finalize_jobs()

    def schedule(self):
        sched = self.new_schedule()
        sched.job = "sshkey"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.conditions.retries = 1
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create and upload ssh-key"
        sched.on_success = ["bastion"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "bastion"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create Bastion Config"
        sched.on_success = ["create"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "create"
        sched.archive.timeout = 7200
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.automation_phase = "infrastructure"
        sched.human_description = "Create Kafka Cluster"
        sched.conditions.dependency = ["sshkey"]
        sched.on_success = ["cleanup"]
        self.add_schedule()

        sched = self.new_schedule()
        sched.job = "cleanup"
        sched.archive.timeout = 1800
        sched.archive.timewait = 120
        sched.archive.cleanup.instance = "clear"
        sched.failure.keep_resources = True
        sched.automation_phase = "infrastructure"
        sched.human_description = "Destroy Bastion Config"
        self.add_schedule()

        return self.get_schedules()