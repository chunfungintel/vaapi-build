#!/bin/bash
print_usage() {
  echo "usage: ./run.sh -m <mqtt-ip-address> -t <mqtt-topic>\n"

  echo "  -m the IP address and port of the MQTT broker"
  echo "  -t the topic to publish of the MQTT broker"
}

while getopts m:t: flag
do
    case "${flag}" in
        m)
            export MQTT_IP_ADDRESS=${OPTARG};;
        t)
            export MqttTopic=${OPTARG};;
        *)
            print_usage
            ;;
    esac
done

if [ -z $MQTT_IP_ADDRESS ]; then
  export MQTT_IP_ADDRESS=localhost
fi

export WKLD_DIR="$( cd "$( dirname "${BASH_SOURCE[0]-$0}" )" >/dev/null 2>&1 && pwd )"
export WKLD_LIBS_DIR=${WKLD_DIR}/libs
export cl_cache_dir=${WKLD_DIR}/cl_cache

source /opt/intel/oneapi/compiler/latest/env/vars.sh
source /opt/intel/openvino/setupvars.sh
source /opt/intel/dlstreamer/setupvars.sh

export GST_PLUGIN_PATH=${WKLD_LIBS_DIR}:/root/gstreamer/gst/lib/x86_64-linux-gnu/gstreamer-1.0:${GST_PLUGIN_PATH}:/usr/lib/x86_64-linux-gnu/gstreamer-1.0
export LD_LIBRARY_PATH=${WKLD_LIBS_DIR}:/root/gstreamer/gst/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}

export PYTHONUNBUFFERED=1

unset http_proxy
unset https_proxy

if ! [[ -z $RTSPSrc ]]; then
  rtsp_ip=${RTSPSrc%:*}
  export no_proxy=${no_proxy},$rtsp_ip
fi

#if [[ -d "/tmp/.X11-unix" ]]; then
#  socket_num=1
#  for s in `ls /tmp/.X11-unix`; do
#    if [[ ${#s} == 2 ]]; then
#      socket_num=$((${s/X/}))
#      #echo "$s-> $socket_num"
#    fi
#  done
#  export DISPLAY=:$socket_num
#  python3 /home/kpi/libs/provision.py
#fi

if [[ "${DISPLAY//:}" == 99 ]]; then
echo EFLOW
Xvfb :99 -screen 0 1920x1080x24 &
fi

if [[ -n "$EFLOW_PIPELINE" ]]
then
    echo "not Empty"
    eval "$EFLOW_PIPELINE"
else
    echo "empty"
fi

cd ${WKLD_DIR}/workload/pipelineExecutor && npm start &
sleep 1
cd ${WKLD_DIR}/workload/pipelineController && npm start
