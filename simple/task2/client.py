#!/usr/bin/python2
import logging
import sys
from socket import AF_INET, SOCK_STREAM, socket
from argparse import ArgumentParser
import os

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

DEFAULT_BUFF_SIZE = 1024*1024


def main(args):
    if args.file is not None:
        handle_upload(args.file, args.addr, args.port)
    elif args.list:
        handle_list(args.addr, args.port)
    elif args.dl is not None:
        handle_dl(args.dl, args.addr, args.port)
    else:
        LOG.info("No work to do, specify some arguments. Terminating...")


def handle_list(addr, port):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((addr, port))
    s.send("2^^")
    msg = s.recv(DEFAULT_BUFF_SIZE)
    LOG.info("Listing recieved. Printing files...")
    result = eval(msg)
    if len(result) > 0:
        for i in eval(msg):
            print(i)
    else:
        LOG.info("There are no files.")
    s.close()
    LOG.info("Work finished. Terminating...")


def handle_upload(file, addr, port):
    try:
        with open(file, "rb") as f:
            file_buffer = f.read()
        file_size = os.path.getsize(args.file)
    except IOError:
        LOG.info("File not found. Terminating ...")
        sys.exit(1)
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((addr, port))
    msg = "1^^%s^^%s" % (file, file_size)
    s.send(msg)
    msg = s.recv(1024 * 1024)
    if msg == "1":
        s.sendall(file_buffer)
        LOG.info("File sent successfully.")
    else:
        LOG.info(msg)
    s.close()
    LOG.info("Closing Client and socket.")


def handle_dl(f_name, addr, port):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((addr, port))
    msg = "3^^%s" % f_name
    s.send(msg)
    msg = s.recv(DEFAULT_BUFF_SIZE)
    if msg == "1":
        msg = ""
        while 1:
            block = s.recv(DEFAULT_BUFF_SIZE)
            if len(block) <= 0:
                break
            msg += block

        with open(f_name, "wb") as f:
            f.write(msg)
        LOG.info("File created.")
    else:
        LOG.info(msg)

    LOG.info("Terminating & closing sockets...")
    s.close()


if __name__=="__main__":
    parser = ArgumentParser(description="Client for uploading/listing files.")
    parser.add_argument('-f', '--file', help="File to be uploaded.")
    parser.add_argument('-l', '--list', help="List all the files in the server.", action='store_true')
    parser.add_argument('-a', '--addr', help="Address of the host. Default localhost.", default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen on port.", default=7778, type=int)
    parser.add_argument('-d', '--dl', help="Download specified file.")
    args = parser.parse_args()
    main(args)