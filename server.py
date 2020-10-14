import socket
import sys
import time
from time import sleep
uptime_start = time.perf_counter()
import random
from _thread import *
ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 5556
while_loop = True
client_ip_list = []
username_list = []
kicked_clients = []
muted_clients = []
#NOTE: These usernames are here so that anyone trolly can't take them and confuse users.
usernames_list = ['You', 'Server', 'server']
online = len(client_ip_list)
command_list = ['/whoishere']
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except:
    #NOTE: Small amount of redundancy, just in case.
    port = random.randint(49152, 65535)
    print(f"PORT 5556 CANNOT BE ACCESSED, PLEASE DIRECT ALL CLIENTS TO PORT {port}")
    print("Resuming normal operation...")
    ServerSocket.bind(host, port)
print('Waiting for a Connection..')
ServerSocket.listen(200)
#TODO: Make a pre-start server console, similar to client console. THREAD IT so that it can receive console logs and be interacted with at the same time.
#NOTE: Using connection instead of IP to make it harder to accidentally kick someone else out.
def remove(connection):
    if connection in client_ip_list:
        client_ip_list.remove(connection)
def broadcast(message, connection, address, username): 
    for clients in client_ip_list:
        if address not in muted_clients:
            if username not in muted_clients:
                if clients!=connection:
                    clients.sendall(message.encode('utf-8')) 
def threaded_client(connection, address):
    username_received = False
    username = ''
    #TODO: Add a username length limit, so that trolls have a tougher time.
    while username_received == False:
        connection.sendall(bytes('username', 'utf-8'))
        username_receive = connection.recv(2048)
        username_receive_decoded = username_receive.decode('utf-8')
        if username_receive_decoded in usernames_list:
            print(f"{address} attempted to take a username that has already been registered.")
            username_taken = "username_taken"
            username_taken_encoded = username_taken.encode('utf-8')
            connection.sendall(username_taken_encoded)
            continue
        elif username_receive_decoded == address:
            if username_receive_decoded not in usernames_list:
                print(f"{address} has not chosen a username and will use {address} as username.")
                username_received = True
                connection.sendall(bytes("username_chosen", "utf-8"))
                username = username_receive_decoded
                break
        else:
            print(f"{address} has chosen {username_receive_decoded} as their username.")
            usernames_list.append(username_receive_decoded)
            username_received = True
            username = username_receive_decoded
            connection.sendall(bytes("username_chosen", "utf-8"))
            break
    while username_received == True:
        # try:
            data = connection.recv(2048)
            if username in kicked_clients:
                print(kicked_clients)
                connection.sendall(bytes("server_kick", "utf-8"))
                username_list.remove(username)
                print(f"{username} has been kicked.")
                connection.shutdown(2)
                connection.close()
                sys.exit()
            reply = f'{username} says: ' + data.decode('utf-8')
            if address not in muted_clients:
                global your_reply
                your_reply = f'(You) said: ' + data.decode('utf-8')
            elif username not in muted_clients:
                your_reply = f'(You) said: ' + data.decode('utf-8')
            else:
                your_reply = f'(You, Muted) said: ' + data.decode('utf-8')
            server_log = data.decode('utf-8')
            if server_log == "/whoishere":
                command_check("/whoishere", username)
                whoishere(connection)
            if not data:
                break
            if server_log not in command_list:
                broadcast(reply, connection, address, username)
                connection.sendall(your_reply.encode('utf-8'))
                print(f"{address} ({username}) has sent \"{server_log}\"")
    """
        except:
            print(f"{address} has left the chat!")
            client_ip_list.remove(connection)
            usernames_list.remove(username)
            online = len(client_ip_list)
            if online < 1:
                print(f"There are now {online} threads.")
            else:
                print(f"There is now {online} thread(s).")
            connection.shutdown(2)
            connection.close()
            sys.exit() 
    """
# def inbox(dead_connection, message):
def command_check(command, username):
    if command in command_list:
        print (f"{username} issued {command} to the server.")
#NOTE: Defining whoishere() because later with the implementation of the server_console, it could be useful, but otherwise, it probably won't be.
#NOTE: The sleep_minutes function is to make it easier for the server (or Operator) to define how long a mute duration should be.
def whoishere(connection):
    online = len(client_ip_list)
    if online != 1:
        whoishere_fstring = f"There are currently {online} people online right now, {username_list}"
        connection.sendall(whoishere_fstring.encode('utf-8'))
    else:
        whoishere_fstring = f"There is currently {online} people online right now, {username_list}"
        connection.sendall(whoishere_fstring.encode('utf-8'))
def server_console():
    while while_loop == True:
        console_input = input(">>> ")
        if console_input == "/whoishere":
            online = len(client_ip_list)
            if online != 1:
                whoishere_fstring = f"There are currently {online} people online right now, {client_ip_list}"
                print(whoishere_fstring)
            else:
                whoishere_fstring = f"There is currently {online} people online right now, {client_ip_list}"
                print(whoishere_fstring)
        if console_input == "/kick":
            while_loop == False
            who_to_kick = input("(Username to kick)>>> ")
            if who_to_kick not in usernames_list:
                print ("This user is not online right now.")
            elif who_to_kick in usernames_list:
                kicked_clients.append(who_to_kick)
                time.sleep(10)
                kicked_clients.remove(who_to_kick)
                while_loop == True
            else:
                print("Unknown Error, cannot kick.")
        if console_input == "/uptime":
            uptime_call = time.perf_counter()
            print(f"Uptime: {uptime_call - uptime_start:5.1f} seconds.")
        if console_input == "/mute":
            who_to_mute = input("(Username to mute)>>> ")
            if who_to_mute not in muted_clients:
                if who_to_mute in username_list:
                    how_long_mute = input("(Duration of Mute (Minutes))>>> ")
                    start_new_thread(mute_timer, (who_to_mute, how_long_mute))
                elif who_to_mute in usernames_list:
                    raw_how_long_mute = input("(Duration of Mute (Minutes))>>> ")
                    how_long_mute = int(raw_how_long_mute)
                    start_new_thread(mute_timer, (who_to_mute, how_long_mute))
                else:
                    print("IP address is invalid or the user is not online right now.")
            else:
                print("IP address has already been muted.")
        if console_input == "/help":
            print("""
            /help - Shows this help section.
            /whoishere - Lists how many are online in your server and what their IP addresses are.
            /mute - Prevents the server from broadcasting a username's responses. The muted client will not know they are muted.
            /kick - Kicks the client from the server.
            /uptime - Prints the amount of time that the server has been on. 
            """)
        else:
            print("Invalid Command.")
def mute_timer(entity, duration):
    muted_clients.append(entity)
    print(f"{entity} has been muted for {duration} minutes.")
    time.sleep(duration * 60)
    print(f"{entity} has been unmuted.")
    muted_clients.remove(entity)
    sys.exit()

while while_loop == True:
    start_new_thread(server_console, ())
    Client, address = ServerSocket.accept()
    #TODO: Make it so that it's discernible where a message came from.
    #TODO: Figure out how to make the thread only run when it needs to, so that the thread doesn't just run wild (and possibly do something problematic, like take more resources than it should)
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, address))
    client_ip_list.append(Client)
    print(client_ip_list)
    username_list.append(address)
    online = len(client_ip_list)
    print(f'Thread Count: {online}')
ServerSocket.close()