from chat_server import Server
# from client_state_machine import ClientSM
from chat_client_class import Client

server = Server()

# client = ClientSM(server)
client = Client(server)
# tmp = client.connect_to("server")
# state = client.set_state("OK")
# myname = client.
name = client.get_name()
print(name)

# ip = 10.208.2.251
# myip = 10.209.70.46

