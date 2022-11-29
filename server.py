#!/usr/bin/env python3
"""Server script for puffy."""
import socket
import time
import sys
import threading

# constants
HOST = '0.0.0.0'
PORT = 12211

# global vars
clients = []
nicknames = []
threads = []

running = True


def init():
    global server
    # socket init
    print(f"Binding to port {PORT} on {HOST}...", end=' ')
    while running:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((HOST, PORT))
            server.listen()
            break  # connected
        except OSError:
            print("ERROR: Port already taken. Waiting...")
            time.sleep(1)
    print("DONE")

    # try:
    #     listen()
    # except KeyboardInterrupt:
    #     close()
    listen()
    # except Exception as e:
    #     print(e)
    #     server.close()


def close():
    global running

    print("Received KeyboardInterrupt. Stopping...")
    broadcast("<SERVER_CLOSED>".encode())
    print("Disconnecting clients...", end=' ')
    for client in clients:
        disconnect(client, announce=False)
    print("DONE")
    print("Stopping threads...", end=' ')
    # for thread in threads:
    #     thread
    print("DONE")
    print("Stopping server...", end=' ')
    server.close()
    print("DONE")
    print("Exiting...")
    running = False
    sys.exit()


def disconnect(client, announce=True):
    index = clients.index(client)
    nickname = nicknames[index]
    print(f"Disconnecting {nickname}...", end=' ')
    clients.remove(client)
    client.sendall("<SERVER_CLOSED>".encode())
    client.close()
    print("DONE")
    if announce:
        broadcast(f"{nickname} disconnected.".encode())


def broadcast(message, encode=True):
    print(f"Broadcasting: {message}")
    for client in clients:
        client.sendall(message)


def handle(client):
    while running:
        try:
            index = clients.index(client)
            nickname = nicknames[index]
            received = client.recv(4096).decode()
            message = f"{nickname}: {received}".encode()

            if received == "":
                print(f"Message empty, kicking client...", end=' ')
                disconnect(client)
            else:
                broadcast(message)
        except Exception as exc:
            if client in clients:
                print(f"An exception occured: {exc}, disconnecting client.")
                disconnect(client)
            else:
                print("Can't disconnect: client not connected.")
            # # if error occured, remove client from list
            # index = clients.index(client)
            # nickname = nicknames[index]
            # # print(f"{nickname} disconnected.")
            # broadcast(f"{nickname} disconnected.".encode())
            # clients.remove(client)
            # client.close()
            break


def listen():
    print("Listening...")
    while running:
        # wait for connection and accept it
        client, (ip, port) = server.accept()
        print(f"Accepted connection from: {ip}:{port}")

        # request nickname
        client.sendall("<NICKNAME>".encode('utf-8'))
        nickname = client.recv(4096).decode()
        nicknames.append(nickname)
        clients.append(client)

        # broadcast join
        print(f"with nick: {nickname}")
        broadcast(f"{nickname} joined!".encode())
        client.sendall('Connected!'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.daemon = True
        thread.start()
        threads.append(thread)


if __name__ == "__main__":
    init()
