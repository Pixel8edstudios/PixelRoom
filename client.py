import socket
import sys
import random
import time
import threading
from _thread import *
while_loop = True
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
default_ip = socket.gethostname()
# client_commands = ["/exit"]
bind_ip_address = default_ip
server_keywords = ['username', 'server_kick']
"""
Default Port uses a random generator for the ports because I was sick of changing the code every time to test two clients at once,
but it's also so if that someone wants to, they can have multiple clients on it for whatever reason.
Later, I might make some sort of switch for the generator to have it be manually defined by user.

Another Idea is to make a verifier to make sure that no two ports are bound to the same place, but it's such a long range that I highly
doubt that it would ever come up. Might bring it up very very very late into development.
"""
#TODO: Make the defaults manually defineable (and make them persistent, maybe by having it stored somewhere like a .txt)
#TODO: Make it possible to adjust randint range through pre-start console
default_port = random.randint(49152, 65535)
bind_port = default_port
bind_address = (bind_ip_address, bind_port)
server_ip = socket.gethostname()
server_port = 5556
server_address = (server_ip, server_port)
#TODO: Have client attempt to establish connection using connect IP and Port before starting chat room to let client know if its worth it.
#TODO: This should be tackled earlier rather than later, but make the server_ip and server_port persistently customizable from console.
while while_loop == True:
    print(f"""
    Client Pre-start console:
    1) Configure Socket Binding (Current Bind Address: {bind_address} )
    2) Connect to Server (Connecting to: {server_address})
    3) Shut down Client
    """)
    Pre_start_console = input("(Pre-start)>>> ")
    if Pre_start_console == "1":
        print (f"""
        1) Customize IP Binding (default: {default_ip}, current: {bind_ip_address})
        2) Customize Port Binding (default: {default_port} current: {bind_port})
        3) Back
        """)
        Pre_start_console = input("(Pre-start)>>> ")
        if Pre_start_console == "1":
            ip_address = input("(Bind-IP)>>> ")
            print(f"Bind address changed to {bind_ip_address} ")
        if Pre_start_console == "2":
            port = input("(Bind-Port)>>> ")
            print(f"Bind port changed to {bind_port}")
        if Pre_start_console == "3":
            continue
    if Pre_start_console == "2":
        break
    if Pre_start_console == "3":
        print("Exiting")
        sys.exit()
try:
    bind_address = (bind_ip_address, bind_port)
    client.bind(bind_address)
    print (f"Client bound at {bind_address}.")
except:
    print(f"Cannot connect to {bind_address}! Please reconfigure client.")
    sys.exit()
#TODO: Make it so that if the client can't connect, the client goes back to the pre-start console.
try:
    client.connect(server_address)
    print(f"Connected to server at {server_address}")
except:
    print("The client cannot connect to the server.")
    sys.exit()
#TODO: Have a separate thread that sends connection verification to the server every couple of seconds. 
#TODO: Make pre-start console accessible from chat-room interface to make it, uh, no longer a pre-start console.
def recv():
    while while_loop == True:
        global username_given
        server_message = client.recv(2048)
        decoded_server_message = server_message.decode('utf-8')
        if decoded_server_message in server_keywords:
            if decoded_server_message == "username":
                while while_loop == True:
                    username_in_use = 0
                    print("Server is requesting you select a username. Select a username? (Y/n)")
                    username_confirm = input("(Confirm-Username)>>> ")
                    if username_confirm == "Y":
                        if username_in_use == 0:
                            print("What will your username be?")
                        else:
                            print("What will your username be? (Previous username was taken.)")
                        username = input("(Username)>>> ")
                        client.sendall(bytes(username, "utf-8"))
                        username_in_use += 1
                        if decoded_server_message == "username_taken":
                            print(f'Sorry, {username} is either reserved or already taken by someone online.')
                            break
                        else:
                            print(f"Using {username}.")
                            username_given = True
                            break
                    elif username_confirm == "n":
                        print("Noted. Using IP address as default.")
                        client.sendall(bytes(default_ip, 'utf-8'))
                        username_given = True
                        break
                    else:
                        print("Not a valid response. Please respond with\"Y\" or \"n\".")
            # Don't remove this kick part. It won't result in you bypassing kick, it just guarantees that you won't have a client-side recognition of the kick.
            if decoded_server_message == "server_kick":
                #TODO: Make the crash more "pretty" for the user when they are kicked.
                #TODO: After a kick, don't just crash the client, that's a bit too much power for a server to have over a client.
                print("The server has kicked you.")
                client.shutdown(2)
                client.close()
                sys.exit()
        else:
            if decoded_server_message:
                print(server_message.decode('utf-8'))
rt = threading.Thread(target=recv, args=())
def send():
    try:
        username_check = client.recv(2048)
        username_check_decoded = username_check.decode('utf-8')
        if username_check_decoded == 'username_chosen':
            while while_loop == True:
            #For now, this is the way that it has to be so the input console signal doesn't get scrambled up. Maybe someday, i'll find a way to do
            # global message_to_send
                message_to_send = input(">>> ")
            # command_check(message_to_send)
        # if message_to_send != client_commands:
                client.sendall(bytes(message_to_send, "utf-8"))
    except:
        print("Cannot send message, connection closed.")
        pass
        client.shutdown(2)
        pass
        client.close()
        pass
        sys.exit()
#NOTE: I will eventually need this code once I start implementing commands.
# def command_check(command):
#    if command in client_commands:
st = threading.Thread(target=send, args=())
time.sleep(1)
rt.start()
st.start()
st.join()
rt.join()