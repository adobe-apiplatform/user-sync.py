# Copyright (c) 2016-2017 Adobe Systems Incorporated.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

import os
import threading
import vcr
import requests

class TestService:
    def __init__(self, config):
        '''
        Initializes the server with the specified configuration.
        '''
        self.config = {
                'proxy_host': 'localhost',
                'proxy_port': 8888,
                'destination_host': 'usermanagement.adobe.io',
                'pass_through': True
            }
        self.config.update(config)
        self.server = None
        self.server_thread = None
        
        
    def run(self):
        '''
        Starts the server given the proxy configuration.
        '''
        self.server = TestServer((self.config['proxy_host'], self.config['proxy_port']), TestServerHandler, config=self.config)
        self.server_thread = threading.Thread(target = self.server.serve_forever())
        self.server_thread.daemon = True
        
    def stop(self):
        '''
        Stops the service by shutting down the HTTP server
        '''
        self.server.shutdown()
        
class TestServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, config=None, bind_and_activate=True):
        '''
        Initialize the test server. TestServer basically subclasses HTTPServer
        to keep track of the configuration context, as the base HTTPServer class
        takes in a class for the handler rather than an instance, and there is
        no direct way for the handler to keep the context.
        '''
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.config = config
        
class TestServerHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_GET(self):
        '''
        
        '''
        url = 'https://' + self.server.config['destination_host'] + self.path
        req_headers = self.headers.dict
        req_headers['host'] = self.server.config['destination_host']
        cassette_file = self.server.config['get_filename']
        record_mode = 'all' if self.server.config['pass_through'] else 'none'
        test_vcr = vcr.VCR(
            record_mode=record_mode,
            decode_compressed_response=True
        )
        with test_vcr.use_cassette(cassette_file) as cass:
            response = requests.get(url, headers=req_headers)
            cass.dirty = True
            
        self._set_headers()
        self.wfile.write(response.content)
        
    def do_POST(self):
        url = 'https://' + self.server.config['destination_host'] + self.path
        req_headers = self.headers.dict
        req_headers['host'] = self.server.config['destination_host']
        cassette_file = self.server.config['post_filename']
        record_mode = 'all' if self.server.config['pass_through'] else 'none'
        test_vcr = vcr.VCR(
            record_mode=record_mode,
            decode_compressed_response=True
        )
        with test_vcr.use_cassette(cassette_file) as cass:
            response = requests.get(url, headers=req_headers)
            cass.dirty = True
            
        self._set_headers()
        self.wfile.write(response.content)
