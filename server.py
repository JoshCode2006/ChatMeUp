import socket
import threading

HOST = "localhost"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []


def package_list(entry):
    packaged = ""
    for item in entry:
        packaged += f"{item}&*"
    return packaged


def broadcast(name, message):
    if name == "ALL":
        for client in clients:
            client.send(message)
    else:
        index = nicknames.index(name)
        for client in clients:
            if client != clients[index]:
                client.send(message)


def handle_connection(client):
    stop = False
    while not stop:
        try:
            incoming = client.recv(1024).decode('utf-8').split("&*")
            message = incoming[1].encode('utf-8')
            name = incoming[0]
            broadcast(name, message)
        except:
            index = clients.index(client)
            clients.remove(client)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast("ALL", package_list(nicknames).encode('utf-8'))
            print(f"{nickname} left the chat")
            stop = True


def main():
    print("Server is running")
    while True:
        client, addr = server.accept()
        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        print(f"{nickname} joined the chat.")
        broadcast("ALL", package_list(nicknames).encode('utf-8'))
        thread = threading.Thread(target=handle_connection, args=(client,))
        thread.start()


if __name__ == "__main__":
    main()
