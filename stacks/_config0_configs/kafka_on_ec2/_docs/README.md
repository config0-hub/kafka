# Kafka Cluster on AWS EC2

## Description

This stack creates a Kafka cluster on EC2: ZooKeeper, Kafka brokers, Schema Registry, Kafka Connect, the REST Proxy, KSQL and Control Center. Its `ca` job records the cluster's certificate authority as the `<kafka_cluster>_ca.pem` resource. Its `create` job creates the nodes in parallel, then `kafka_cluster_on_ubuntu` configures each node through the SSM EC2 execution engine. It does not create or use an SSH bastion.

The caller supplies the `instance_profile_name`, `managed_tag_key`, and `managed_tag_value` promoted by the `ssm_ec2_exec_eventbridge_install` resource record. The EC2 stack records those values on every server so host orders can target the instance through SSM.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| kafka_cluster | Kafka cluster name | &nbsp; |
| num_of_zookeeper | ZooKeeper node count | 1 |
| num_of_broker | Kafka broker count | 1 |
| num_of_schema_registry | Schema Registry node count | 1 |
| num_of_connect | Kafka Connect node count | 1 |
| num_of_rest | Kafka REST Proxy count | 1 |
| num_of_ksql | KSQL server count | 1 |
| num_of_control_center | Control Center node count | 1 |
| ssh_key_name | Existing EC2 key pair. This stack requires it and gives it to every node; `aws_ec2_server` declares it optional. Not used for configuration transport | &nbsp; |
| instance_profile_name | Instance profile promoted by the SSM engine install record | &nbsp; |
| managed_tag_key | Managed tag key promoted by the SSM engine install record | &nbsp; |
| managed_tag_value | Managed tag value promoted by the SSM engine install record | &nbsp; |
| install_name | Name of the `ssm_ec2_exec_eventbridge_install` record the host orders run through | &nbsp; |
| sg_id | Security group ID | null |
| vpc_id | VPC network identifier | null |
| subnet_ids | Subnet ID list | null |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| ami | AMI ID | null |
| ami_filter | Ubuntu Noble AMI filter | ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-* |
| ami_owner | Canonical Ubuntu AMI owner | 099720109477 |
| aws_default_region | Default AWS region | us-east-1 |
| associate_public_ip_address | Associate public IP address with instance | false |
| instance_type | EC2 instance type | t3.micro |
| disksize | Root disk size in GB | 20 |
| publish_to_saas | Publish the cluster name and private IPs to the Config0 run page | true |
| labels | Resource labels | null |
| cloud_tags_hash | Resource tags for the cloud provider | null |

## Dependencies

### Substacks

- `config0-hub:::aws::aws_ec2_server`
- `config0-hub:::mongodb::create_mongodb_pem`
- `config0-hub:::kafka::kafka_cluster_on_ubuntu`

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>
