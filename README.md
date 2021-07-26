# HTTP-Proxy
# Intro 🚪
HTTP proxies have a lot of use cases, from caching, authentication and preventing users from accessing malicious websites. They’re widely used in the world wide web and in business settings. Businesses use proxies to prevent their employees from surfing malicious websites, and enforce authentication and logging. Websites use proxies to provide caching and load balancing that shrinks websites load time. <br />
# Description
This project is a parallel HTTP proxy server that accepts a GET request and makes it on behalf of the client. The HTTP proxy returns the response if succeeded to the client, and an 404 if there was an error. <br />
The proxy server does the following (assuming it's single threaded) <br />
1.Opens a listening TCP socket, and binds it to the port specified by the first command line argument. <br />
2.Uses TCP for communication with both clients and servers. <br />
3.Opens a TCP connection for every HTTP request to be proxied. <br />
4.After the client’s HTTP request is parsed. Opens a TCP connection with the asked website, making the request and return the response back to the client if successful. <br />
5.Closes the TCP connection with both client and requested website’s server. (because HTTP 1.0 doesn’t have persistent connections). <br />
# Implementation steps: <br />
1. Making sure that the code validates HTTP requests correctly, <br />
a.A valid HTTP request contains the following parts <br />
<METHOD> <URL or PATH> <HTTP VERSION> v
And a Host header, if the specified resource is a PATH (relative): <br />
Host: <HOSTNAME> <br />
All other headers just need to be properly formatted [name] [colon] [value], any names and values are valid. <br />
<HEADER NAME>: <HEADER VALUE> <br />
b.After parsing HTTP requests correctly, making sure that we can identify which requests are malformed (have missing required parts or bad method). For HTTP/1.0 all the available methods are GET, HEAD, POST, -PUT- , any other method will return 501, missing parts in the request line of malformed headers will return 400. <br />
2. Making sure that code parses the URL correctly (i.e. Sanitization) <br />
After validation, the proxy will need to parse the requested URL. The proxy needs at most three pieces of information to be extracted: the requested host and port, and the requested path. If parsing the URL fails, returns INVALID_REQUEST, don't validate the URL. <br />
3. Making sure that code accepts a single TCP connection correctly and rejects bad requests. <br />
 PUT www.google.com/ HTTP/1.0\r\n\r\n gets a "Not Implemented" (501) response. <br />
 GOAT www.google.com/ HTTP/1.0\r\n\r\n gets a “Bad Request” (400) response. <br />
4. Making sure that we can act as a proxy for a single client sending sequential requests. <br />
  Accept from client: <br />
  GET http://eng.alexu.edu.eg/ HTTP/1.0 <br />
  Or <br />
  GET / HTTP/1.0 <br />
  Host: eng.alexu.edu.eg <br />
no threading yet. After accepting the client’s connection, read their HTTP request -> sanitize it -> reject it if invalid -> send it to the remote server and then the new part is to read the response of the remote server then send it back to the client socket and close their connection. <br />
5. Caching: <br />
Just before sending back the response to the client, we make a copy and store this response somewhere in memory (like a hashtable) not in a file. <br />
If the client sends a request twice, we’ll use the cached copy the second time and later on ( we’ll assume that the page is totally static). <br />
6. Serving the masses: By ending this part, we are able to serve clients in parallel. <br />



