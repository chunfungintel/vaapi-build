#!/bin/bash


#IMAGE_TAG=${1//dockerfile_}
IMAGE_TAG=`git rev-parse --short=10 HEAD`-`date '+%Y%m%d%H%M%S'`
IMAGE_NAME=gar-registry.caas.intel.com/virtiot/vaapi-dxg:${IMAGE_TAG}
DOCKERFILE=${1}

DOCKER_BUILDKIT=1 \
docker build \
--cpuset-cpus 0-$(nproc) \
--secret id=mynetrc,src=$HOME/.netrc \
--no-cache=false \
-f ${DOCKERFILE} \
-t $IMAGE_NAME .

docker push $IMAGE_NAME

echo $IMAGE_NAME
