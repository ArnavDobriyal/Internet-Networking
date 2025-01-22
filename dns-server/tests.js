// dns-client.js

const dgram = require('dgram');
const dnspacket = require('dns-packet');

// Helper function to send DNS request
function sendDNSRequest(query, type = 'A') {
  const client = dgram.createSocket('udp4');

  // Encode the DNS packet
  const packet = dnspacket.encode({
    type: 'query',
    id: Math.floor(Math.random() * 65535),  // Random DNS transaction ID
    questions: [{
      type: type,     // Query type: A, CNAME, etc.
      class: 'IN',
      name: query     // Domain name to query
    }]
  });

  // Send the packet to DNS server
  client.send(packet, 0, packet.length, 8080, '127.0.0.1', (err) => {
    if (err) {
      console.error('Error sending DNS request:', err);
    }
    console.log(`DNS query sent for ${query} (Type: ${type})`);

    // Wait for the response
    client.on('message', (msg) => {
      const response = dnspacket.decode(msg);
      console.log('DNS Response:', response);
      client.close();
    });
  });
}

// Test cases
function runTests() {
  // Test 1: Query A record for arnav.com
  sendDNSRequest('arnav.com', 'A');

  // Test 2: Query A record for blocg.arnav.com
  sendDNSRequest('blocg.arnav.com', 'A');

  // Test 3: Query CNAME record for www.arnav.com
  sendDNSRequest('www.arnav.com', 'CNAME');

  // Test 4: Query unknown domain (no record)
  sendDNSRequest('unknown.com', 'A');

  // Test 5: Query with wrong type (MX record for unsupported type)
  sendDNSRequest('arnav.com', 'MX');
}

// Run the tests
runTests();
