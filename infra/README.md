# Usage instructions
Provision machines
```
sudo vagrant up
```
Stop machines
```
sudo vagrant halt
```
Destroy machines
```
sudo vagrant destroy
```
SSH to chosen machine
```
sudo vagrant ssh <name>
# e.g. sudo vagrant ssh cassandra_1
```

# Architectures
Vagrantfile contains configuration for amd64 and arm64 architectures. By default the amd64 is commented out.

# Cassandra set-up
To set up cassandra do the following instructions
```
sudo systemctl stop cassandra
sudo rm -rf /var/lib/cassandra/{commitlog,data,hints,saved_caches}/*
vim /etc/cassandra/cassandra.yaml
    # Fields to be set up:
    # - cluster_name
    # - seed.provider.parameters.seeds
    # - listen_address
sudo systemctl start cassandra
```