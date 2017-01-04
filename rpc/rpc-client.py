from argparse import ArgumentParser
from xmlrpclib import ServerProxy, Fault
import os


if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument('-l', '--addr', help="Listen address of server. Default localhost.",  default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Listen port of server.", default=19191, type=int)
    args = parser.parse_args()

    server = (args.addr, int(args.port))
    try:
        proxy = ServerProxy("http://%s:%d" % server)
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print("Some error: %s. Terminating..." % e)
        exit(1)

    methods = [i[:-5] for i in filter(lambda x: 'system.' not in x, proxy.system.listMethods())]
    welcome = "Insert the command you want: %s." % methods
    print(welcome)

    while True:
        try:
            inp = raw_input("Specify the command: ")
            if inp.startswith("list"):
                msg = proxy.list_file()
                if msg:
                    print(msg)
                else:
                    print("No files on server!")

            elif inp.startswith("upload"):
                fname = raw_input("Specify file name (abs/relative): ")
                try:
                    with open(fname, 'rb') as f:
                        file_buffer = f.read()

                    if proxy.upload_file(os.path.basename(fname), file_buffer):
                        print("File upload successful!")
                    else:
                        print("File upload failed!")
                except IOError as ioe:
                    print("IOError: %s." % ioe)

            elif inp.startswith("download"):
                fname = raw_input("Specify the name of the file: ")
                buffer = proxy.download_file(fname)
                if buffer:
                    try:
                        with open(fname, "wb") as f:
                            f.write(buffer)
                        print("File downloaded.")
                    except IOError as ioe:
                        print("IOError: %s." % ioe)
                else:
                    print("No such file!")

            elif inp.startswith("delete"):
                fname = raw_input("Specify the file to delete: ")
                if proxy.delete_file(fname):
                    print("File deleted.")
                else:
                    print("File not deleted. No such file.")

            elif inp.startswith("rename"):
                old = raw_input("Specify the file name to be changed: ")
                new = raw_input("Specify the new file name: ")
                if proxy.rename_file(old, new):
                    print("File renamed!")
                else:
                    print("No such file. ")

            else:
                print("Unknown command - %s." % welcome)


        except KeyboardInterrupt:
            print("Terminating...(KBE)")
            break
        except Fault as Faust:
            print("Some unknown error: %s." % Faust)


