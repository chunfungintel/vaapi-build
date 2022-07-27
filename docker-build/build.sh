#!/bin/bash


IMAGE_TAG=${1//dockerfile_}
IMAGE_NAME=gar-registry.caas.intel.com/virtiot/vaapi-dxg:${IMAGE_TAG}
DOCKERFILE=${1}

docker build -f ${DOCKERFILE} -t $IMAGE_NAME .
docker push $IMAGE_NAME
