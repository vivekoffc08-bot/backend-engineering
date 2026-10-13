# TCP vs UDP --- Backend Networking Notes

## Hussein Nasser video + Python `asyncio` server walkthroughs

**Video:** [When to Use UDP vs TCP in Building a Backend
Application?](https://www.youtube.com/watch?v=qqRYkcta6IE)

These are study notes, not a verbatim transcript. They follow the
video's key themes---UDP, TCP, chat systems, multiplayer games,
browsers/web servers---and combine them with your supplied architecture
notes and Python server examples.

------------------------------------------------------------------------

## 1. Where TCP and UDP fit

``` text
Application protocol: HTTP, database protocol, custom protocol
                         ↓
Transport:              TCP or UDP
                         ↓
Network:                IP
                         ↓
Link/physical:           Wi-Fi, Ethernet, radio/electrical/light
```

**IP (Layer 3)** routes packets between networks using source and
destination IP addresses. IP does not provide TCP's ordered byte stream,
retransmission, or application message semantics.

**TCP/UDP (Layer 4)** provide transport services. Ports help the
operating system deliver received data to the appropriate
socket/application.

``` text
192.168.1.20:8080
       │       └── port
       └────────── IP address
```

An actual TCP connection is identified by the source IP, source port,
destination IP, and destination port, along with the protocol. A port is
a transport identifier, not a physical door.

------------------------------------------------------------------------

## 2. TCP vs UDP --- core differences

### TCP --- Transmission Control Protocol

TCP provides a **reliable, ordered byte stream** between endpoints. It
includes:

-   Connection establishment and termination.
-   Sequence numbers and acknowledgements.
-   Retransmission of lost data.
-   Reordering before bytes are delivered to the application.
-   Flow control to avoid overwhelming the receiver.
-   Congestion control to adapt to network conditions.

TCP is connection-oriented and maintains state for each active
connection.

Important nuance: TCP is reliable, not magical or infallible. If the
connection fails and data cannot be delivered, TCP can time out or
report an error. An ACK means TCP received bytes; it does **not** prove
that the remote application completed a business operation.

### UDP --- User Datagram Protocol

UDP sends independent **datagrams**. It provides source/destination
ports and datagram boundaries, plus a checksum for error detection (with
details depending on context).

UDP does **not** itself provide:

-   A connection handshake.
-   Delivery acknowledgements or automatic retransmission.
-   Ordered delivery or duplicate suppression.
-   TCP-style flow control or congestion control.

Datagrams may be lost, duplicated, or arrive out of order. If an
application needs reliability, ordering, deduplication, or congestion
control, it must implement suitable mechanisms or use a higher-level
protocol such as QUIC.

UDP is called connectionless, but the OS still maintains socket
resources, port bindings, and queues. Some OS APIs can "connect" a UDP
socket to a default peer; that still does not add TCP-like reliable
delivery.

### Comparison table

  -----------------------------------------------------------------------
  Feature                 TCP                     UDP
  ----------------------- ----------------------- -----------------------
  Model                   Connection-oriented     Connectionless
                                                  datagrams

  Data delivered to app   Ordered byte stream     Individual datagrams
  as                                              

  Message boundaries      Not preserved by TCP    Preserved per datagram

  Delivery                Retransmits lost data;  Best effort
                          reports failure if it   
                          cannot continue         

  Ordering                Ordered stream          No ordering guarantee

  Handshake               Normally a 3-way        No transport handshake
                          handshake               required

  ACKs                    Yes                     No built-in delivery
                                                  ACK

  Flow control            Yes                     No TCP-style flow
                                                  control

  Congestion control      Yes                     Not built into UDP

  State                   Per-connection state    No TCP-like connection
                                                  state required by
                                                  protocol

  Common use              HTTP/1.1, HTTP/2, SSH,  DNS, real-time media,
                          databases, brokers      games, telemetry

  Caveat                  Reliability can add     UDP is not
                          delay when loss occurs  automatically faster in
                                                  every scenario
  -----------------------------------------------------------------------

Avoid the oversimplification "TCP is slow, UDP is fast." Performance
depends on network conditions, message sizes, implementation, and the
application's needs. Sending UDP at unlimited rates can cause congestion
and packet loss; responsible UDP applications need appropriate
congestion control.

------------------------------------------------------------------------

## 3. Byte stream vs datagrams

### TCP is a byte stream

``` python
writer.write(b"HELLO")
writer.write(b"WORLD")
```

The receiver is **not** guaranteed to read `HELLO` and `WORLD` as two
separate messages. It might read `HELLOWORLD`, `HEL`, then `LOWORLD`, or
another grouping.

TCP preserves byte order, not `write()` boundaries. A TCP application
protocol must define message framing, for example:

-   Fixed-size messages.
-   Delimiter such as newline.
-   Length prefix before each message.
-   A protocol-specific framing format.

`reader.read(1024)` reads up to 1024 bytes; it does not mean "read one
complete message."

### UDP preserves datagram boundaries

If a client sends two datagrams, `HELLO` and `WORLD`, the receiver gets
two separate datagram events if both arrive. Datagrams can still be
lost, duplicated, or reordered.

------------------------------------------------------------------------

## 4. TCP three-way handshake

A TCP connection normally starts with:

``` text
Client                                Server
  | -------- SYN --------------------> |
  | <------- SYN + ACK --------------- |
  | -------- ACK --------------------> |
  |                                    |
  |       Connection established       |
```

-   **SYN:** client requests connection setup and synchronizes
    sequence-number state.
-   **SYN-ACK:** server acknowledges the client's SYN and sends its own
    SYN.
-   **ACK:** client acknowledges the server's SYN.

TCP uses sequence numbers to track bytes and ACKs to acknowledge
received data. This is transport setup, **not** user
login/authentication.

UDP can send a datagram without this TCP handshake.

------------------------------------------------------------------------

## 5. Choosing a protocol for real applications

The video compares chat systems, multiplayer games, and browsers/web
servers.

### Chat or messaging

Chat messages usually need to arrive intact and in order:

``` text
1. Are you free?
2. Let's meet at 6.
3. I'm on my way.
```

TCP is a natural fit for a client-server connection because it supplies
reliable, ordered bytes. The application still needs to handle identity,
persistence, reconnects, and business-level delivery/read receipts.

UDP can be used, but then the application must build any needed
acknowledgements, retries, ordering, and duplicate handling.

### Multiplayer games

A game might send frequent player-position updates:

``` text
t=100 ms: position (10, 4)
t=116 ms: position (11, 4)
t=132 ms: position (12, 4)
```

An old position arriving late may be less useful than the newest
position. UDP can be useful for time-sensitive updates where some loss
is tolerable.

Not all game messages are disposable. Inventory changes, purchases, and
match results need correctness guarantees. Games may use sequence
numbers, timestamps, prediction, interpolation, selective reliability,
and congestion control on top of UDP. TCP can still be appropriate for
some game traffic.

### Browser and web server

-   HTTP/1.1 commonly runs over TCP.
-   HTTP/2 commonly runs over TCP.
-   HTTP/3 runs over QUIC, which uses UDP underneath and implements
    reliability, streams, and congestion control at the QUIC layer.

Traditional HTTP responses contain HTML, JavaScript, CSS, JSON, images,
or other content. Missing bytes would make the content unusable, so
TCP's reliable ordered stream is a natural fit for HTTP/1.1 and HTTP/2.

QUIC/HTTP/3 addresses some limitations of TCP's single ordered byte
stream by supporting multiple streams. Loss affecting one QUIC stream
need not block delivery on all other streams in the same way. This
reliability is supplied by QUIC---not by UDP alone.

------------------------------------------------------------------------

## 6. Raw TCP/UDP vs HTTP APIs

When you write:

``` python
@app.get("/users")
def get_users():
    return {"users": []}
```

you work at the application layer. FastAPI and Uvicorn handle HTTP and
the lower-level socket/transport machinery.

With a raw TCP or UDP server, you work closer to the transport layer:

``` text
Your custom application protocol
              ↓
           TCP/UDP
              ↓
              IP
              ↓
        Wi-Fi / Ethernet
```

Raw TCP does not automatically understand HTTP methods, headers,
cookies, JSON, routes, or status codes. Raw UDP does not understand an
application protocol either. **You define what the bytes mean.**

### Raw TCP in production

-   **PostgreSQL, MySQL, Redis:** database protocols are commonly
    carried over TCP. Redis commonly uses RESP over TCP on port `6379`;
    PostgreSQL commonly uses `5432`; MySQL commonly uses `3306`.
-   **Kafka and RabbitMQ:** use TCP-based protocols for client/broker
    communication.
-   **SSH:** commonly uses TCP port `22`.

TCP transports ordered bytes; the application protocol defines message
formats, authentication, acknowledgements, and operations.

### Raw UDP in production

-   **DNS:** commonly uses UDP port `53` for short query/response
    exchanges; DNS can also use TCP in defined cases.
-   **Real-time voice/video:** UDP-based media can prioritize fresh data
    over waiting for retransmission of old media.
-   **Games:** frequent position/state updates can tolerate selected
    losses.
-   **Telemetry:** UDP can suit lightweight events when occasional loss
    is acceptable.

Real media and game systems add buffering, loss handling, feedback, and
congestion control. UDP alone does not provide these features.

------------------------------------------------------------------------

## 7. Supplied architecture notes --- refined

-   **IP (Layer 3):** routes packets using IP addressing; it does not
    provide TCP's ordered byte stream or application semantics.
-   **TCP/UDP (Layer 4):** ports identify transport endpoints. TCP
    provides reliable ordered bytes; UDP sends datagrams without
    built-in delivery/order guarantees.
-   **TCP resource use:** active connections maintain state such as
    sequence numbers, buffers, timers, and flow/congestion-control
    information.
-   **UDP resource use:** UDP has less TCP-like per-connection
    machinery, but the OS still maintains sockets, queues, and port
    bindings.
-   **"UDP blasts as fast as possible":** UDP itself has no TCP-style
    congestion control, but applications should not blindly transmit
    without congestion-aware behavior.
-   **"TCP guarantees delivery":** more precisely, TCP retransmits and
    provides an ordered stream while the connection works; it can still
    fail and report an error.

------------------------------------------------------------------------

# Part II --- Python asyncio TCP Server

## 8. Complete TCP server

Save as `tcp_server.py`:

``` python
import asyncio


async def handle_client(reader, writer):
    address = writer.get_extra_info("peername")
    print(f"client connected from address => {address}")

    try:
        while True:
            data = await reader.read(1024)

            if not data:
                break

            message = data.decode()
            print(f"Received => {message}")

            writer.write(f"Server Received : {message}".encode())
            await writer.drain()

    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Connection closed => {address}")


async def main():
    server = await asyncio.start_server(
        handle_client,
        host="127.0.0.1",
        port=8080
    )

    print("TCP server started on port 8080")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

``` bash
python tcp_server.py
```

`127.0.0.1` is loopback: this example is reachable from the same
machine, not normally from other devices on your LAN.

## 9. TCP server, line by line

### `import asyncio`

Imports Python's asynchronous I/O library: event loop, coroutines, and
network helpers.

### `async def handle_client(reader, writer):`

Defines the coroutine that handles **one accepted TCP connection**.

-   `reader` is an `asyncio.StreamReader` for incoming bytes.
-   `writer` is an `asyncio.StreamWriter` for outgoing bytes.

If multiple clients connect, asyncio can run multiple handler
coroutines, each with its own reader/writer pair.

### `address = writer.get_extra_info("peername")`

Gets the remote peer address, often something like:

``` python
("127.0.0.1", 53124)
```

The remote port is usually the client's temporary/ephemeral port---not
the server's listening port `8080`.

### `print(...)`

Logs the peer for learning/debugging. Production systems commonly use
structured logging.

### `try:`

Starts a cleanup region. The `finally` block will run when the handler
exits normally or with an exception.

### `while True:`

Keeps reading from this connection. A TCP connection can carry multiple
chunks/messages over its lifetime.

### `data = await reader.read(1024)`

Reads **up to** 1024 bytes. It waits asynchronously for data/EOF and
allows the event loop to run other tasks while waiting.

Crucially, the returned chunk may be shorter than 1024 bytes and does
not correspond to one client `write()` call or one complete application
message.

### `if not data: break`

An empty bytes value indicates EOF: the peer has closed its sending side
and no more bytes are available. The loop ends.

TCP can support half-close, where one direction is closed while the
other direction may still be usable. This simple example ends its read
loop at EOF.

### `message = data.decode()`

Converts bytes into a Python string, using UTF-8 by default. This
assumes the protocol sends text. Arbitrary binary data should not be
blindly decoded.

### `print(f"Received => {message}")`

An f-string inserts `message` into the log. It logs the chunk read,
which may not be a complete message.

### `writer.write(f"Server Received : {message}".encode())`

Creates a response string, encodes it into bytes, and queues it for the
TCP stream.

-   `f"..."` formats a string.
-   `.encode()` turns text into bytes.
-   `write()` queues data; it doesn't necessarily flush it immediately.

This is a small custom protocol---not HTTP.

### `await writer.drain()`

Waits according to the stream's write-buffer flow control/backpressure.
It helps prevent endlessly queuing output faster than it can be handled.

It is **not** an application-level acknowledgement that the client
processed the response.

### `finally:`

Runs cleanup when leaving the `try` block.

### `writer.close()`

Initiates closing the stream writer/connection.

### `await writer.wait_closed()`

Waits for closure to complete.

### Final `print(...)`

Logs that the handler is closing its connection.

## 10. TCP server startup, line by line

### `async def main():`

Defines the top-level coroutine that creates and runs the server.

### `await asyncio.start_server(...)`

``` python
server = await asyncio.start_server(
    handle_client,
    host="127.0.0.1",
    port=8080
)
```

-   `handle_client` is used for each accepted connection.
-   `host` is the local address to bind.
-   `port=8080` chooses the local TCP port.
-   `await` waits for asynchronous setup.

The OS creates/configures the listening socket. The OS TCP stack handles
the handshake; asyncio accepts the connection and provides stream
objects to the handler.

### `async with server:`

Uses the server's asynchronous context manager to manage its lifetime
and close it on exit.

### `await server.serve_forever()`

Keeps accepting connections. Without a long-running await, `main()`
could finish and the program would exit.

### `if __name__ == "__main__":`

Runs the startup code only when this file is executed directly, not when
imported by another module.

### `asyncio.run(main())`

Creates/runs the event loop for `main()` and closes it when finished.

------------------------------------------------------------------------

# Part III --- Python asyncio UDP Server

## 11. Complete UDP server

Save as `udp_server.py`:

``` python
import asyncio


class MyUDPServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"Received {message} from {addr}")

        self.transport.sendto(b"Hello from UDP Server", addr)


async def main():
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: MyUDPServerProtocol(),
        local_addr=("127.0.0.1", 8080)
    )

    print("UDP server started running on port 8080")

    try:
        await asyncio.sleep(3600)
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

``` bash
python udp_server.py
```

The TCP and UDP examples can use port `8080` simultaneously because TCP
port `8080` and UDP port `8080` are different transport endpoints.

## 12. UDP server, line by line

### `class MyUDPServerProtocol:`

Defines a class implementing callbacks that asyncio invokes for the
datagram endpoint.

Unlike the TCP example, it doesn't receive a persistent
`StreamReader`/`StreamWriter` pair per peer. It receives datagram events
on a bound UDP socket.

### `def connection_made(self, transport):`

Asyncio calls this when the local datagram endpoint is ready. The name
can be misleading: this does **not** mean a TCP-like handshake happened
with every client. It means the local UDP transport has been set up.

### `self.transport = transport`

Stores the transport on the protocol object so another method can send
datagrams or close the endpoint. `self` refers to this particular
instance.

### `def datagram_received(self, data, addr):`

Asyncio calls this method when one UDP datagram arrives.

-   `data` contains that datagram's bytes.
-   `addr` is the sender's address, usually `(IP, port)`.

The event loop invokes this callback; your code doesn't call it manually
for every packet.

### `message = data.decode()`

Decodes bytes as UTF-8 text by default. This assumes the datagram
payload is text.

### `print(f"Received {message} from {addr}")`

Logs the text and sender address.

A UDP callback receives one datagram at a time, so the datagram boundary
is preserved. The datagram can still be lost before it arrives.

### `self.transport.sendto(b"Hello from UDP Server", addr)`

Sends one datagram containing the bytes `Hello from UDP Server` to the
sender's address.

-   `b"..."` is a bytes literal.
-   `addr` specifies where the reply goes.
-   UDP does not guarantee delivery or retransmit this reply
    automatically.

One UDP socket can receive packets from multiple clients and reply to
each sender by using the supplied address.

## 13. UDP endpoint startup, line by line

### `loop = asyncio.get_running_loop()`

Gets the event loop currently running this coroutine.

### `await loop.create_datagram_endpoint(...)`

Creates a UDP endpoint and returns a `(transport, protocol)` pair.

``` python
transport, protocol = await loop.create_datagram_endpoint(
    lambda: MyUDPServerProtocol(),
    local_addr=("127.0.0.1", 8080)
)
```

### `lambda: MyUDPServerProtocol()`

A lambda is a small anonymous function. This is conceptually similar to:

``` python
def create_protocol():
    return MyUDPServerProtocol()
```

Asyncio calls the factory to create the protocol object that receives
callbacks.

### `local_addr=("127.0.0.1", 8080)`

Tells the OS to bind the UDP socket to loopback address and port 8080.
The tuple is `(host, port)`.

### `transport, protocol = ...`

-   `transport` sends datagrams and closes the endpoint.
-   `protocol` is the callback object. The example doesn't otherwise use
    this variable directly.

### `await asyncio.sleep(3600)`

Keeps the coroutine alive for one hour without blocking the event-loop
thread. The loop can continue dispatching datagram callbacks while this
coroutine sleeps.

### `finally: transport.close()`

Closes the UDP transport when the coroutine exits or is interrupted.

### `asyncio.run(main())`

Runs the top-level coroutine with an event loop.

------------------------------------------------------------------------

# Part IV --- Clients to Test the Servers

## 14. TCP client

Save as `tcp_client.py`:

``` python
import asyncio


async def main():
    reader, writer = await asyncio.open_connection(
        "127.0.0.1",
        8080
    )

    writer.write(b"Hello TCP server")
    await writer.drain()

    data = await reader.read(1024)
    print("Response:", data.decode())

    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
```

Run `python tcp_server.py` in one terminal, then `python tcp_client.py`
in another.

Expected output:

``` text
Response: Server Received : Hello TCP server
```

Explanation:

-   `asyncio.open_connection()` establishes a TCP connection and returns
    reader/writer streams.
-   `writer.write()` queues bytes.
-   `await writer.drain()` waits for write-buffer flow control.
-   `await reader.read(1024)` waits for response bytes.
-   `writer.close()` starts closing the connection.
-   `await writer.wait_closed()` waits for closure.

This short test sends one small payload. It does not prove that TCP
preserves message boundaries; TCP does not.

## 15. UDP client

Save as `udp_client.py`:

``` python
import asyncio


class UDPClientProtocol:
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(self.message)

    def datagram_received(self, data, addr):
        print("Response:", data.decode())
        self.transport.close()

    def error_received(self, exc):
        print("UDP error:", exc)

    def connection_lost(self, exc):
        if not self.on_con_lost.done():
            self.on_con_lost.set_result(True)


async def main():
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPClientProtocol(
            b"Hello UDP server",
            on_con_lost
        ),
        remote_addr=("127.0.0.1", 8080)
    )

    try:
        await asyncio.wait_for(on_con_lost, timeout=3)
    except asyncio.TimeoutError:
        print("No UDP response received before timeout")
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Run `python udp_server.py` in one terminal, then `python udp_client.py`
in another.

Expected output:

``` text
Response: Hello from UDP Server
```

UDP may lose the request or response, so the timeout ensures the demo
finishes if no reply arrives.

### UDP client explanation

-   `__init__` stores the outgoing bytes and a future used to signal
    completion.
-   `connection_made()` runs when the local UDP endpoint is ready, then
    sends the datagram.
-   `sendto(self.message)` sends to the configured peer; no TCP
    handshake is performed.
-   `datagram_received()` handles the reply and closes the transport.
-   `error_received()` reports some asynchronous socket/network errors,
    but cannot detect every lost packet.
-   `connection_lost()` completes the future so `main()` can finish.
-   `create_datagram_endpoint(..., remote_addr=...)` configures a
    default peer. It remains UDP, not a TCP connection.
-   `asyncio.wait_for(..., timeout=3)` waits up to three seconds. This
    timeout is application logic, not a UDP reliability feature.

------------------------------------------------------------------------

# Part V --- Python Syntax and Server Design

## 16. Python syntax used in both servers

### `async def`

Defines a coroutine function:

``` python
async def main():
    ...
```

It can use `await`.

### `await`

``` python
data = await reader.read(1024)
```

Suspends the current coroutine until the asynchronous operation has a
result, allowing other tasks to run.

### Event loop

The event loop coordinates coroutines and I/O callbacks. One event-loop
thread can handle many connections while tasks wait for network I/O,
provided code does not block that thread.

### `while True` and `break`

``` python
while True:
    if condition:
        break
```

Repeats until `break` exits the loop.

### `try` / `finally`

``` python
try:
    ...
finally:
    writer.close()
```

Ensures cleanup runs when control leaves the `try` block, including on
exceptions.

### `str` and `bytes`

``` python
raw = "hello".encode()
text = raw.decode()
```

-   `str` represents text.
-   `bytes` represents byte values.
-   Socket transports send/receive bytes.
-   The application protocol must define encoding (often UTF-8 for
    text).

### F-strings

``` python
print(f"Received {message} from {addr}")
```

Insert values into a string.

### Tuples

``` python
("127.0.0.1", 8080)
```

A pair representing host and port.

### Classes and `self`

``` python
class MyProtocol:
    def connection_made(self, transport):
        self.transport = transport
```

A class defines an object type. `self` refers to the particular object
instance, allowing it to retain values for later callbacks.

### Lambda

``` python
lambda: MyUDPServerProtocol()
```

A small function that returns a protocol instance when called.

### `if __name__ == "__main__":`

Starts the server only when the file is run directly, not when imported
as a module.

------------------------------------------------------------------------

## 17. Build a TCP server from scratch: checklist

Before coding, answer these questions:

1.  **Bind address and port?** Example: `127.0.0.1:8080` for local
    testing.
2.  **How are connections accepted?** `asyncio.start_server()`.
3.  **What runs for each client?** A handler with `reader` and `writer`.
4.  **What is the application protocol?** Define what the bytes mean and
    how a message ends.
5.  **How is data read?** `reader.read()`, `readexactly()`, or a
    protocol-specific framing strategy.
6.  **How is the response sent?** Encode to bytes, `writer.write()`,
    then `await writer.drain()`.
7.  **How are EOF and errors handled?**
8.  **How are resources closed?** `writer.close()` and
    `await writer.wait_closed()`.
9.  **How are many clients handled?** Keep I/O asynchronous; use limits
    and timeouts; don't block the event loop with long CPU work.
10. **How is it secured?** Validate input, define
    authentication/encryption where needed, limit message sizes, log
    safely, and shut down gracefully.

Minimal structure:

``` python
async def handle_client(reader, writer):
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            # Parse data according to your protocol.
            response_bytes = b"response"
            writer.write(response_bytes)
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(
        handle_client,
        host="127.0.0.1",
        port=8080
    )
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
```

The parsing and `response_bytes` must be designed for the application
protocol.

## 18. Build a UDP server from scratch: checklist

1.  Choose local address and port.
2.  Create a protocol class with asyncio's expected callbacks.
3.  Store the transport in `connection_made()`.
4.  Process each datagram in `datagram_received(data, addr)`.
5.  Validate and parse the datagram.
6.  Send replies using `transport.sendto(response_bytes, addr)`.
7.  Define server lifetime and shutdown.
8.  Decide what packet loss means. Add sequence numbers, ACKs, retries,
    deduplication, and timeouts if needed.
9.  Validate datagram sizes and input. UDP services can receive
    unsolicited or spoofed traffic.
10. Implement appropriate congestion-aware behavior for sustained
    traffic.

Minimal structure:

``` python
class MyProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # Validate and parse one datagram.
        response_bytes = b"response"
        self.transport.sendto(response_bytes, addr)


async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        MyProtocol,
        local_addr=("127.0.0.1", 8080)
    )
    try:
        await asyncio.Event().wait()
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
```

`asyncio.Event().wait()` keeps the coroutine alive until cancelled or
signalled; production code should integrate this with the application's
shutdown lifecycle.

------------------------------------------------------------------------

## 19. Final corrections and caveats

-   **TCP is reliable, not infallible.** A connection can fail; handle
    errors and retries at the appropriate level.
-   **TCP is a byte stream.** It does not preserve individual write
    boundaries. Define message framing.
-   **UDP is connectionless, not resource-free.** Sockets, port
    bindings, queues, and OS state still exist.
-   **UDP does not provide built-in congestion control.** Do not blindly
    send at unlimited speed.
-   **UDP is not automatically faster.** The complete design determines
    performance.
-   **Both TCP and UDP use ports.** They have separate port spaces.
-   **HTTP does not always use TCP.** HTTP/1.1 and HTTP/2 commonly use
    TCP; HTTP/3 uses QUIC over UDP.
-   **QUIC is not plain UDP.** It adds reliability, streams, and
    congestion control above UDP.
-   **A UDP response can be lost.** A timeout and retry policy are
    application-level choices.
-   **`reader.read(1024)` is not a complete-message read.** It reads up
    to 1024 bytes from a stream.

## 20. Quick protocol decision guide

  --------------------------------------------------------------------------
  Requirement                Typical starting point  Reason
  -------------------------- ----------------------- -----------------------
  REST API / conventional    HTTP/1.1 or HTTP/2 over Reliable ordered stream
  web app                    TCP                     and mature tooling

  HTTP/3                     QUIC over UDP           QUIC provides
                                                     reliability and streams

  Database connection        Usually TCP             Reliable ordered
                                                     protocol communication

  SSH                        TCP                     Ordered remote
                                                     terminal/session data

  Live voice/video           Often UDP-based media   Fresh media may be more
                                                     useful than late
                                                     retransmission

  Frequent game position     Often UDP               Can prioritize newest
  updates                                            state and tolerate
                                                     selected loss

  Purchases/inventory/game   Reliable protocol plus  Must prevent
  results                    application correctness lost/duplicated
                                                     business actions

  Common DNS query           Often UDP; TCP also     Efficient small
                             used                    request/response

  Telemetry                  Depends on loss         UDP can be lightweight,
                             tolerance               but missing metrics may
                                                     matter
  --------------------------------------------------------------------------

## 21. Final mental model

``` text
IP:
"Which destination network/host should this packet move toward?"

TCP:
"Give the application a reliable, ordered stream of bytes, or report failure."

UDP:
"Send this datagram; delivery and order are not guaranteed."

Port:
"Which transport endpoint should receive the data?"

Application protocol:
"What do these bytes mean?"
```

Python patterns:

``` text
TCP:
start_server()
  → accepted connection
  → handle_client(reader, writer)
  → read/write stream
  → close writer

UDP:
create_datagram_endpoint()
  → bind one datagram socket
  → datagram_received(data, addr)
  → sendto(response, addr)
  → close transport
```

If you understand the transport behavior first, the code becomes much
easier: **TCP manages a stream per accepted connection; UDP handles
individual datagrams arriving at a bound socket.**

------------------------------------------------------------------------

## Sources and scope

-   Hussein Nasser, [When to Use UDP vs TCP in Building a Backend
    Application?](https://www.youtube.com/watch?v=qqRYkcta6IE). The
    published outline covers UDP, TCP, chat systems, multiplayer games,
    browsers/web servers, and summary.
-   Python code explanations are based on the supplied examples and
    Python's `asyncio` stream/datagram programming model.
-   Accuracy notes distinguish protocol guarantees from simplified
    analogies, so these notes can serve as a practical backend
    reference.


---

# 16. The Missing Connection: How My HTTP Backends Worked Without Me Writing TCP or UDP

This chapter connects the networking concepts to the backends you have already built with Node.js, Express, React clients, databases, and APIs. It is an addition to the earlier material, not a replacement for it.

## 16.1 The core doubt

You have written code such as:

```javascript
app.get("/users", async (req, res) => {
  const users = await User.find();
  res.json(users);
});

app.post("/users", async (req, res) => {
  const user = await User.create(req.body);
  res.status(201).json(user);
});
```

You may reasonably ask:

- Where did I create the TCP server?
- Where did I create the UDP server?
- How did the browser send my HTTP request if I only wrote an Express route?
- How did my server send the response?
- If TCP and UDP are responsible for network communication, why did I only think about HTTP methods?

**Answer:** Your route code describes what your application should do after an HTTP request reaches it. A framework and runtime create or use the underlying network socket and implement the lower-level protocol work. In a typical HTTP/1.1 backend, TCP is used underneath HTTP, even though you did not call TCP APIs directly.

You normally do **not** create a UDP server just to build a REST API. UDP is not the usual transport for HTTP/1.1 or HTTP/2. HTTP/3 is the important exception: it runs over QUIC, which uses UDP.

## 16.2 Think in layers: each layer has a different job

A typical HTTP/1.1 request over HTTPS can be pictured like this:

```text
Your application code
  Express route: GET /users
  Reads data, applies business logic, creates JSON
             ↑ HTTP request/response
HTTP layer
  Parses method, path, headers, body, status code
             ↑↓ TLS encryption/decryption for HTTPS
Transport layer
  TCP: ordered byte stream, connection management,
  acknowledgements and retransmission
             ↑↓
Internet layer
  IP: addressing and routing packets between hosts
             ↑↓
Link / physical network
  Ethernet, Wi-Fi, radio signals, cables, etc.
```

This diagram is conceptual. The exact implementation is distributed across libraries, the runtime, the operating system, and network hardware. TLS sits between HTTP and TCP in the common HTTPS-over-TCP stack.

Each layer has a separate responsibility:

| Layer/protocol | Main question it answers |
|---|---|
| HTTP | What does this request mean? Which method, path, headers, and body? |
| TLS (for HTTPS) | How are application bytes encrypted and authenticated? |
| TCP | How do the two endpoints exchange an ordered stream of bytes reliably? |
| IP | How are packets addressed and routed between hosts? |
| Wi-Fi/Ethernet/etc. | How does data travel across a particular local link? |

HTTP methods are **not** TCP or UDP commands. `GET`, `POST`, `PUT`, and `DELETE` describe application-level operations. TCP does not know that a byte sequence represents `POST /users`; it transports bytes.

## 16.3 What happened when you built an Express backend?

Consider a simplified server:

```javascript
const express = require("express");
const app = express();

app.use(express.json());

app.get("/hello", (req, res) => {
  res.json({ message: "Hello" });
});

app.listen(3000, () => {
  console.log("Server listening on port 3000");
});
```

Conceptually, these lines have different responsibilities:

1. `require("express")` loads the HTTP application framework.
2. `express()` creates the application object that will hold middleware and routes.
3. `express.json()` registers middleware that parses JSON request bodies when appropriate.
4. `app.get("/hello", ...)` registers an application-level rule: if an incoming HTTP request matches the `GET` method and `/hello` path, run this handler.
5. `app.listen(3000, ...)` asks Express/Node.js to start listening for incoming HTTP connections on port `3000`.

The last line is the crucial connection. You did not write `socket()`, `bind()`, `listen()`, `accept()`, or a TCP state machine yourself. Node.js provides the HTTP server and socket APIs, and the operating system provides the underlying networking implementation. The exact internal sequence depends on the runtime and platform, but the abstraction is what matters.

In low-level Python TCP examples, you explicitly see operations such as:

```python
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 8080))
server.listen()
connection, address = server.accept()
```

In Express, `app.listen(...)` hides much of that lower-level setup. It does **not** mean the networking work disappeared; it means the framework/runtime performs it for you.

> **Important distinction:** Express is not itself a TCP replacement. It is an HTTP framework. Node.js's HTTP server and socket layer connect the HTTP framework to the operating system's networking facilities.

## 16.4 End-to-end journey: browser/client → your backend

Suppose your React frontend executes:

```javascript
const response = await fetch("https://api.example.com/users", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Asha" })
});

const result = await response.json();
```

Here is the conceptual journey for a typical HTTPS request using HTTP/1.1 or HTTP/2 over TCP.

### Sender side: your browser or frontend runtime

1. **Your JavaScript describes an HTTP request.** It supplies a URL, method, headers, and body. `fetch()` is a high-level API; you do not manually construct TCP segments.
2. **The HTTP implementation prepares the request.** It handles the selected HTTP version's rules for representing the request. HTTP/1.1 has a textual request format; HTTP/2 uses binary frames. Your code does not need to serialize those details itself.
3. **The client establishes or reuses a connection.** For HTTP/1.1 or HTTP/2 over HTTPS, this commonly means a TCP connection, with TLS established for HTTPS. Connections may be reused, so a new TCP handshake is not necessarily required for every request.
4. **The data goes through the stack.** HTTP data is protected by TLS when HTTPS is used, passed to TCP as a byte stream, and carried in IP packets over the network. TCP segments and IP packets are not the same thing as HTTP requests.
5. **The network transports the data.** Routers forward IP packets. The receiver's TCP stack processes the arriving segments and makes the ordered byte stream available to the receiving application.

DNS lookup may occur before connection establishment to resolve the hostname to an address, unless a usable cached result is available. That lookup is a separate step; it is not the HTTP request itself.

### Receiver side: your backend machine

6. **The server's operating system receives network traffic.** IP delivers traffic to the appropriate host and transport endpoint. TCP processes the segments and makes ordered stream bytes available to the listening/accepted socket.
7. **The server runtime reads bytes from the socket.** Node.js's HTTP server interprets those bytes according to the HTTP protocol. With HTTPS, TLS processing also takes place before the HTTP layer sees plaintext HTTP data.
8. **The HTTP parser reconstructs the request.** It identifies the method, target path, headers, and any body according to the HTTP version's rules.
9. **Express matches the request to middleware and a route.** For `POST /users`, the JSON middleware can parse the body, and the matching route handler executes.
10. **Your application performs its job.** It validates data, queries or updates a database, applies authorization/business rules, and creates a response.
11. **Your handler creates an HTTP response.** For example, `res.status(201).json(user)` tells Express to produce a response with status `201 Created` and a JSON representation. Express handles HTTP formatting and response headers.
12. **The response travels back down the stack.** The HTTP server gives response bytes to the transport side; TLS encrypts them for HTTPS; TCP transports an ordered stream back to the client; IP and the network carry packets toward the client.
13. **The client processes the response.** The browser/client's networking stack receives the data, the HTTP implementation reconstructs the response, and `fetch()` resolves to a `Response` object. Calling `response.json()` parses the response body as JSON.

The response follows the same general layered model in reverse. TCP does not decide what `201 Created` means; HTTP does. TCP's job is to transport the bytes carrying that status and body.

## 16.5 A sequence diagram of the request

```text
React / Browser       HTTP + TCP stack       Network       Server stack       Node / Express       Database
      |                       |                  |                 |                   |                 |
      | fetch(POST /users)     |                  |                 |                   |                 |
      |---------------------->|                  |                 |                   |                 |
      |                       | TCP/TLS as needed|                 |                   |                 |
      |                       |----------------->|---------------->|                   |                 |
      |                       |                  |                 | HTTP bytes parsed |                 |
      |                       |                  |                 |------------------>|                 |
      |                       |                  |                 |                   | query/insert    |
      |                       |                  |                 |                   |---------------->|
      |                       |                  |                 |                   |<----------------|
      |                       |                  |                 |<------------------| JSON + status   |
      |                       |<-----------------|<----------------|                   |                 |
      | HTTP response received|                  |                 |                   |                 |
      |<----------------------|                  |                 |                   |                 |
      | response.json()       |                  |                 |                   |                 |
```

This is an illustrative sequence, not a packet capture. Real systems may reuse connections, use proxies/load balancers, run middleware, or communicate with databases over separate connections.

## 16.6 Why you did not write a UDP server for your REST APIs

For ordinary REST APIs, the common arrangement is:

```text
React / browser
    |
    | HTTP request
    | commonly HTTP/1.1 or HTTP/2 over TCP + TLS
    v
Node.js / Express backend
    |
    | database-specific protocol, commonly over TCP
    v
Database
```

You use UDP only if the application or a protocol in the stack needs it. Examples include DNS queries in common configurations, real-time media, certain game traffic, and QUIC/HTTP/3. Even these examples have protocol-specific details and exceptions.

If your backend uses `fetch()` to call another HTTP service, that client library handles the HTTP connection and transport details. If it uses a database driver, the driver handles the database protocol and its socket communication. You usually write business logic rather than raw networking code.

You can build a UDP server in Python to learn datagrams or support a UDP-based protocol, but you would not normally replace an Express HTTP server with a basic UDP echo server and expect browsers to speak ordinary HTTP to it. A UDP socket does not automatically understand HTTP request semantics.

## 16.7 What if TCP delivers data in pieces?

This is one of the most important details when moving from HTTP frameworks to raw sockets.

TCP is a **byte stream**, not a message-delivery system. If a client writes bytes that represent one HTTP request, a server reading from a raw TCP socket might receive those bytes in multiple reads—or, depending on timing and buffering, more than one logical piece of data in one read.

For example, the sender might write:

```text
POST /users HTTP/1.1\r\n
Content-Type: application/json\r\n
Content-Length: 16\r\n
\r\n
{"name":"Asha"}
```

A raw TCP server cannot assume that one `recv(1024)` returns the entire request. It might receive only the beginning, then receive the rest in a later read. Nor should it assume each `send()` corresponds to one `recv()`.

An HTTP server solves this by parsing the HTTP protocol and reading enough data to identify the complete headers and body according to the HTTP rules. It uses framing information such as `Content-Length` or chunked transfer coding in HTTP/1.1, as applicable. HTTP/2 uses its own frame structure.

That is why your Express route receives a parsed `req` object rather than asking you to manually combine TCP chunks, find the end of the headers, and determine the body length.

**The route handler is invoked after the HTTP server has done the protocol parsing needed to expose a request.** This does not mean every body is necessarily loaded into memory before the handler runs; streaming requests and bodies have their own behavior.

## 16.8 The difference between a port, an HTTP route, and a method

These are three different concepts:

- **Port**, such as `3000` or `443`: identifies a transport endpoint on a host. TCP port `3000` and UDP port `3000` are distinct transport endpoints.
- **HTTP method**, such as `GET` or `POST`: indicates the intended operation in an HTTP request.
- **HTTP path**, such as `/users/42`: identifies the target resource/endpoint within the HTTP application.

For example:

```javascript
app.get("/users", handler);
app.post("/users", handler);
```

These are two HTTP route definitions that can share the same listening port and underlying server. The HTTP server receives the request, then Express chooses a handler based on the method and path. You do not need a separate TCP port for each method.

A TCP connection is not equivalent to one HTTP route or one HTTP request. A connection can carry multiple HTTP requests over time; HTTP/2 can multiplex multiple streams over a single TCP connection.

## 16.9 Where HTTPS and port 443 fit

When you visit `https://example.com`, the URL scheme indicates HTTPS. In the common HTTP/1.1-over-TCP or HTTP/2-over-TCP case, the simplified stack is:

```text
HTTP
TLS encryption
TCP
IP
Network link
```

TLS protects the HTTP data in transit and authenticates the server using certificates. TCP transports the encrypted bytes as an ordered stream. Port `443` is the default port associated with HTTPS, but a service can use other ports too.

Do not confuse the URL scheme with the transport protocol: **HTTPS does not mean UDP.** HTTP/3 is also HTTPS, but it uses HTTP/3 over QUIC over UDP. The browser and server negotiate supported protocols; application code commonly continues to use high-level APIs.

## 16.10 What changes with HTTP/3?

The familiar HTTP route abstraction can still exist, but the transport beneath it changes:

```text
HTTP/1.1 -> usually TCP
HTTP/2   -> TCP
HTTP/3   -> QUIC -> UDP
```

QUIC provides transport features including reliable streams, congestion control, and connection management over UDP. HTTP/3 does not simply send unstructured HTTP requests through a bare UDP socket. QUIC adds the mechanisms needed for HTTP/3's transport behavior.

Therefore, the statement “HTTP uses TCP” is a useful rule for many traditional backends but is not universally true for every HTTP version.

## 16.11 How this relates to your database and backend projects

Your backend often communicates over more than one connection:

```text
Browser / React
    |
    | HTTP API request
    v
Express / FastAPI application
    |
    | Database driver's protocol (commonly over TCP)
    v
MongoDB / PostgreSQL / MySQL / Redis, depending on setup
```

The browser-to-backend HTTP connection and backend-to-database connection are separate connections. Your route may receive an HTTP request, then the database driver sends a different protocol to the database. The database returns its own protocol response, and your application turns the result into an HTTP response.

Similarly, when your backend calls an external HTTP API, that is another client-side connection. It does not reuse the incoming browser connection as a direct connection to the external service.

This means that a single user action may involve several independent networking conversations. Each has its own endpoints, protocol, timeout, error handling, and connection lifecycle.

## 16.12 What you were responsible for versus what the framework handled

| Concern | In your Express/FastAPI route code | Usually handled by runtime/framework/OS |
|---|---|---|
| Choosing endpoint behavior | Yes | Framework dispatches matching route |
| Reading application data | Yes | Database driver performs network I/O |
| Validating and authorizing requests | Usually yes | Some validation/auth helpers may assist |
| Constructing application response data | Yes | Framework serializes JSON and formats HTTP |
| Parsing HTTP syntax | Usually no | HTTP server/framework |
| Creating/listening on sockets | Usually no | Runtime/server API and OS |
| TCP sequence numbers and acknowledgements | No | TCP implementation in OS/runtime stack |
| IP routing and link-layer transmission | No | OS and network infrastructure |
| TLS encryption/certificate processing | Usually no | TLS library/server/client stack, configured by application or infrastructure |
| Retries and application-level idempotency | Depends | Some libraries retry; application must understand semantics |

The boundaries vary by framework, deployment model, reverse proxy, and configuration. For example, TLS might terminate at a load balancer rather than inside Node.js or FastAPI.

## 16.13 What changes when you write a raw TCP server?

When you write a raw TCP server, you step below HTTP:

```text
Client bytes
    |
    v
TCP socket
    |
    v
Your application code must define the message format
```

You can send JSON, a custom binary format, or even manually constructed HTTP bytes. TCP only provides the stream. If you invent your own protocol, you must define how messages start and end, how large they can be, what fields mean, how errors are represented, and how versioning works.

A minimal TCP echo server can simply return whatever bytes it reads. It is a TCP server, but not automatically an HTTP server. To become an HTTP server, it must parse HTTP correctly—or delegate that work to an HTTP library.

## 16.14 What changes when you write a raw UDP server?

UDP provides individual datagrams:

```text
Client datagram
    |
    v
UDP socket
    |
    v
Your application processes one received datagram
```

Your code receives a datagram and its sender address, then may send a response datagram to that address. UDP does not provide TCP-style delivery guarantees, ordered byte-stream semantics, or retransmission of lost datagrams. If your application needs reliability, ordering, congestion handling, or request correlation, it must use a protocol that supplies those properties or implement suitable mechanisms itself.

A raw UDP echo server is not an HTTP server. A protocol such as QUIC can use UDP while providing richer transport behavior above it.

## 16.15 Final mental model

When you build an API, you normally work at the **HTTP application layer**:

- You choose routes and HTTP methods.
- You inspect request data and headers.
- You implement authentication, validation, business logic, and database operations.
- You return a status code, headers, and response body.

Meanwhile, lower layers carry the request and response between machines:

- HTTP defines the request/response semantics and message framing.
- TLS may encrypt and authenticate the application data.
- TCP commonly carries HTTP/1.1 and HTTP/2 as an ordered byte stream.
- QUIC over UDP carries HTTP/3.
- IP routes packets between hosts.
- The operating system, runtime, framework, and network infrastructure do much of the work you did not write manually.

So your past backends worked **not because TCP and UDP were unnecessary, but because the HTTP server, runtime, libraries, and operating system handled the transport plumbing beneath your application code**. You chose the application behavior; the stack delivered the bytes.

### Quick self-check

1. Does `app.post("/users", handler)` create a separate TCP connection for that route? **No.** It registers HTTP behavior on the application server.
2. Does TCP understand `POST`? **No.** TCP transports bytes; the HTTP implementation interprets the method.
3. Does `app.listen(3000)` mean no TCP socket exists? **No.** It starts a listening HTTP server using the runtime/OS networking facilities.
4. Is every HTTP version carried over TCP? **No.** HTTP/1.1 and HTTP/2 commonly use TCP; HTTP/3 uses QUIC over UDP.
5. Does one TCP `recv()` always return one complete HTTP request? **No.** TCP is a byte stream, so the HTTP implementation must parse the protocol framing.
6. Does a database query reuse the browser's HTTP connection? **No, not normally.** The application uses a separate database connection and protocol.
7. Do you need to learn raw TCP/UDP to build ordinary APIs? **Not to get started.** But understanding them helps you debug connections, timeouts, streaming, performance, and real-time systems.

