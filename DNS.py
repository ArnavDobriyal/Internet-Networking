import socketserver
import dnslib
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class DNSRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        try:
            # Parse the incoming DNS request
            dns_request = dnslib.DNSRecord.parse(data)
            logging.info(f"Received DNS request: {dns_request.q.qname} ({dns_request.q.qtype}, {dns_request.q.qclass})")

            # Build DNS response
            response = dnslib.DNSRecord(dns_request.header)
            response.header.set_rcode(dnslib.RCODE.NOERROR)
            response.add_answer(
                dnslib.RR(
                    rname=dns_request.q.qname,
                    rtype=dns_request.q.qtype,
                    rclass=dns_request.q.qclass,
                    ttl=300,
                    rdata=dnslib.A("127.0.0.1")  # Change IP based on need
                )
            )

            # Send the response
            socket.sendto(response.pack(), self.client_address)

        except Exception as e:
            logging.error(f"Error processing DNS request: {e}")

class DNSServer:
    def __init__(self, ip="127.0.0.1", port=5353):
        self.server_address = (ip, port)
        self.server = socketserver.UDPServer(self.server_address, DNSRequestHandler)

    def start(self):
        logging.info(f"Starting DNS server on {self.server_address[0]}:{self.server_address[1]}")
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down server.")
        finally:
            self.server.shutdown()

if __name__ == "__main__":
    dns_server = DNSServer()
    dns_server.start()
