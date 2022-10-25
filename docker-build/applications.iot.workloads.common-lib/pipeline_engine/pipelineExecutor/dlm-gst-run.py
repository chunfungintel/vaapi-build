#!/usr/bin/env python3
#
# Gstreamer kmssink example python application using leased DRM device(s) from
# a drm-lease-manager.
#
# Requires kmssink set_window_handle interface support.
#
#  https://github.com/intel-media-ci/gstreamer/pull/23
#  https://gerrit.automotivelinux.org/gerrit/gitweb?p=src/drm-lease-manager.git;a=summary
#
# Usage:
#  $ drm-lease-manager -vt &
#  $ dlm-gst-run <gst-launch-1.0 ... pipeline cmd> <card>
#

import os
import sys
from Xlib import display
from Xlib.ext import randr
from os import listdir

from ctypes import *
dlm = cdll.LoadLibrary("libdrmlease.o")
dlm.drm_lease.argtypes = [c_char_p]

import gi
gi.require_version('GIRepository', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GstVideo, GLib, GObject

class Lease:
  def __init__(self, card):
    self.card   = bytes(card, 'utf-8')
    self.handle = dlm.drm_lease(self.card)

    assert self.handle > 0, "Could not lease dlm handle"

    print("Got DLM Handle:", self.handle)

  def __del__(self):
    print("Release lease:", self.handle)

def get_x11_socket_no():
  # X11 server (Xorg) unix-domain socker directory
  xpath = "/tmp/.X11-unix"
  socketno = "0"
  for f in listdir(xpath):
    if len(f) == 2 and f[0] == 'X':
      socketno = f[1]
  return socketno

def get_display_info(monitor):
  s = get_x11_socket_no()
  d = display.Display(':'+s)
  screen_count = d.screen_count()
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
      result.append("" + str(i) + "-" + params.name)
      i=i+1

  return result[monitor]

Gst.init(None)

loop      = GLib.MainLoop()
#cmd       = sys.argv[1]
leases    = list()
monidx    = -1
if len(sys.argv) == 2:
  cmd     = sys.argv[1]
elif len(sys.argv) == 3:
  monidx  = int(sys.argv[2])
  print("INFO: get input monitor index " + str(monidx))
  monitorname = get_display_info(monidx)
  print("INFO: lease monitor " + monitorname)
  lease = Lease(monitorname)
  leases.append(lease)
  """ Inserts 'fd=x' into 'cmd' right after 'kmssink'. """
  tempcmd = sys.argv[1]
  kmssink = "kmssink"
  i = tempcmd.find(kmssink)
  if i == -1: # not found
    cmd = tempcmd
  else:
    fdText = " fd={} ".format(lease.handle)
    cmd = tempcmd[:i + len(kmssink)] + fdText + tempcmd[i + len(kmssink):]

def on_message(bus, message):
  if Gst.MessageType.EOS is message.type:
    loop.quit()
  elif Gst.MessageType.ERROR is message.type:
    err, debug = message.parse_error()
    print("ERROR:", err, debug)
    loop.quit()

##def on_sync_message(bus, message):
##  if message.get_structure().get_name() == "prepare-window-handle":
##    if monidx != -1:
##      monitorname = get_display_info(monidx)
##      print("INFO: lease monitor " + monitorname)
##      lease = Lease(monitorname)
##      leases.append(lease)
##      message.src.set_window_handle(lease.handle)

try:
  pipeline = Gst.parse_launch(cmd)
  #print(cmd)
  bus = pipeline.get_bus()
  bus.add_signal_watch()
  bus.enable_sync_message_emission()
  bus.connect("message", on_message)
  #bus.connect("sync-message::element", on_sync_message)

  pipeline.set_state(Gst.State.PLAYING)

  loop.run()
finally:
  pipeline.set_state(Gst.State.NULL)
  while len(leases):
    lease = leases.pop()
    del lease
