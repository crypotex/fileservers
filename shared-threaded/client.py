import socket
import os
import logging
import json

from argparse import ArgumentParser


BUFFER_SIZE = 1024*1024
MAX_PDU_SIZE = 200*1024*1024

FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class Client:
    # Always increment id by one for identifier, so it wouldn't break the code
    identifier = {0: "Disconnect", 1: "Upload", 2: "List Files", 3: "Download"}

    def __init__(self, args):
        LOG.info("Client started. ")
        self.saddr = args.addr
        self.port = args.port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((args.addr, args.port))
            LOG.info("Connected to server.")
            self.min_id = min(self.identifier.keys())
            self.max_id = max(self.identifier.keys())
            self.interactive_shell()
        except socket.error as soe:
            LOG.info("Socket error with msg: %s." % soe)
            LOG.info("Closing client.")
            self.sock.close()


    def interactive_shell(self):
        print("Welcome!")
        try:
            while True:
                welcome_msg = "Press 1 for Upload, 2 for list of files and 3 for download, 0 to disconnect"
                inp = None
                while inp is None:
                    try:
                        print(welcome_msg)
                        inp = int(raw_input("Insert [0,1,2,3] only: \n"))
                        if inp < self.min_id or inp > self.max_id:
                            inp = None
                    except ValueError as ve:
                        print("Please only insert one integer, nothing else.")
                try:
                    LOG.info("Client chose %s(%s), starting request." % (inp, self.identifier[inp]))
                except KeyError:
                    LOG.info("Keyerror, should never happen, if correctly filled identifier dictionary...Shutting down")
                    break

                # Now handle request-response
                if inp == 0:
                    self.sock.send("0")
                    break
                elif inp == 1:
                    self.handle_upload()
                elif inp == 2:
                    self.handle_list()
                elif inp == 3:
                    self.handle_dl()
                else:
                    LOG.info("Unimplemented functionality, identifier %s." % inp)
        except KeyboardInterrupt:
            LOG.info("Keyboard Interrupt called.")
        print("Closing client...")
        self.sock.close()
        LOG.info("Closed client socket... Bye!")

    def handle_list(self):
        self.sock.send("2^^")
        msg = self.sock.recv(BUFFER_SIZE)
        result = json.loads(msg)
        if len(result) > 0:
            print("Files are:")
            for i in result:
                print(i)
        else:
            print("There are no files.")

    def handle_dl(self):
        f_name = raw_input("Specify file name to download from server: \n")
        msg = "3^^%s" % f_name
        self.sock.send(msg)
        msg = self.sock.recv(BUFFER_SIZE)
        if msg == "1":
            msg = ""
            while 1:
                block = self.sock.recv(BUFFER_SIZE)
                msg += block
                if len(block) < BUFFER_SIZE:
                    break

            with open(f_name, "wb") as f:
                f.write(msg)
            print("File created successfully.")
        else:
            print(msg)

    def handle_upload(self):
        fname = raw_input("Specify file to upload (Abs/relative path works): ")
        try:
            with open(fname, "rb") as f:
                file_buffer = f.read()
            file_size = os.path.getsize(fname)
        except IOError:
            print("File not found. ")
            return

        msg = "1^^%s^^%s" % (fname, file_size)
        self.sock.send(msg)
        msg = self.sock.recv(BUFFER_SIZE)
        if msg == "1":
            self.sock.sendall(file_buffer)
            self.sock.send("")
            print("File sent successfully.")
        else:
            print(msg)


if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument('-l', '--addr', help="Listen address of server. Default localhost.",  default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen port of server.", default=19191, type=int)
    args = parser.parse_args()
    s = Client(args)

