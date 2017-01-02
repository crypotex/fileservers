import socket
import os
import threading
import logging
import json

from argparse import ArgumentParser


BUFFER_SIZE = 1024*1024
MAX_PDU_SIZE = 200*1024*1024

FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class Server:
    def __init__(self, args):
        LOG.info("Server Started.")
        self.socket = self.__socket_init(args.laddr, args.port)
        self.clients = {}
        self.dumpdir = args.dump
        if not os.path.isdir("./%s" % args.dump):
            os.makedirs("./%s" % args.dump)
        self.main_threader()

    @staticmethod
    def __socket_init(server_ip, port):
        """ Socket Initialization """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((server_ip, port))
        except socket.error as e:
            LOG.error("Socket error: %s" % str(e))
            exit(1)
        LOG.info("Socket initialized")
        return s

    def main_threader(self):
        self.socket.listen(5)
        while True:
            try:
                client, address = self.socket.accept()
                client.settimeout(7200)
                threading.Thread(target=self.run_client_thread, args=(client, address)).start()
                LOG.info("Current Clients: %s" % str(self.clients))
            except KeyboardInterrupt:
                LOG.exception('Ctrl+C - terminating server')
                break
        self.socket.close()

    def run_client_thread(self, client, address):
        LOG.info("New thread initialized with :%s and %s" % (str(client), address))
        while True:
            try:
                msg = client.recv(BUFFER_SIZE).split("^^")
                LOG.info("New request: %s." % msg)
                if msg[0] == "0":
                    LOG.info("Client disconnecting.")
                    break
                elif msg[0] == "1":
                    if int(msg[2]) > MAX_PDU_SIZE:
                        client.send("File is too big, will not upload.")
                        LOG.info("Recieved file was too big, terminating.")
                    else:
                        f_name = "%s/%s" % (self.dumpdir, msg[1])
                        if not os.path.exists(f_name):
                            try:
                                client.send("1")
                                msg = ""
                                while 1:
                                    block = client.recv(BUFFER_SIZE)
                                    msg += block
                                    if len(block) < BUFFER_SIZE:
                                        break

                                with open(f_name, "wb") as f:
                                    f.write(msg)
                            except IOError:
                                del msg
                                LOG.error("Broken pipe, terminating connection.")
                                break

                            LOG.info("File created.")
                        else:
                            client.send("File exists on the Server.")
                            LOG.info("File exists, not going to create a file.")

                elif msg[0] == "2":
                    msg = json.dumps(os.listdir(self.dumpdir))
                    client.sendall(msg)
                    LOG.info("Sent response to client with dump dir contents.")

                elif msg[0] == "3":
                    f_name = "%s/%s" % (self.dumpdir, msg[1])
                    try:
                        with open(f_name, "rb") as f:
                            client.send("1")
                            client.sendall(f.read())
                        LOG.info("Client downloaded file %s successfully." % f_name)
                    except IOError:
                        LOG.error("There is no such file: %s." % f_name)
                        client.send("No such file on server.")
                else:
                    LOG.error("Client sent a unrecognized control message: %s." % msg)
                    break

            except socket.error as soe:
                LOG.info("Connection error. Closing client %s." % address)
                break
        if client is not None:
            try:
                client.close()
            except socket.error:
                LOG.info("Client %s disconnected." % address)


if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument('-l', '--laddr', help="Listen address. Default localhost.",  default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=19191, type=int)
    parser.add_argument('-d', '--dump', help="Folder as dump dir.", default="dump")
    args = parser.parse_args()
    s = Server(args)

