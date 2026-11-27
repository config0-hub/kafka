# Kafka Cluster Deployment

## Description

This worker stack installs a Kafka cluster on its EC2 nodes: ZooKeeper, Kafka brokers, Schema Registry, Kafka Connect, KSQL, the REST Proxy and Control Center, with TLS on. Each kind is installed in that order, all its nodes in parallel. Host execgroups are delivered directly to each node through the SSM EC2 execution engine and run Ansible in localhost mode. Every node receives the IP lists of all seven kinds, its own private IP and, where its role needs one, its id. The cluster's certificate authority is read from the `<kafka_cluster>_ca.pem` record and reaches the nodes through an SSM secret. No SSH key, bastion, remote inventory, or Docker bootstrap is used.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| kafka_cluster | Kafka cluster name | &nbsp; |
| aws_default_region | AWS region containing the hosts | &nbsp; |
| install_name | Name of the `ssm_ec2_exec_eventbridge_install` record the host orders run through | &nbsp; |
| zookeeper_hosts | List of hostnames for ZooKeeper nodes | &nbsp; |
| broker_hosts | List of hostnames for Kafka broker nodes | &nbsp; |
| schema_registry_hosts | List of hostnames for Schema Registry nodes | &nbsp; |
| connect_hosts | List of hostnames for Kafka Connect nodes | &nbsp; |
| rest_hosts | List of hostnames for REST API nodes | &nbsp; |
| ksql_hosts | List of hostnames for KSQL nodes | &nbsp; |
| control_center_hosts | List of hostnames for Control Center nodes | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| publish_to_saas | Publish values to the Config0 SaaS UI | null |

## Dependencies

### Hostgroups

- `config0-hub:::kafka::ubuntu_vendor_setup`
- `config0-hub:::kafka::ubuntu_vendor_init_cluster`

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
</pre>