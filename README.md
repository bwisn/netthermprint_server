# netthermprint_server
## What it is?
Server compatible with libnetthermprint

## How to run it?
```
docker build -t netthermprint_server .
docker run -p 41231:41231 -p 41230:41230/udp netthermprint_server
```
