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
import time
import gzip
import StringIO
import logging

class UserSyncTestService:
    def __init__(self, config):
        '''
        Initializes the test service given the configuration, but does not start the service.
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
        Starts the service by starting the test server on another thread.
        '''
        record_mode = 'all' if self.config['pass_through'] else 'none'
        recorder = vcr.VCR(
            record_mode=record_mode,
            match_on=('method', 'scheme', 'host', 'port', 'path', 'query', 'body'),
            decode_compressed_response=True
        )
        cassette = recorder.use_cassette(self.config['cassette_filename'])
        cassette.__enter__()

        self.server = UserSyncTestServer((self.config['proxy_host'], self.config['proxy_port']), UserSyncTestServerHandler, config=self.config, cassette=cassette)
        self.server_thread = threading.Thread(target = self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        # give the server some time to startup
        time.sleep(1)
        
    def stop(self):
        '''
        Stops the service by shutting down the test server, and waiting for the test server thread to end.
        '''
        self.server.shutdown()
        self.server_thread.join()
        self.server.cassette.__exit__()
        
class UserSyncTestServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, config=None, bind_and_activate=True, cassette=None):
        '''
        Initialize the test server. TestServer basically subclasses HTTPServer to keep track of the configuration
        context, as the base HTTPServer class takes in a class for the handler rather than an instance, and there is no
        direct way for the handler to keep the context.
        '''
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.config = config
        self.cassette = cassette
        self.logger = logging.getLogger('user-sync-test-server')

class UserSyncTestServerHandler(BaseHTTPRequestHandler):
    def _prepare_request(self):
        '''
        Builds and preprocesses variables needed for the http proxy target request, including the url, request headers,
        and the vcr object.
        :rtype: str, dict(str,any), vcr.VCR
        '''
        url = 'https://' + self.server.config['destination_host'] + self.path
        request_headers = self.headers.dict
        request_headers['host'] = self.server.config['destination_host']
        return url, request_headers

    def _send_response(self, response):
        '''
        Sends the response to the proxy client. If the content-encoding is gzip, recompress it before sending it to
        the client, and update the header content-length. Data is sent via chunking or in a single block, depnding on
        the delivery type of the original response (though effectively it is always sent in one chunk)
        :param cassette_filename: 
        '''
        # process headers before passing them along. Some of these entries may need to be updated before we let them go.
        headers = response.headers.copy()
        if not 'Accept-Encoding' in headers:
            headers['Accept-Encoding'] = 'identity'

        # re-encode the content before passing this along, if needed.
        output = response.content
        if 'Content-Encoding' in response.headers and response.headers['Content-Encoding'] == 'gzip':
            buffer = StringIO.StringIO()
            with gzip.GzipFile(fileobj=buffer, mode="w") as f:
                f.write(output)
            output = buffer.getvalue()
            headers['Content-Length'] = '%d' % len(output)

        # pass along response headers
        self.send_response(response.status_code)
        for header in headers:
            self.send_header(header, headers[header])
        self.end_headers()

        # handle chunking
        if 'Transfer-Encoding' in response.headers and response.headers['Transfer-Encoding'].lower() == 'chunked':
            self.wfile.write('%X\r\n%s\r\n' % (len(output), output))
            self.wfile.write('0\r\n\r\n')
        else:
            self.wfile.write(output)

    def do_GET(self):
        '''
        Handles get request via proxy through vcr. The response is obtained by either using the get cassette file, or by
        passing along the request to the live server, depending whether the test server is in record mode.
        '''
        url, request_headers = self._prepare_request()
        response = requests.get(url, headers=request_headers)
        self.server.cassette.dirty = True
        self._send_response(response)

    def do_POST(self):
        '''
        Same as do_GET, but executes post using a post cassette file.
        '''
        url, request_headers = self._prepare_request()
        data = self.rfile.read(int(self.headers['Content-Length']))
        response = requests.post(url, headers=request_headers, data=data)
        self.server.cassette.dirty = True
        self._send_response(response)

    def log_message(self, format, *args):
        self.server.logger.debug("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))