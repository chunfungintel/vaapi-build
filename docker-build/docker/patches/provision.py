#!/usr/bin/env python3
#
# Read display output and using xrandr to turn off monitors
#

import os
from os import listdir
from Xlib import display
from Xlib.ext import randr

def get_x11_socket_no():
  # X11 server (Xorg) unix-domain socker directory
  xpath = "/tmp/.X11-unix"
  socketno = "0"
  for f in listdir(xpath):
    if len(f) == 2 and f[0] == 'X':
      socketno = f[1]
  return socketno

def turn_off_monitor_from_xserver(s):
  s = get_x11_socket_no()
  d = display.Display(':'+s)
  default_screen = d.get_default_screen()
  result = []
  screen = 0
  info = d.screen(screen)
  window = info.root

  res = randr.get_screen_resources(window)

  i = 0
  for output in res.outputs:
    params = d.xrandr_get_output_info(output, res.config_timestamp)

    if len(params.crtcs) == 0 or len(params.modes) != 0:
      os.system("xrandr --output " + params.name + " --set non-desktop 1")
      os.system("xrandr --output " + params.name + " --off")
      i=i+1

  if i < 4:
    print("ERROR: the system has less than 4 monitors connected, NVR testcase may run with failure!")


socketnum = get_x11_socket_no()
os.environ.setdefault('DISPLAY', ':'+socketnum)
os.system("xhost +")
turn_off_monitor_from_xserver(socketnum)
