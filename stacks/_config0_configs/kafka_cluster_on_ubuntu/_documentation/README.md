# Kafka Cluster Deployment

This stack automates the deployment of a complete Kafka cluster on Ubuntu servers. It sets up and configures all necessary components including ZooKeeper, Kafka brokers, Schema Registry, Kafka Connect, REST API, KSQL, and Control Center.

## Variables

### Required Variables

| Name | Description |
|------|-------------|
| bastion_hostname | Bastion host name |
| kafka_cluster | Kafka cluster name |
| ssh_key_name | Name label for SSH key |
| aws_default_region | Default AWS region |
| zookeeper_hosts | 99checkme99 List of hostnames for ZooKeeper nodes |
| broker_hosts | 99checkme99 List of hostnames for Kafka broker nodes |
| schema_registry_hosts | 99checkme99 List of hostnames for Schema Registry nodes |
| connect_hosts | 99checkme99 List of hostnames for Kafka Connect nodes |
| rest_hosts | 99checkme99 List of hostnames for REST API nodes |
| ksql_hosts | 99checkme99 List of hostnames for KSQL nodes |
| control_center_hosts | 99checkme99 List of hostnames for Control Center nodes |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| vm_username | Configuration for vm username | ubuntu |
| publish_to_saas | Boolean to publish values to config0 SaaS UI | null |
| tf_runtime | Terraform runtime version | tofu:1.6.2 |
| ansible_docker_image | Ansible container image | config0/ansible-run-env |

## Features

- Automated deployment of a complete Kafka cluster ecosystem
- Multi-node support for all Kafka components
- Configurable host distribution for Kafka services
- Automated Python and Docker installation on target servers
- Secure SSH key management for server access
- Integration with Config0 SaaS for resource tracking (optional)
- Centralized Control Center for monitoring and management

## Dependencies

### Execgroups

- [config0-publish:::ubuntu::docker](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/ubuntu/docker)
- [config0-publish:::ansible::ubuntu](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/ansible/ubuntu)
- [config0-publish:::kafka::ubuntu_vendor_setup](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/kafka/ubuntu_vendor_setup)
- [config0-publish:::kafka::ubuntu_vendor_init_cluster](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-publish/kafka/ubuntu_vendor_init_cluster)

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.