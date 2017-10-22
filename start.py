#!/usr/bin/env python3
#test
import pathlib
pathlib.exec_dir = pathlib.abs_dir(globals().get('__file__'))
curr_folder = pathlib.exec_dir

from parser import *
from server import Detour, Daemon
import cherrypy

def main():
    cherrypy.config.update({
        'server.socket_port': 27900,
        'request.show_tracebacks': True,
    })
    Daemon(cherrypy.engine).subscribe()
    config = {
        '/': {
            'tools.staticdir.root': curr_folder,
        },
        '/public': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'public'
        }
    }
    cherrypy.quickstart(Detour(curr_folder + '/public'), '/', config)

if __name__ == '__main__':
    main()
