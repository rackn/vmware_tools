# Docker And Development Info

## Using Docker to help test the agent
Using the Dockerfile build and fire up an instance of the
container and log into it, using a volume mount to share your
drpy development env with the container.

    docker build -t drpydev .
    docker run -it --rm -v /home/errr/programs/work/vmware_tools/drpy:/opt/rackn drpydev /bin/bash

Next you want to install drpy into the container in
development mode.

    cd /opt/rackn
    pip3 install -e .

Next make a config file. Below is an example

    [Config]
    endpoint = https://drp.mrice.internal:8092/api/v3
    token = (generate using: drpcli users token rocketskates ttl 3y | jq -r .Token)
    machine_uuid = efc8bba7-0adc-4b89-8299-02e9fa49e239


Next start the agent

    agent -f foo.conf