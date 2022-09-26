#!/bin/bash

#----------------------------------------------------------------------------
#
# INTEL CONFIDENTIAL
#
# Copyright 2022 (c) Intel Corporation.
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them  is governed by the  express license under which  they were
# provided to you ("License"). Unless the License provides otherwise, you  may
# not  use,  modify,  copy, publish,  distribute,  disclose  or transmit  this
# software or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no  express
# or implied  warranties, other  than those  that are  expressly stated in the
# License.
#
# Unified Shell Script to launch container Based Workloads
#----------------------------------------------------------------------------

# Intel http-proxy servers
http_proxy=${http_proxy:-http://proxy-chain.intel.com:912}
https_proxy=${https_proxy:-http://proxy-chain.intel.com:912}
HTTP_PROXY=${HTTP_PROXY:-http://proxy-chain.intel.com:912}
HTTPS_PROXY=${HTTPS_PROXY:-http://proxy-chain.intel.com:912}
no_proxy="intel.com,.intel.com,localhost,127.0.0.1,amr-registry-pre.caas.intel.com"
NO_PROXY="intel.com,.intel.com,localhost,127.0.0.1,amr-registry-pre.caas.intel.com"

###################################################
# Color escape codes
###################################################
RED='\033[0;31m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'		# No color

# Default Values
PRIVILEGED=''
VOL_MOUNTS=''
unique_env_command=''
NAME=''
entry_point_args=''
network_config='--network host'
additional_args=''

###################################################
# Print the usage
###################################################
print_usage() {
  echo "usage: ./run_container.sh [-f <path/to/container/config> or -l <path/to/local/config>] -m <mqtt-ip-address>
  [-u image:tag or -i image:tag] [-e v1=a, -e v2=b, ...] [optional: -p] [optional: -s] [Optional -n custom_name]
  [Optional -v /dev:/dev, -v s2:d2, ...] [Optional -a v1=a, -a v2=b, ...] [Optional -c]
  [-o '--pid=host --network host --shm-size=6G']\n"

  echo " -i image:tag starts a container image"
  echo " -u image:tag stops a running container image "
  echo " -f path to to a config.yml file in container image"
  echo " -l path to a local config.yml"
  echo " -m the IP address and port of the MQTT broker"
  echo " -e an environment variable to pass to the workload"
  echo " -s Option to enable privileged mode"
  echo " -v Option to add mount directories"
  echo " -n Option to set the custom name to the particular instance for docker run"
  echo " -p enables Intel internal proxy settings for HTTP and HTTPS, use the environmental variable if it is set else use the default values"
  echo " -a Option to pass additional args to the entrypoint scripts"
  echo " -c Option to remove the default host network option"
  echo " -o Option to pass additional args to docker, these args should be enclosed in quotes"
  echo "  |- Example: ./run_container.sh -i xyz -f config.yml -m 192.168.1.12 -p -s -e CGROUP_CPU_PERCENTAGE=0.9 -v /dev/:/dev"
}

###################################################
# Parse command line parameters
###################################################
while getopts f:l:m:e:h:i:u:v:n:a:o:psc  flag
do
    case "${flag}" in
        f)
            CONFIG=${OPTARG};;
        l)
            CONFIG_LOCAL=${OPTARG};;
        m)
            IP_ADDRESS=${OPTARG};;
        e)
            ENV_LIST="${ENV_LIST} --env ${OPTARG}";;
        s)
            PRIVILEGED="--privileged ";;
        p)
            ENV_LIST="${ENV_LIST} \
              --env HTTP_PROXY=${HTTP_PROXY} --env HTTPS_PROXY=${HTTPS_PROXY} \
              --env http_proxy=${http_proxy} --env https_proxy=${https_proxy} \
              --env no_proxy=${no_proxy} --env NO_PROXY=${NO_PROXY}" ;;
        i)
            IMAGE=${OPTARG}
            CMD="docker run -i";;
        v)
            VOL_MOUNTS+="-v ${OPTARG} ";;
        n)
            #name=`echo $RANDOM | md5sum | head -c 6; echo;`
            NAME=" --name ${OPTARG} ";;
            #NAME=" --name ${OPTARG}_$name ";;
        u)
            IMAGE=${OPTARG}
            docker_id=$( docker ps -q --filter ancestor="${OPTARG}" )
            UNINSTALL_CMD="docker stop ${docker_id} ";; #; docker rm ${docker_id}
        a)
            entry_point_args+="${OPTARG} ";;
        c)
            network_config='';;
        o)
            additional_args+="${OPTARG} ";;
        h|*)
            print_usage
            exit 1;;
    esac
done

if [ -n "$UNINSTALL_CMD" ]
then
  echo "${UNINSTALL_CMD}"
  ${UNINSTALL_CMD}
  exit 0
fi

remove_duplicate_env_variables()
{
  local_key_lst=()
  local_idx=0
  env_key_lst=()
  env_idx=0

  # Replace --env to empty in local config variable
  local_params=$(echo "$1" | sed -r 's/--env //g')
  l1=(${local_params//=/ })

  # Replace --env to empty in env variables
  env_local_params=$(echo "$2" | sed -r 's/--env //g')
  l2=(${env_local_params//=/ })

  # Loop through the local variables and get the Keys
  for ((i=0;i<${#l1[@]};i+=2)); do
    local_key_lst[local_idx]="${l1[i]}"
    let local_idx+=1
  done

  # Loop through the env variables and get the Keys
  for ((i=0;i<${#l2[@]};i+=2)); do
    env_key_lst[env_idx]="${l2[i]}"
    let env_idx+=1
  done

  # Find the duplicates
  duplicate_keys=$(echo "${local_key_lst[@]}" "${env_key_lst[@]}" | tr ' ' '\n' | sort | uniq -d)

  # Compose the unique env variables
  for ((i=0;i<${#l1[@]};i+=1)); do
    if [[ "$duplicate_keys" != *"${l1[i]}"* ]]; then
      unique_env_command+="--env ${l1[i]}=${l1[i+1]} "
    fi
    let i+=1
  done

  # Append Env variable that takes precedence over local variable
  unique_env_command+="$2"
}

if [ -n "$CONFIG" ] && [ -n "$CONFIG_LOCAL" ]
then
   echo -e "${RED}ERROR: Both -f and -l parameters cannot be set. ${NC}\n\n"
   print_usage
   exit 1
elif [ -n "$CONFIG_LOCAL" ]
then
   # Convert YAML config file to environment variable list string
   ENV_LIST_LOCAL=$(python3 convert_configfile_to_envvarlist.py $CONFIG_LOCAL)
   if [ $? -gt 0 ]
   then
     echo -e "${RED}ERROR: local config file conversion to environment variable list failed ${NC}"
     echo -e "${RED}  |- ${ENV_LIST_LOCAL}${NC}"
     exit 1
   fi
   remove_duplicate_env_variables "${ENV_LIST_LOCAL}" "${ENV_LIST}"
   ENV_LIST="$unique_env_command "
elif [ -n "$CONFIG" ]
then
   ENV_LIST="--env WKLD_CONFIG=${CONFIG} ${ENV_LIST}"
fi

if [ -z "$CMD" ]
then
  echo -e "${RED}ERROR: option -i or -u must be specified. ${NC}\n\n"
  print_usage
  exit 1
fi

# Pass in MQTT IP address as an environment variable
CMD="${CMD}${NAME} --rm ${network_config} ${additional_args} ${PRIVILEGED}${VOL_MOUNTS}${ENV_LIST} -v /tmp/wlc_workload_results:/tmp/wlc_workload_results --env MQTT_IP_ADDRESS=${IP_ADDRESS} \
-e DISPLAY=:99 \
-v /usr/lib/wsl:/usr/lib/wsl \
${IMAGE} ${entry_point_args}"

#-e DISPLAY=:0 \
#-v /usr/lib/wsl:/usr/lib/wsl \
#-v /home/ubuntu/.Xauthority:/home/dlstreamer/.Xauthority \
#-v /home/ubuntu/.Xauthority:/root/.Xauthority \
#-v /usr/share/X11:/usr/share/X11 \
#-v /etc/X11:/etc/X11 \
#-v /mnt/wslg:/mnt/wslg \
#-v /mnt/c/Users/eflow:/mnt/c/Users/eflow \
#-v /tmp:/tmp \


echo "${CMD}"
${CMD}
