#!/bin/bash

export VAAPI_TEST_VIDEO=/home/dlstreamer/hello/Fireworks_1920x1080_12mbps_60fps_Baseline_at_L4.2.h264
gst-launch-1.0 -v filesrc location=${VAAPI_TEST_VIDEO} \
! h264parse ! vaapih264dec ! vaapisink

pip3 install opencv-python
/opt/intel/openvino/samples/python/hello_classification/hello_classification.py \
/home/dlstreamer/hello/alexnet/FP32/alexnet.xml \
/home/dlstreamer/hello/car.png \
GPU

