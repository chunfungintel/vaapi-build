#!/bin/bash

IMAGE="${1:-gar-registry.caas.intel.com/virtiot/vaapi-dxg:0eea345b0f-20221121231522}"

docker run -it \
--entrypoint bash  \
--privileged \
--network host \
-v /mnt/c/Users/eflow:/mnt/c/Users/eflow \
-v /usr/lib/wsl/drivers:/usr/lib/wsl/drivers \
${IMAGE}
