# Kafka Cluster on AWS EC2

## Description
This stack creates a complete Kafka cluster on AWS EC2 instances, including ZooKeeper, Brokers, Schema Registry, Connect, REST, KSQL, and Control Center components. It also provisions a bastion host for secure cluster access.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| kafka_cluster | Kafka cluster name | &nbsp; |
| bastion_sg_id | Bastion host security group | &nbsp; |
| bastion_subnet_ids | Subnets for bastion hosts | &nbsp; |
| sg_id | Security group ID | &nbsp; |
| vpc_id | VPC network identifier | &nbsp; |
| subnet_ids | Subnet ID list | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| num_of_zookeeper | ZooKeeper node count | 1 |
| num_of_broker | Kafka broker count | 1 |
| num_of_schema_registry | Schema registry node count | 1 |
| num_of_connect | Kafka Connect node count | 1 |
| num_of_rest | Kafka REST proxy count | 1 |
| num_of_ksql | KSQL server count | 1 |
| num_of_control_center | Control Center node count | 1 |
| ami | AMI ID | null |
| ami_filter | AMI filter criteria | null |
| ami_owner | AMI owner ID | null |
| bastion_destroy | Destroy bastion host after automation completes | null |
| bastion_ami | Bastion host AMI ID | null |
| bastion_ami_filter | Bastion AMI filter criteria | null |
| bastion_ami_owner | Bastion AMI owner ID | null |
| aws_default_region | Default AWS region | us-east-1 |
| instance_type | EC2 instance type | t3.micro |
| disksize | Disk size in GB | 20 |
| publish_to_saas | Boolean to publish values to config0 SaaS UI | null |
| labels | Configuration for labels | null |
| cloud_tags_hash | Resource tags for cloud provider | null |

## Dependencies

### Substacks
- [config0-publish:::new_ec2_ssh_key](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/new_ec2_ssh_key)
- [config0-publish:::ec2_ubuntu](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/ec2_ubuntu)
- [config0-publish:::kafka_cluster_on_ubuntu](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/kafka_cluster_on_ubuntu)
- [config0-publish:::delete_resource](https://api-app.config0.com/web_api/v1.0/stacks/config0-publish/delete_resource)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>