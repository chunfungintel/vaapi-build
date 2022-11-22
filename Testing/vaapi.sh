#!/bin/bash

export DATA_PATH=/home/kpi
export VAAPIH264DEC=vaapih264dec
export VAAPI_TEST_VIDEO=/home/dlstreamer/hello/output-416-10s.h264
export IE_DEVICE=GPU
export PREPROCESS=vaapi
gst-launch-1.0 -v \
filesrc location=${VAAPI_TEST_VIDEO} \
! h264parse \
! ${VAAPIH264DEC} \
! queue \
! gvadetect model=${DATA_PATH}/datasets/model/yolo-v2-tiny-tf.xml device=${IE_DEVICE} \
inference-interval=5 model-proc=${DATA_PATH}/datasets/model/yolo-v2-tiny-tf.json \
pre-process-backend=${PREPROCESS} \
! queue \
! vaapih264enc ! filesink location=/mnt/c/Users/eflow/Downloads/aibox-edge-$(date '+%Y-%m-%d_%H-%M-%S').h264

