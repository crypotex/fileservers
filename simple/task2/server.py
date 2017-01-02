#!/usr/bin/python2
import logging
from socket import AF_INET, SOCK_STREAM, socket
from argparse import ArgumentParser
import sys
import os.path

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()

DEFAULT_BUFF_SIZE = 1024*1024
DEFAULT_MAX_PDU = DEFAULT_BUFF_SIZE*40


def main(args):
    LOG.info("Starting server on Host: %s and Socket: %d." % (args.laddr, args.port))
    __server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        __server_socket.bind((args.laddr, args.port))
    except:
        LOG.info("IP/PORT in use. Terminating...")
        sys.exit(1)
    __server_socket.listen(1)

    if not os.path.exists(args.dump):
        os.mkdir(args.dump)

    while True:
        try:
            client_socket, client_addr = __server_socket.accept()
            msg = client_socket.recv(DEFAULT_BUFF_SIZE).split("^^")
            if msg[0] == "1":
                if int(msg[2]) > DEFAULT_MAX_PDU:
                    client_socket.send("File is too big, will not upload.")
                    LOG.info("Recieved file was too big, terminating.")
                else:
                    f_name = "%s/%s" % (args.dump, msg[1])
                    if not os.path.exists(f_name):
                        try:
                            client_socket.send("1")
                            msg = ""
                            while 1:
                                block = client_socket.recv(DEFAULT_BUFF_SIZE)
                                if len(block) <= 0:
                                    break
                                msg += block

                            with open(f_name, "wb") as f:
                                f.write(msg)
                        except IOError:
                            del msg
                            LOG.error("Broken pipe, terminating connection.")
                            client_socket.close()

                        LOG.info("File created.")
                    else:
                        client_socket.send("File exists on the Server.")
                        LOG.info("File exists, not going to create a file.")
            elif msg[0] == "2":
                msg = str(os.listdir(args.dump))
                client_socket.sendall(msg)
            elif msg[0] == "3":
                f_name = "%s/%s" % (args.dump, msg[1])
                try:
                    with open(f_name, "rb") as f:
                        client_socket.send("1")
                        client_socket.sendall(f.read())
                except IOError:
                    LOG.error("There is no such file: %s." % f_name)
                    client_socket.send("No such file on server.")
            else:
                LOG.error("Client sent a unrecognized control message: %s." % msg)

            LOG.info("Client handled. Closing client socket.")
            client_socket.close()
        except KeyboardInterrupt:
            LOG.info("KBE: Terminating server...")
            break


if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument('-l', '--laddr', help="Listen address. Default localhost.",  default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=7778, type=int)
    parser.add_argument('-d', '--dump', help="Folder as dump dir.", default="dump")
    args = parser.parse_args()
    main(args)


