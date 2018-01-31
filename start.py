#!/usr/bin/env python3

from parser import *
from server import Detour, Daemon, WSHandler
import cherrypy
from pathlib import Path

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool


def main():
    cherrypy.config.update({
        'server.socket_port': 27900,
        'request.show_tracebacks': True,
    })

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    curr_folder = str(Path(__file__).parent.absolute())
    Daemon(cherrypy.engine).subscribe()
    config = {
        '/': {
            'tools.staticdir.root': curr_folder,
        },
        '/public': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'public',
        },
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': WSHandler,
        },
    }
    cherrypy.quickstart(Detour(curr_folder + '/public'), '/', config)

if __name__ == '__main__':
    main()
