let http = require('http');
let server = http.createServer((request, response) => {
  response.writeHead(200, {'Content-Type': 'text/html'});
  response.end('<h1>Hello world</h1>');
});
server.listen(8080);
