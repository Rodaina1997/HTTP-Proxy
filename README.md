# HTTP-Proxy
Intro 🚪
HTTP proxies have a lot of use cases, from caching, authentication and preventing users from accessing malicious websites. They’re widely used in the world wide web and in business settings. Businesses use proxies to prevent their employees from surfing malicious websites, and enforce authentication and logging. Websites use proxies to provide caching and load balancing that shrinks websites load time. <br />
This project is a parallel HTTP proxy server that accepts a GET request and makes it on behalf of the client. The HTTP proxy returns the response if succeeded to the client, and an 404 if there was an error. <br />
The proxy DOES handle multiple clients in parallel, more on that later. It  handles GET requests in parallel.
Other request methods (PUT, PATCH, DELETE, ...etc) received by the proxy should return a 501 not implemented error. 

