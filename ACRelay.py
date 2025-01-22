import socket
import threading
import os
import time

# Global variables
clients = []
relays = []

# Function to handle messages from clients or relays
def handle_connection(conn, is_relay=False):
    while True:
        try:
            message = conn.recv(1024)
            if not message:
                break

            # Relay the message to all other clients and relays
            for client in clients:
                if client != conn:
                    try:
                        client.sendall(message)
                    except:
                        clients.remove(client)
            for relay in relays:
                if relay != conn:
                    try:
                        relay.sendall(message)
                    except:
                        relays.remove(relay)
        except:
            break

    # Remove the connection from the appropriate list
    if is_relay:
        relays.remove(conn)
    else:
        clients.remove(conn)
    conn.close()

# Function to accept incoming client connections
def accept_clients(server_socket):
    while True:
        client_conn, client_addr = server_socket.accept()
        clients.append(client_conn)
        threading.Thread(target=handle_connection, args=(client_conn, False)).start()

# Function to connect to another AChat relay
def connect_to_relay(relay_host, relay_port):
    try:
        relay_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        relay_conn.connect((relay_host, relay_port))
        relays.append(relay_conn)
        threading.Thread(target=handle_connection, args=(relay_conn, True)).start()
        print(f"Connected to relay: {relay_host}:{relay_port}")
    except Exception as e:
        print(f"Failed to connect to relay {relay_host}:{relay_port}: {e}")

# Function to generate a new relay script
def generate_relay_script(parent_host, parent_port):
    script_content = f"""import socket
import threading

clients = []
relays = []

def handle_connection(conn, is_relay=False):
    while True:
        try:
            message = conn.recv(1024)
            if not message:
                break
            for client in clients:
                if client != conn:
                    try:
                        client.sendall(message)
                    except:
                        clients.remove(client)
            for relay in relays:
                if relay != conn:
                    try:
                        relay.sendall(message)
                    except:
                        relays.remove(relay)
        except:
            break
    if is_relay:
        relays.remove(conn)
    else:
        clients.remove(conn)
    conn.close()

def accept_clients(server_socket):
    while True:
        client_conn, client_addr = server_socket.accept()
        clients.append(client_conn)
        threading.Thread(target=handle_connection, args=(client_conn, False)).start()

def connect_to_relay(relay_host, relay_port):
    try:
        relay_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        relay_conn.connect((relay_host, relay_port))
        relays.append(relay_conn)
        threading.Thread(target=handle_connection, args=(relay_conn, True)).start()
        print(f"Connected to relay: {{relay_host}}:{{relay_port}}")
    except Exception as e:
        print(f"Failed to connect to relay {{relay_host}}:{{relay_port}}: {{e}}")

def start_relay_server(host, port, parent_host, parent_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"AChat Relay running on {{host}}:{{port}}")
    threading.Thread(target=accept_clients, args=(server_socket,)).start()
    connect_to_relay(parent_host, parent_port)

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 9000
    PARENT_HOST = "{parent_host}"
    PARENT_PORT = {parent_port}
    start_relay_server(HOST, PORT, PARENT_HOST, PARENT_PORT)
"""
    script_name = f"relay_{int(time.time())}.py"
    with open(script_name, "w") as f:
        f.write(script_content)
    print(f"Generated relay script: {script_name}")

# Function to generate a chat room GUI script
def generate_chat_gui_script(relay_host, relay_port):
    script_content = f"""import socket
import threading
from tkinter import Tk, Text, Button, Scrollbar, Entry, END

class ChatRoom:
    def __init__(self, host, port):
        self.root = Tk()
        self.root.title("AChat Room")
        self.chat_log = Text(self.root, state='disabled', width=50, height=20, wrap='word')
        self.chat_log.pack(padx=10, pady=10)
        
        self.scrollbar = Scrollbar(self.root, command=self.chat_log.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.chat_log['yscrollcommand'] = self.scrollbar.set
        
        self.message_entry = Entry(self.root, width=40)
        self.message_entry.pack(padx=10, pady=5)
        self.message_entry.bind('<Return>', lambda event: self.send_message())
        
        self.send_button = Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)
        
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_relay()
        
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.root.mainloop()

    def connect_to_relay(self):
        try:
            self.socket.connect((self.host, self.port))
            self.append_message("Connected to relay.")
        except Exception as e:
            self.append_message(f"Failed to connect to relay: {{e}}")

    def receive_messages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message:
                    self.append_message(message)
            except:
                break

    def send_message(self):
        message = self.message_entry.get()
        if message:
            try:
                self.socket.sendall(message.encode('utf-8'))
                self.append_message(f"You: {{message}}")
                self.message_entry.delete(0, END)
            except Exception as e:
                self.append_message(f"Failed to send message: {{e}}")

    def append_message(self, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, message + "\\n")
        self.chat_log.config(state='disabled')
        self.chat_log.see(END)

if __name__ == "__main__":
    HOST = "{relay_host}"
    PORT = {relay_port}
    ChatRoom(HOST, PORT)
"""
    script_name = f"chat_gui_{int(time.time())}.py"
    with open(script_name, "w") as f:
        f.write(script_content)
    print(f"Generated chat room GUI script: {script_name}")

# Start the relay server
def start_relay_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"AChat Relay running on {host}:{port}")

    # Start thread to accept client connections
    threading.Thread(target=accept_clients, args=(server_socket,)).start()

if __name__ == "__main__":
    HOST = input("Enter host IP (default: 0.0.0.0): ") or "0.0.0.0"
    PORT = int(input("Enter host port (default: 9000): ") or 9000)
    PARENT_HOST = input("Enter parent relay host (leave empty if root): ")
    PARENT_PORT = int(input("Enter parent relay port (leave empty if root): ") or 0)

    if PARENT_HOST:
        connect_to_relay(PARENT_HOST, PARENT_PORT)

    start_relay_server(HOST, PORT)

    # Generate additional scripts
    while True:
        generate = input("Generate relay or chat room script? (relay/chat/none): ").lower()
        if generate == "relay":
            generate_relay_script(HOST, PORT)
        elif generate == "chat":
            generate_chat_gui_script(HOST, PORT)
        else:
            break
