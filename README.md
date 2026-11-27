# kafka
This is an Config0 contribution repository

The Kafka execgroups install Confluent Platform 5.3.1 from Confluent's Debian repository, with
Java 8 from the Ubuntu Noble archive. An apt preferences file holds every `confluent-*` package at 5.3.1-1.
Ansible runs on each node in localhost mode through the SSM execution engine: one host aggregate per node,
which the host-order handler runs as two child orders, setup then init, in the node's workspace.
One node kind runs at a time, starting with ZooKeeper.
The nodes need the region's server-config install, which supplies `ssh_key_name`, `instance_profile_name`,
`managed_tag_key`, `managed_tag_value` and `install_name`.
Node IPs and ids reach Ansible as `ANS_VAR_*` extra variables. The `kafka_on_ec2` `ca` job records the
cluster CA, and each node reads it as the `secret:::kafka_ca_pem` SSM secret.
The legacy SSH key, generated inventory, bastion, and remote-host actions were removed.
