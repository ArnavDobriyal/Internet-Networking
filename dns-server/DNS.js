// DNS server that handles A and CNAME record queries efficiently using UDP and dns-packet.

const dgram = require('node:dgram');
const dnspacket = require('dns-packet');

const server = dgram.createSocket('udp4');

// Extended database to handle A and CNAME records
const db = {
  'arnav.com': {
    type: 'A',       // A record
    data: '1.2.3.4'  // IP address
  },
  'blocg.arnav.com': {
    type: 'A',       // A record
    data: '5.6.7.8'  // IP address
  },
  'www.arnav.com': {
    type: 'CNAME',   // CNAME record
    data: 'arnav.com' // Alias
  }
};

function handleDNSRequest(msg, rinfo) {
  let incomingReq;

  try {
    incomingReq = dnspacket.decode(msg);
  } catch (err) {
    console.error('Failed to decode DNS request:', err);
    return; 
  }


  if (!incomingReq.questions || incomingReq.questions.length === 0) {
    console.error('Invalid DNS request: no questions found');
    return;
  }

  const queryName = incomingReq.questions[0].name;
  const record = db[queryName];

  // If record is found, create a response based on the record type
  if (record) {
    if (record.type === 'A') {
      sendARecordResponse(incomingReq, record.data, rinfo);
    } else if (record.type === 'CNAME') {
      sendCNAMERecordResponse(incomingReq, record.data, rinfo);
    }
  } else {
    console.log(`No record found for query: ${queryName}`);
  }
}

function sendARecordResponse(incomingReq, ipfromdb, rinfo) {
  const response = {
    type: 'response',
    id: incomingReq.id,
    questions: incomingReq.questions,
    answers: [{
      type: 'A',
      class: 'IN',
      name: incomingReq.questions[0].name,
      data: ipfromdb
    }]
  };

  const encodedResponse = dnspacket.encode(response);
  sendDNSResponse(encodedResponse, rinfo);
}

function sendCNAMERecordResponse(incomingReq, cnamefromdb, rinfo) {
  const response = {
    type: 'response',
    id: incomingReq.id,
    questions: incomingReq.questions,
    answers: [{
      type: 'CNAME',
      class: 'IN',
      name: incomingReq.questions[0].name,
      ttl: 300,
      data: cnamefromdb
    }]
  };

  const encodedResponse = dnspacket.encode(response);
  sendDNSResponse(encodedResponse, rinfo);
}

function sendDNSResponse(encodedResponse, rinfo) {
  server.send(encodedResponse, 0, encodedResponse.length, rinfo.port, rinfo.address, (err) => {
    if (err) {
      console.error('Error sending DNS response:', err);
    } else {
      console.log('DNS response sent');
    }
  });
}

server.on('message', handleDNSRequest);

server.bind(8080, () => {
  console.log('DNS server running on port 8080');
});


/*
Use command
px nodemon index.js  
dig @127.0.0.1 -p 8080 domain.name
 node tests.js 
*/