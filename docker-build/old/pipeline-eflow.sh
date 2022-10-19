#!/bin/bash

echo EFLOW modified pipeline

set -x

sed -i 's/video\/x-raw(memory:VASurface)/video\/x-raw/g' /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json && \
sed -i 's/video\/x-raw(memory:VAMemory)/video\/x-raw/g' /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json && \
sed -i 's/tune=3//g' /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json && \
sed -i 's/,height=720,width=1280//g'  /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json && \
sed -i 's/"vaapi"/"auto"/g' /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json && \
sed -i 's/"vaapi"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-measured-aibox-low-na-avc-cpu.json && \
sed -i 's/"vaapi"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-measured-aibox-low-na-avc-gpu.json && \
sed -i 's/"vaapi"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-measured-aibox-mid-na-avc-cpu.json && \
sed -i 's/"vaapi"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-measured-aibox-mid-na-avc-gpu.json && \
sed -i 's/"vaapi"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-proxy-aiboxTheo-low-na-avc-cpu.json && \
sed -i 's/"vaapi"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-proxy-aiboxTheo-low-na-avc-gpu.json && \
sed -i 's/"vaapi"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-proxy-aiboxTheo-mid-na-avc-cpu.json && \
sed -i 's/"vaapi"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-proxy-aiboxTheo-mid-na-avc-gpu.json && \
sed -i 's/"vaapi-surface-sharing"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-proxy-aiboxTheo-low-na-avc-gpu.json && \
sed -i 's/"vaapi-surface-sharing"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-proxy-aiboxTheo-mid-na-avc-gpu.json && \
sed -i 's/"vaapi-surface-sharing"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-measured-aibox-low-na-avc-gpu.json && \
sed -i 's/"vaapi-surface-sharing"/"auto"/g' /home/kpi/workload/workload-config/nvr-adl-measured-aibox-mid-na-avc-gpu.json && \
sed -i 's/vah264dec/vaapih264dec/g' /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json && \
sed -i 's/vah264lpenc/vaapih264enc/g' /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json


jq 'del(.subPipelines.aibox_mid_pipeline_rtspsrc.elements[] | select(.elementName == "gvawatermark") )' \
/home/kpi/workload/workload-config/pipelines/aibox-pipeline.json | tee /tmp/aibox-pipeline.json >/dev/null && \
cp /tmp/aibox-pipeline.json /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json
jq 'del(.subPipelines.aibox_mid_pipeline_filesrc.elements[] | select(.elementName == "gvawatermark") )' \
/home/kpi/workload/workload-config/pipelines/aibox-pipeline.json | tee /tmp/aibox-pipeline.json >/dev/null && \
cp /tmp/aibox-pipeline.json /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json
jq 'del(.subPipelines.theo_mid_pipeline.elements[] | select(.elementName == "gvawatermark") )' \
/home/kpi/workload/workload-config/pipelines/aibox-pipeline.json | tee /tmp/aibox-pipeline.json >/dev/null && \
cp /tmp/aibox-pipeline.json /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json

jq 'del(.subPipelines.aibox_mid_pipeline_rtspsrc.elements[] | select(.elementName == "vapostproc") )' \
/home/kpi/workload/workload-config/pipelines/aibox-pipeline.json | tee /tmp/aibox-pipeline.json >/dev/null && \
cp /tmp/aibox-pipeline.json /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json
jq 'del(.subPipelines.aibox_mid_pipeline_filesrc.elements[] | select(.elementName == "vapostproc") )' \
/home/kpi/workload/workload-config/pipelines/aibox-pipeline.json | tee /tmp/aibox-pipeline.json >/dev/null && \
cp /tmp/aibox-pipeline.json /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json
jq 'del(.subPipelines.theo_mid_pipeline.elements[] | select(.elementName == "vapostproc") )' \
/home/kpi/workload/workload-config/pipelines/aibox-pipeline.json | tee /tmp/aibox-pipeline.json >/dev/null && \
cp /tmp/aibox-pipeline.json /home/kpi/workload/workload-config/pipelines/aibox-pipeline.json
