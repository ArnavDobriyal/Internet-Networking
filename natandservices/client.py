import socket

def client():
    # Client connects to the NAT router
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('127.0.0.1', 8888))  
        message = "Hello from the client!"
        print(f"Client: Sending message to NAT Router: {message}")
        s.sendall(message.encode())

        # Receive the response from the NAT router
        data = s.recv(1024)
        print(f"Client: Received response: {data.decode()}")

if __name__ == "__main__":
    client()
