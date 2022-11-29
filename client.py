#!/usr/bin/env python3
"""Client script for puffy."""

import socket
import time
import threading
import tqdm
import os
# import random as rn

# constants
BUFFER_SIZE = 4096
# HOST = '127.0.0.1'
# PORT = 12211

print("Enter server IP followed by PORT.")
while True:
    try:
        # HOST, PORT = input("IP:PORT > ").split(':')
        HOST, PORT = "0.0.0.0", 12211

    except (ValueError, IndexError):
        print(f"Invalid format.")

    else:
        break

# choose nickname
nickname = input("nickname: ")
# nickname = str(rn.randint(0, 100000))
connected = False


def init():
    # connect to server
    global client, connected
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST, PORT))
        except ConnectionRefusedError as exc:
            print(f"ERROR: {exc}; Waiting...")
            time.sleep(1)
        else:
            receive_thread = threading.Thread(target=receive)
            receive_thread.daemon = True
            receive_thread.start()

            write_thread = threading.Thread(target=send)
            write_thread.daemon = True
            write_thread.start()

            connected = True
            break


def receive():
    global connected
    while True:
        try:
            message = client.recv(BUFFER_SIZE).decode()
            if message == '<NICKNAME>':
                client.sendall(nickname.encode())
            elif message == '<SERVER_CLOSED>':
                print("Server closed. Exiting...")
                client.close()
                connected = False
                # sys.exit()
            elif message == '':
                pass
            else:
                print(message)
        except OSError as exc:
            print(f"Lost connection to the server.\nDetails: {exc}\nExiting...")
            # print(f"an error occured. {exc}")
            client.close()
            connected = False
            break


def send():
    try:
        while True:
            message = input()
            # print(message)
            client.sendall(message.encode())
    except Exception as exc:
        print(f"Couldn't send message: {exc}")


if __name__ == "__main__":
    init()

while connected:
    time.sleep(1)
