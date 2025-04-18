# Kafka Cluster Deployment

This stack automates the deployment of a complete Kafka cluster on Ubuntu servers. It sets up and configures all necessary components including ZooKeeper, Kafka brokers, Schema Registry, Kafka Connect, REST API, KSQL, and Control Center.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| bastion_hostname | Bastion host name | &nbsp; |
| kafka_cluster | Kafka cluster name | &nbsp; |
| ssh_key_name | Name label for SSH key | &nbsp; |
| aws_default_region | Default AWS region | &nbsp; |
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
| vm_username | Configuration for vm username | ubuntu |
| publish_to_saas | Boolean to publish values to config0 SaaS UI | null |
| tf_runtime | Terraform runtime version | tofu:1.6.2 |
| ansible_docker_image | Ansible container image | config0/ansible-run-env |

## Dependencies

### Execgroups

- [config0-publish:::github::lambda_trigger_stepf](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/github/lambda_trigger_stepf/default)
- [config0-publish:::ubuntu::docker](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/ubuntu/docker/default)
- [config0-publish:::ansible::ubuntu](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/ansible/ubuntu/default)
- [config0-publish:::kafka::ubuntu_vendor_setup](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/kafka/ubuntu_vendor_setup/default)
- [config0-publish:::kafka::ubuntu_vendor_init_cluster](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/exec/groups/config0-publish/kafka/ubuntu_vendor_init_cluster/default)

### Shelloutconfigs

- [config0-publish:::terraform::resource_wrapper](http://config0.http.redirects.s3-website-us-east-1.amazonaws.com/assets/shelloutconfigs/config0-publish/terraform/resource_wrapper/default)

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>