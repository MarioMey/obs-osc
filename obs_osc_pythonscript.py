#!/usr/bin/env python3
"""
OBS-OSC-PythonScript (https://github.com/MarioMey/obs-osc-pythonscript)

It's an OBS Python scripts that allows to receive/send OSC messages from/to 
OBS and from/to another OSC sending capable software, like PureData, 
MobMuPlat, TouchOSC, etc. It is based on OBS script OSC Sender for OBS, but
this time, it can receive messages(original doesn't). It uses python-osc and 
it neither use obs-websockets nor obs-websockets-py.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Mario Mey"
__contact__ = "mariomey@gmail.com"
__credits__ = []
__date__ = "2021/07/29"
__deprecated__ = False
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.3"

import time, threading
import obspython as obs

from obs_osc_api import (
	scene_change, 
	consola, 
	consola_hslider, 
	c1, c2, c3, 
	c, 
	th
)

from obs_api import (
	scene_change, 
	item_set_visible,
	item_remove, 
	item_duplicate,
	item_reference,
	item_set_transform,
	item_get_transform,
	item_set_pos,
	item_set_scl,
	item_set_rot,
	item_set_alignment,
	item_set_visible,
	item_set_crop,
	item_set_scl_filter,
	item_get_order_index,
	item_set_order_index,
	item_swap_order_index,
	item_set_private_setting,
	item_create_group,
	item_create_text,
	item_create_image,
	item_create_video,
)

from obs_api import (
	source_set_image_file, 
	source_set_video_file, 
	source_set_slide_time,
	source_set_text,
	source_set_text_size,
	source_set_volume, 
	source_set_opacity,
	source_set_bri_sat_hue, 
	source_set_hue, 
	source_set_lut_file,
	source_set_setting,
	source_filter_set_value, 
	source_filter_set_enabled, 
	source_filter_get_settings, 
	source_set_text,
	source_capture_window, 
	source_get_settings, 
	source_capture_window
)

from obs_tween import (
	item_tween, 
	source_tween
)

from pythonosc import osc_message_builder
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

clientPort = 10000
serverPort = 10008
clientIP = "127.0.0.1"
server = None

client = udp_client.SimpleUDPClient(clientIP, clientPort)
client.send_message("/init", 1)

def source_activated(cd):
    global pleaseLog
    source = obs.calldata_source(cd, "source")
    if source is not None:
        name = obs.obs_source_get_name(source)
        if name[0] == "/":
            client.send_message(name, 1)
            if (pleaseLog):
                print("send " + name)

def handleOSC(address, args, data):
	print(f'{address}, {args}, {data}')

def source_tween_(*args):
	
	if args[1] in ['to_value', 'value']:
		source_tween(None,
			source_name=args[2],
			filter_name=args[3],
			setting=args[4],
			to_value=args[5],
			duration=args[6],
			delay=args[7] if len(args) > 7 else 0,
			ease_type=args[8] if len(args) > 8 else 'linear')

	elif args[1] == 'from_to_value':
		source_tween(None, 
			source_name=args[2],
			filter_name=args[3],
			setting=args[4],
			from_value=args[5],
			to_value=args[6],
			duration=args[7],
			delay=args[8] if len(args) > 8 else 0,
			ease_type=args[9] if len(args) > 9 else 'linear')

def item_tween_(*args):

	if args[1] in ['to_pos', 'pos']:
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			to_pos_x=args[4],
			to_pos_y=args[5],
			duration=args[6],
			delay=args[7] if len(args) > 7 else 0,
			ease_type=args[8] if len(args) > 8 else 'linear')

	elif args[1] == 'from_to_pos':
		item_tween(None, 
			scene_name=args[2],
			item_name=args[3],
			from_pos_x=args[4],
			from_pos_y=args[5], 
			to_pos_x=args[6],
			to_pos_y=args[7],
			duration=args[8],
			delay=args[9] if len(args) > 9 else 0,
			ease_type=args[10] if len(args) > 10 else 'linear')
	
	elif args[1] in ['to_scl', 'scl']:
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			to_scl_x=args[4],
			to_scl_y=args[5],
			duration=args[6],
			delay=args[7] if len(args) > 7 else 0,
			ease_type=args[8] if len(args) > 8 else 'linear')

	elif args[1] == 'from_to_scl':
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			from_scl_x=args[4],
			from_scl_y=args[5], 
			to_scl_x=args[6],
			to_scl_y=args[7],
			duration=args[8],
			delay=args[9] if len(args) > 9 else 0,
			ease_type=args[10] if len(args) > 10 else 'linear')

	elif args[1] in ['to_rot', 'rot']:
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			to_rot=args[4],
			duration=args[5],
			delay=args[6] if len(args) > 6 else 0,
			ease_type=args[7] if len(args) > 7 else 'linear')

	elif args[1] == 'from_to_rot':
		item_tween(None, 
			scene_name=args[2],
			item_name=args[3],
			from_rot=args[4],
			to_rot=args[5],
			duration=args[6],
			delay=args[7] if len(args) > 7 else 0,
			ease_type=args[8] if len(args) > 8 else 'linear')

	elif args[1] in ['to_transform', 'transform']:
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			to_pos_x=args[4],
			to_pos_y=args[5],
			to_scl_x=args[6],
			to_scl_y=args[7],
			to_rot=args[8], 
			duration=args[9],
			delay=args[10] if len(args) > 10 else 0,
			ease_type=args[11] if len(args) > 11 else 'linear')

	elif args[1] == 'from_to_transform':
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			from_pos_x=args[4],
			from_pos_y=args[5],
			from_scl_x=args[6],
			from_scl_y=args[7],
			from_rot=args[8],
			to_pos_x=args[9],
			to_pos_y=args[10],
			to_scl_x=args[11],
			to_scl_y=args[12],
			to_rot=args[13],
			duration=args[14], 
			delay=args[15] if len(args) > 15 else 0,
			ease_type=args[16] if len(args) > 16 else 'linear')

# defines script description 
def script_description():
	return '''obs-osc-pythonscript
	OBS Python scripts that allows to receive/send OSC messages from/to OBS and from/to another OSC sending capable software, like PureData, MobMuPlat, TouchOSC, etc.'''

# defines user properties
def script_properties():
	#global props 
	props = obs.obs_properties_create()
	obs.obs_properties_add_text(props, "host", "Host IP", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_int(props, "port", "Host port", 1, 400000, 1)
	obs.obs_properties_add_bool(props, "logOscOutput", "Log OSC output")
	obs.obs_properties_add_int(props, "serverPort", "Listen port", 1, 400000, 1)
	return props

def script_defaults(settings):
	obs.obs_data_set_default_string(settings, "host", clientIP)
	obs.obs_data_set_default_int(settings, "port", clientPort)
	obs.obs_data_set_default_int(settings, "serverPort", serverPort)


def script_load(settings):
	global despachante
	
	sh = obs.obs_get_signal_handler()
	obs.signal_handler_connect(sh, "source_activate", source_activated)

	despachante = dispatcher.Dispatcher()

	despachante.map("/scene_change", scene_change)

	despachante.map("/item_set_visible",         item_set_visible)
	despachante.map("/item_remove",              item_remove)
	despachante.map("/item_tween",               item_tween_)
	despachante.map("/item_duplicate",           item_duplicate)
	despachante.map("/item_reference",           item_reference)
	despachante.map("/item_get_transform",       item_get_transform)
	despachante.map("/item_set_transform",       item_set_transform)
	despachante.map("/item_set_pos",             item_set_pos)
	despachante.map("/item_set_scl",             item_set_scl)
	despachante.map("/item_set_rot",             item_set_rot)
	despachante.map("/item_set_alignment",       item_set_alignment)
	despachante.map("/item_set_visible",         item_set_visible)
	despachante.map("/item_set_crop",            item_set_crop)
	despachante.map("/item_get_order_index",     item_get_order_index)
	despachante.map("/item_set_order_index",     item_set_order_index)
	despachante.map("/item_swap_order_index",    item_swap_order_index)
	despachante.map("/item_set_private_setting", item_set_private_setting)
	despachante.map("/item_set_scl_filter",      item_set_scl_filter)
	despachante.map("/item_create_group",        item_create_group)
	despachante.map("/item_create_text",         item_create_text)
	despachante.map("/item_create_image",        item_create_image)
	despachante.map("/item_create_video",        item_create_video)


	despachante.map("/source_tween",               source_tween_)
	despachante.map("/source_set_image_file",      source_set_image_file)
	despachante.map("/source_set_video_file",      source_set_video_file)
	despachante.map("/source_set_slide_time",      source_set_slide_time)
	despachante.map("/source_set_text",            source_set_text)
	despachante.map("/source_set_text_size",       source_set_text_size)
	despachante.map("/source_set_volume",          source_set_volume)
	despachante.map("/source_set_opacity",         source_set_opacity)
	despachante.map("/source_filter_set_enabled",  source_filter_set_enabled)
	despachante.map("/source_filter_set_value",    source_filter_set_value)
	despachante.map("/source_filter_get_settings", source_filter_get_settings)
	despachante.map("/source_set_setting",         source_set_setting)
	despachante.map("/source_set_bri_sat_hue",     source_set_bri_sat_hue)
	despachante.map("/source_set_hue",             source_set_hue)
	despachante.map("/source_set_lut_file",        source_set_lut_file)
	despachante.map("/source_capture_window",      source_capture_window)
	despachante.map("/source_get_settings",        source_get_settings)
	# despachante.map("/*", handleOSC)


def script_unload():
	global server
	
	print(f'Script_unload')
	global server
	server.server_close()
	time.sleep(1)

def script_update(settings):
	global host
	global port
	global client
	global server
	global pleaseLog

	pleaseLog    = obs.obs_data_get_bool(settings, "logOscOutput")
	host         = obs.obs_data_get_string(settings, "host")
	port         = obs.obs_data_get_int(settings, "port")

	client = udp_client.SimpleUDPClient(host, port)
	print("target set to "+host+":"+str(port)+"")

	# Server
	serverPort = obs.obs_data_get_int(settings, "serverPort")
	try:
		server.server_close()
	except:
		print('*Server not created yet')

	server = osc_server.BlockingOSCUDPServer(("127.0.0.1", serverPort), despachante)
	th(server_th, [settings])

	# Loop cada 1000ms
	# obs.timer_remove(funcion_loop)
	# if and source_name != "":
		# obs.timer_add(funcion_loop, 1000)

def server_th(settings):
	print(f'Serving on {server.server_address}')
	server.serve_forever()  # Blocks forever
	print(f'CORRECTLY CLOSED SERVER {server.server_address}')
