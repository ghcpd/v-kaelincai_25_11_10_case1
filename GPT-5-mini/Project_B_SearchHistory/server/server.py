from http.server import HTTPServer, SimpleHTTPRequestHandler
import os, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src')
os.chdir(ROOT)

class C(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stdout.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format%args))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8002'))
    httpd = HTTPServer(('127.0.0.1', port), C)
    print('Serving at http://127.0.0.1:%d' % port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Stopping')
        httpd.server_close()
