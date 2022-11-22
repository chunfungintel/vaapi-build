#!/bin/bash

#for i in {1..3}; do sed -i '$d' /home/kpi/run.sh; done
mkdir -p /home/kpi/output/results/{videoAnalytics,encryptStorage}
source /home/kpi/run.sh
export GST_DEBUG="GVA_common:7"

