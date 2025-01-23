import socket
import random

class NATRouter:
    def __init__(self):
        # IP and port pools
        self.private_ips = [f"192.168.1.{i}" for i in range(2, 255)]  # Private IP pool
        self.public_ips = [f"203.0.113.{i}" for i in range(1, 10)]   # Public IP pool
        self.public_ports = list(range(10000, 11000))               # Public port pool
        self.nat_table = {}  # Maps (private IP, private port) -> (public IP, public port)

    def assign_private_ip(self):
        return random.choice(self.private_ips)

    def assign_public_ip_port(self):
        return random.choice(self.public_ips), random.choice(self.public_ports)

    def handle_client(self, client_socket, server_address):
        # Assign private IP and port for the client
        private_ip = self.assign_private_ip()
        private_port = client_socket.getsockname()[1]

        # Assign public IP and port
        public_ip, public_port = self.assign_public_ip_port()
        self.nat_table[(private_ip, private_port)] = (public_ip, public_port)
        print(f"[NAT TABLE] Mapped Private ({private_ip}:{private_port}) -> Public ({public_ip}:{public_port})")

        # Connect to the Internet server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect(server_address)

            # Receive data from client and forward it to the server
            client_data = client_socket.recv(1024)
            print(f"[NAT Router] Forwarding data from client to server: {client_data.decode()}")
            server_socket.send(client_data)

            # Receive response from server and forward it back to the client
            server_response = server_socket.recv(1024)
            print(f"[NAT Router] Forwarding data from server to client: {server_response.decode()}")
            client_socket.send(server_response)

    def start(self, bind_address, server_address):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as nat_socket:
            nat_socket.bind(bind_address)
            nat_socket.listen(1)
            print(f"[NAT Router] Listening on {bind_address}")

            client_socket, client_address = nat_socket.accept()
            print(f"[NAT Router] Connection from {client_address}")
            self.handle_client(client_socket, server_address)
            client_socket.close()

# Internet Server Simulation
def internet_server(bind_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(bind_address)
        server_socket.listen(1)
        print(f"[Internet Server] Listening on {bind_address}")

        client_socket, client_address = server_socket.accept()
        print(f"[Internet Server] Connection from {client_address}")

        # Receive data from the NAT router
        data = client_socket.recv(1024)
        print(f"[Internet Server] Received: {data.decode()}")

        # Send a response back to the NAT router
        response = f"Hello from Internet Server!"
        client_socket.send(response.encode())
        print(f"[Internet Server] Response sent.")
        client_socket.close()

# Main Execution
if __name__ == "__main__":
    # Define addresses
    nat_bind_address = ("127.0.0.1", 8888)  # NAT router
    internet_bind_address = ("127.0.0.1", 9999)  # Internet server

    # Start the Internet server
    print("[Starting Internet Server...]")
    import threading
    threading.Thread(target=internet_server, args=(internet_bind_address,), daemon=True).start()

    # Start the NAT router
    print("[Starting NAT Router...]")
    nat_router = NATRouter()
    nat_router.start(nat_bind_address, internet_bind_address)
