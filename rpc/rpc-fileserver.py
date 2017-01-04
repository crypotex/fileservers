import socket
import os
from SimpleXMLRPCServer import SimpleXMLRPCServer

from argparse import ArgumentParser


class FileServer:
    def __init__(self, dumpdir):
        self.dumpdir = args.dump
        if not os.path.isdir("./%s" % dumpdir):
            os.makedirs("./%s" % dumpdir)

    def list_file(self):
        return os.listdir(self.dumpdir)

    def upload_file(self, filename, buffer):
        fname = "%s/%s" % (self.dumpdir, filename)
        try:
            with open(fname, "wb") as f:
                f.write(buffer)
        except IOError:
            return False
        return True

    def download_file(self, fname):
        fname = "%s/%s" % (self.dumpdir, fname)
        try:
            with open(fname, 'rb') as f:
                return f.read()
        except IOError:
            return False

    def delete_file(self, fname):
        fname = "%s/%s" % (self.dumpdir, fname)
        try:
            os.remove(fname)
            return True
        except OSError:
            return False

    def rename_file(self, fname, new_fname):
        old = "%s/%s" % (self.dumpdir, fname)
        new = "%s/%s" % (self.dumpdir, new_fname)
        try:
            os.rename(old, new)
            return True
        except OSError:
            return False


if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument('-l', '--laddr', help="Listen address. Default localhost.",  default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=19191, type=int)
    parser.add_argument('-d', '--dump', help="Folder as dump dir.", default="dump")
    args = parser.parse_args()
    fs = FileServer(args.dump)

    server_sock = (args.laddr, args.port)

    # Create XML_RPC Server
    server = SimpleXMLRPCServer(server_sock)
    server.register_introspection_functions()
    # Register instance
    server.register_instance(fs)

    try:
        print("Starting RPC-Server.")
        server.serve_forever()
    except KeyboardInterrupt:
        print('KBE, terminating ... ')
    finally:
        server.shutdown()
        server.server_close()
    print("Terminated.")
