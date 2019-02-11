from multiprocessing import Process, Pipe
from logger import warn, info, debug, error
from plugin_wrapper import PluginWrapper
from event_types import EVENT_LOG, EVENT_TIMER
from os import listdir
from os.path import isfile, join
import sys

class PluginManager:

    def __init__(self):
        self.plugs = []
        self.processes = []

    def register_plug(self, clas, args):
        parent_conn, child_conn = Pipe()
        self.plugs.append(parent_conn)

        p = Process(target=PluginWrapper(clas), args=(child_conn,args))
        self.processes.append(p)

        p.start()

    def send_to_plugs(self, msg):
        for p in self.plugs:
            try:
                p.send(msg)
            except ValueError as err:
                error('Failed sending {}'.format(msg))
                continue

    def stop_plugins(self):
        for p in self.processes:
            try:
                p.terminate()
            except:
                continue

    def load_plugins(self, args_plug):
        plugin_files = [f for f in listdir('./plugins/') if isfile(join('./plugins/', f))]

        debug(plugin_files)

        for p in plugin_files:
            try:
                module_name = 'plugins.{}'.format(p[0:-3])
                if p[0:-3] != '__init__':
                    debug('Loading {}'.format(module_name))
                    exec('import {}'.format(module_name))
                    mod = sys.modules[module_name]
                    clas = mod.Plugin
                    self.register_plug(clas, args_plug)

            except Exception as e: # TODO: handle expected exceptions and do proper error printing 
                error('Failed to load plugin: {}'.format(p))
                error(e)

    
