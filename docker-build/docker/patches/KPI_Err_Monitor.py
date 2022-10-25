#!/usr/bin/env python3

from gstgva import VideoFrame
import time
from WorkloadCommonLib  import msg_bus
import os
from WorkloadCommonLib import kpi
from WorkloadCommonLib import yaml_config_parser

class EvalKPI:
    def __init__(self, AppName):
        self.frame_start_time = self.FPS_counter = time.perf_counter()
        self.frame_end_time = 0
        self.frame_count = 0
        self.FPS_interval = 1
        self.FPS_Sum = 0
        self.AvgFPS_counter = 0
        self.FPS = 0

        self.app_Name = AppName

        #Initialize the MessageBus Layer
        self.mqtt_ip = None
        self.mqtt_port = None

        self.mqtt_ip = os.getenv('MQTT_IP_ADDRESS')
        self.mqtt_port = os.getenv('MQTT_PORT')

        self.msgBus_obj = msg_bus.MQTT_MsgBus()

        if self.mqtt_ip is not None and self.mqtt_port is not None:
            self.msgBus_obj.init_msg_bus(self.app_Name,self.mqtt_ip,self.mqtt_port)
        elif self.mqtt_ip is None and self.mqtt_port is None:
            self.msgBus_obj.init_msg_bus(self.app_Name)
        elif self.mqtt_ip is None and self.mqtt_port is not None:
            self.mqtt_ip = "localhost"
            self.msgBus_obj.init_msg_bus(self.app_Name,self.mqtt_ip,self.mqtt_port)
        elif self.mqtt_ip is not None and self.mqtt_port is None:
            self.msgBus_obj.init_msg_bus(self.app_Name,self.mqtt_ip)

        #Parse the KPI configuration
        config_file = "/home/kpi/config/" + os.getenv('WKLD_CONFIG') + ".yaml"

        kpi_vars =[ 'kpi_1_enabled', 'kpi_2_enabled', 'kpi_exit_on_failure', 'kpi_settling_time_seconds', 'kpi_number_nines', \
                'kpi_1_max_frametime_milliseconds', 'kpi_2_window_milliseconds', 'kpi_2_target_frames_per_window', 'kpi_2_min_frames_per_window']
        kpi_config = {}

        if config_file is not None:
            # parse the default config file
            parser = yaml_config_parser.YamlConfigParser(config_file)
            config = parser.YamlParse()
            if config is None:
                self.msgBus_obj.cleanup_msg_bus()
                exit()

            for key in kpi_vars:
                kpi_config[key] = parser.get(key, config)
                if kpi_config.get(key) == None:
                    print(f"{key}  paramater is missing ")
                    self.msgBus_obj.cleanup_msg_bus()
                    exit()
        else:
            #If custom config provided , read from ENV variables
            for key in kpi_vars:
                kpi_config[key] = int(os.getenv(key.upper()))
                if kpi_config.get(key) == None:
                    print(f"{key}  paramater is not set in ENV ")
                    self.msgBus_obj.cleanup_msg_bus()
                    exit()

        #Initialize KPI layer
        self.kpi_obj = kpi.KPI_Model()
        self.kpi_obj.init_KPI_model(self.app_Name,kpi_config,self.msgBus_obj)

    def KPI_ErrCheck(self, frame: VideoFrame) -> bool:
        self.frame_count += 1
        now = time.perf_counter()
        frame_latency_ms = (now - self.frame_start_time) * 1000
        self.FPS += 1
        self.frame_start_time  = now

        if int(os.getenv('SHOW_FPS')) == 1:
            if (now - self.FPS_counter) >= self.FPS_interval:
                fps = self.FPS/(now - self.FPS_counter)
                self.AvgFPS_counter += 1
                # leave initial 2sec as we wont get required number of frames to caluclate AVG
                if self.AvgFPS_counter > 2:
                    self.FPS_Sum += fps
                    AvgFPS = self.FPS_Sum /  (self.AvgFPS_counter  - 2)
                    print("FPS({}sec): {:.2f} ---------- Average FPS:{:.2f} \r".format(self.FPS_interval , fps , AvgFPS))
                self.FPS_counter = now
                self.FPS = 0
        self.kpi_obj.evaluate_kpi(self.frame_count, frame_latency_ms)
        return True

