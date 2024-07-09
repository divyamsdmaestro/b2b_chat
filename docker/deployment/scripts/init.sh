#!/bin/bash

# Create a common network for all the services for communication
APP_NETWORK_NAME=iiht_b2b_chat
if [[ "$(docker network ls | grep -ow "${APP_NETWORK_NAME}")" == "" ]]; then
    docker network create "${APP_NETWORK_NAME}"
fi

echo "init.sh: All Done..."
