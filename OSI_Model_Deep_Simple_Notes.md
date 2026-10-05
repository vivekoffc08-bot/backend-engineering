# OSI Model — Deep but Simple Notes

## 1. What is the OSI Model?

The **OSI (Open Systems Interconnection) model** is a conceptual model that helps us understand how data travels from one application/device to another.

It has **7 layers**:

```text
7. Application
6. Presentation
5. Session
4. Transport
3. Network
2. Data Link
1. Physical
```

Important:

> The OSI model is a **conceptual model**, not necessarily seven separate pieces of code running on every device.

Real-world Internet networking is usually described using the **TCP/IP model**, but OSI is extremely useful for understanding what each part of networking is responsible for.

---

# 2. Start With One Simple Question

Suppose you open your browser and request:

```text
https://example.com/users
```

Your application eventually needs to send something like:

```http
GET /users
Host: example.com
```

How does this data travel from your laptop to a server somewhere on the Internet?

Conceptually:

```text
Your Application
       ↓
Application-level data
       ↓
Transport
       ↓
Network
       ↓
Data Link
       ↓
Physical signal
       ↓
Internet
       ↓
Server
       ↓
Reverse process
       ↓
Server Application
```

The OSI model divides this huge problem into smaller responsibilities.

---

# 3. Layer 1 — Physical Layer

### Question:

> **How do I physically transmit the bits?**

This is the lowest layer.

At this level we are concerned with actual physical signals.

Examples:

```text
Wi-Fi       → Radio waves
Ethernet    → Electrical signals
Fiber optic → Light
Bluetooth   → Radio waves
```

You can think:

```text
Bits
 ↓
Encoding/modulation
 ↓
Physical signal
 ↓
Medium
```

### Important correction

It is common to say:

> "The physical layer sends binary."

That's useful as a beginner explanation, but the physical medium doesn't literally contain floating `1`s and `0`s.

The computer has bits:

```text
101101001...
```

Those bits are encoded into physical signals.

So:

```text
Computer data
     ↓
101101001...
     ↓
Encoding/modulation
     ↓
Radio/electrical/light signal
```

---

# 4. Layer 2 — Data Link Layer

### Question:

> **Which device on this local network should receive this data?**

This is where things like:

- MAC addresses
- Frames
- Ethernet
- Wi-Fi

come into the picture.

A simplified frame looks like:

```text
+------------------------------------------------+
| Destination MAC | Source MAC | Data | FCS      |
+------------------------------------------------+
```

For example:

```text
Destination MAC → Router
Source MAC      → Laptop
```

### Layer 1 vs Layer 2

This is one of the most important distinctions.

### Layer 1

Deals with:

```text
Signals
Bits
Radio
Electricity
Light
```

### Layer 2

Deals with:

```text
Frames
MAC addresses
Local network delivery
```

So:

> **Layer 1 moves the physical signal. Layer 2 gives that local communication structure and addressing.**

---

# 5. What Happens With Wi-Fi?

Suppose your home network is:

```text
                 Wi-Fi Router
                /     |      \
               /      |       \
            Laptop   Phone     TV
```

Wi-Fi is a shared wireless medium.

A radio transmission propagates through the surrounding area, so multiple devices may be able to receive the transmission.

The frame contains addressing information.

For example:

```text
Destination MAC = Router's MAC
Source MAC      = Laptop's MAC
```

A device's network interface can determine whether the frame is meant for it and normally discard frames that aren't intended for further processing by that device.

So your understanding:

> "Wi-Fi sends data around and devices ignore data not meant for them"

is **roughly pointing in the right direction**, but don't think of it as every packet being separately sent to every device.

Broadcast, multicast, unicast, Wi-Fi transmission modes, access points, switches, etc. make the real behavior more nuanced.

The key idea is:

> **Layer 2 handles local delivery using MAC addresses.**

---

# 6. Layer 3 — Network Layer

### Question:

> **Which network/device should this packet ultimately reach?**

This is where **IP addresses** and **routing** come in.

Imagine:

```text
YOUR LAPTOP
     |
   ROUTER
     |
    ISP
     |
  INTERNET
     |
GOOGLE SERVER
```

Your laptop and Google's server aren't on the same local network.

Layer 2 alone isn't enough.

Layer 3 provides the mechanism for communicating across different networks.

Example:

```text
Source IP:
192.168.1.10

Destination IP:
Server's IP address
```

Routers use IP information to decide where the packet should go next.

Conceptually:

```text
Packet
  ↓
Router A
  ↓
"Where next?"
  ↓
Router B
  ↓
"Where next?"
  ↓
Router C
  ↓
Destination
```

This is **routing**.

### Remember:

```text
MAC → Local delivery
IP  → Network-to-network delivery
```

---

# 7. Layer 4 — Transport Layer

### Question:

> **Which application/service on that device should receive the data, and how should the data be delivered?**

Common transport protocols:

```text
TCP
UDP
```

This is where **ports** become important.

Suppose your computer is:

```text
192.168.1.10
```

and your FastAPI server is running on:

```text
Port 8000
```

Then conceptually:

```text
192.168.1.10:8000
```

means:

> Go to this device and specifically to the service listening on port 8000.

TCP also provides things such as reliable, ordered delivery.

UDP does not provide the same reliability guarantees.

---

# 8. The House and Door Analogy

Your analogy is actually very useful.

Think of:

```text
Device = House
IP address = House address
Port = Door
Application = Something listening behind the door
```

For example:

```text
                    DEVICE
                      │
              IP: 192.168.1.10
                      │
       ┌──────────────┼──────────────┐
       │              │              │
     Port 22        Port 3000      Port 8000
       │              │              │
      SSH          Node.js        FastAPI
```

So:

```text
192.168.1.10:8000
```

means:

```text
House address + Door number
```

The OS can then deliver the incoming data to the application that is listening on that port.

---

# 9. Are Ports Infinite?

No.

For TCP:

```text
0 → 65535
```

For UDP:

```text
0 → 65535
```

So there are **65,536 possible port numbers for TCP** and separately **65,536 possible port numbers for UDP**.

TCP port `8000` and UDP port `8000` are therefore separate.

But this does NOT mean every port is being used.

Most ports are normally:

```text
unused
```

Only applications/services that need to receive connections listen on particular ports.

For example:

```text
:22   → SSH
:80   → HTTP
:443  → HTTPS
:3000 → Node.js application
:8000 → FastAPI application
:5432 → PostgreSQL
```

These are conventional/default ports, not strict requirements.

For example, your FastAPI application could technically run on `9000` instead of `8000`.

---

# 10. Layer 5 — Session Layer

### Question:

> **How do we manage an ongoing communication session?**

Conceptually, a session involves things like:

```text
Start
 ↓
Communication
 ↓
Synchronization/state
 ↓
More communication
 ↓
End
```

But there is an important real-world detail:

> Modern Internet networking does not usually have a literal, independent "Session Layer program."

Session functionality is often handled by higher-level protocols/applications.

So don't imagine:

```text
Operating System
 ├── Layer 1 process
 ├── Layer 2 process
 ├── Layer 3 process
 ├── Layer 4 process
 ├── Layer 5 process  ← ❌ not necessarily like this
 ├── Layer 6 process
 └── Layer 7 process
```

OSI describes responsibilities; real implementations can combine them differently.

---

# 11. Layer 6 — Presentation Layer

### Question:

> **How should the data be represented?**

This layer is conceptually concerned with things such as:

- Encoding
- Serialization
- Compression
- Encryption
- Decryption
- Data representation/translation

For example:

```text
Application data
      ↓
Encoding
      ↓
Compression
      ↓
Encryption
      ↓
Bytes
```

Examples of data representations include:

```text
JSON
XML
UTF-8
JPEG
PNG
```

Encryption is commonly associated with the Presentation Layer in OSI explanations.

However:

> Real-world protocols don't always fit perfectly into OSI layers.

For example, TLS is often discussed around the Presentation/Application boundary rather than being a literal Layer-6 component.

---

# 12. Layer 7 — Application Layer

### Question:

> **What does this communication actually mean to the application?**

This is where application-level protocols live.

Examples:

```text
HTTP / HTTPS
DNS
SMTP
FTP
SSH
```

For example:

```http
GET /users HTTP/1.1
Host: example.com
Authorization: Bearer ...
Cookie: ...
```

Your:

```text
FastAPI
Node.js
React
Browser
```

applications interact heavily with this layer.

### Cookies

Cookies are not a generic "OSI feature."

They are an **HTTP/application-level mechanism**.

---

# 13. Follow One Request Through Everything

Suppose your browser requests:

```text
https://example.com/users
```

The application wants to send:

```http
GET /users
Host: example.com
```

Conceptually:

## Layer 7 — Application

HTTP creates the request:

```http
GET /users
Host: example.com
```

---

## Layer 6 — Presentation

Data may be:

```text
Encoded
Compressed
Encrypted using TLS
```

depending on the protocol stack.

Conceptually:

```text
HTTP data
   ↓
TLS encryption
   ↓
Encrypted bytes
```

---

## Layer 5 — Session

Session-related state/communication management may be involved.

Again, don't expect a literal Layer-5 component in the OS.

---

## Layer 4 — Transport

TCP may add information such as:

```text
Source port:      54321
Destination port: 443
```

Conceptually:

```text
+---------------------------+
| Source Port: 54321        |
| Destination Port: 443     |
|                           |
| HTTP/TLS data             |
+---------------------------+
```

Port `443` is commonly used for HTTPS.

---

## Layer 3 — Network

IP information is added:

```text
Source IP
Destination IP
```

Conceptually:

```text
+--------------------------------+
| Source IP                      |
| Destination IP                 |
|                                |
| TCP segment                    |
+--------------------------------+
```

Now routers can route the packet.

---

## Layer 2 — Data Link

Your laptop needs to communicate with the next device on the local network, such as your router.

Conceptually:

```text
+--------------------------------+
| Destination MAC                |
| Source MAC                     |
|                                |
| IP packet                      |
+--------------------------------+
```

---

## Layer 1 — Physical

Finally:

```text
Frame
 ↓
Bits
 ↓
Encoding
 ↓
Radio/electrical/light signal
 ↓
Physical medium
```

And the signal leaves your computer.

---

# 14. Encapsulation

This is one of the most important networking concepts.

The higher layers produce data.

Lower layers wrap that data with their own information.

Conceptually:

```text
Application data
       ↓
   + TCP
       ↓
   + IP
       ↓
   + Ethernet/Wi-Fi
       ↓
Physical signal
```

You can think of it like putting a letter inside multiple envelopes.

```text
HTTP DATA
   ↓
TCP wrapper
   ↓
IP wrapper
   ↓
Wi-Fi/Ethernet wrapper
   ↓
Physical transmission
```

At the destination, the reverse process happens.

This is called **decapsulation**.

---

# 15. What Happens at the Server?

The server receives the physical signal.

Then the information is processed upward:

```text
Physical
   ↓
Data Link
   ↓
Network
   ↓
Transport
   ↓
Session
   ↓
Presentation
   ↓
Application
```

Eventually the server's application receives the HTTP request.

For example:

```text
Internet
   ↓
Server network hardware
   ↓
Operating System
   ↓
TCP/IP stack
   ↓
Web server / Uvicorn
   ↓
FastAPI
   ↓
@app.get("/users")
```

---

# 16. Routers Don't Need to Understand Your HTTP Request

This is another very important idea.

Suppose you send:

```http
GET /users
```

to a server.

An intermediate router doesn't need to read:

```text
GET /users
```

It mainly needs to know:

```text
Where should this IP packet go next?
```

Think of a postal system.

If you send:

```text
Vivek
Kalyan
Maharashtra
India
```

to someone in another country, an intermediate post office doesn't need to open the letter and read its contents.

It mainly needs the address.

Similarly:

```text
HTTP → Application
TCP  → Transport
IP   → Routing
MAC  → Local delivery
```

Different parts of the network care about different information.

---

# 17. Where Are These Layers Actually Implemented?

This is where things get really interesting.

They are implemented using a combination of:

```text
Software
Operating System
Kernel
Drivers
Firmware
Hardware
```

For example, your FastAPI application:

```text
FastAPI
   ↓
Uvicorn
   ↓
Python socket API
   ↓
Operating System networking stack
   ↓
TCP/IP
   ↓
Network driver
   ↓
Wi-Fi/Ethernet hardware
   ↓
Radio/electrical signal
```

Your Python code doesn't implement TCP/IP itself.

The operating system does most of the networking work underneath your application.

---

# 18. What About a Mac, Phone, TV, etc.?

Yes — practically every modern network-capable device participates in these networking concepts.

Examples:

```text
Mac
iPhone
Android phone
Smart TV
PlayStation
IoT device
Server
Router
```

A Smart TV might have:

```text
Netflix app
    ↓
HTTP/HTTPS
    ↓
TCP/IP or another transport/network stack
    ↓
Wi-Fi driver
    ↓
Wi-Fi hardware
    ↓
Radio
```

Your phone does similar things.

The exact implementation differs from device to device.

---

# 19. Do These Layers Constantly Run?

The networking subsystem is always available, but that does NOT mean your device is constantly sending useful application data.

When networking is active, the relevant components can handle things such as:

```text
Wi-Fi management
DNS
TCP connections
UDP traffic
Notifications
Background synchronization
Application traffic
Routing
```

When Netflix is playing:

```text
Netflix
 ↓
Application protocol
 ↓
Transport
 ↓
IP
 ↓
Wi-Fi
 ↓
Radio
```

When WhatsApp receives a message:

```text
Network packet
 ↓
OS networking stack
 ↓
Appropriate socket
 ↓
WhatsApp process
 ↓
Message displayed
```

---

# 20. Data Names at Different Layers

Different layers use different terminology.

A simplified version:

```text
Layer 7 → Data
Layer 6 → Data
Layer 5 → Data
Layer 4 → TCP Segment / UDP Datagram
Layer 3 → IP Packet
Layer 2 → Frame
Layer 1 → Bits / Signals
```

So:

```text
Application data
       ↓
TCP Segment
       ↓
IP Packet
       ↓
Wi-Fi/Ethernet Frame
       ↓
Bits/Signals
```

This terminology is useful when reading networking documentation.

---

# 21. The Most Important Mental Model

Don't just memorize the seven layer names.

Ask a question at each layer:

```text
L7  What am I doing?
    → HTTP, DNS, SSH, etc.

L6  How is my data represented?
    → Encoding, encryption, compression

L5  What communication session am I maintaining?
    → Session management

L4  Which application/service?
    → TCP/UDP + Port

L3  Which network/device?
    → IP + Routing

L2  Which local device?
    → MAC + Frame

L1  How do the bits physically travel?
    → Radio/Electricity/Light
```

---

# 22. The Complete Picture

```text
                  YOUR FASTAPI APP
                         │
                         │
                  HTTP / HTTPS
                         │
              ┌──────────▼──────────┐
              │ APPLICATION         │ L7
              ├─────────────────────┤
              │ PRESENTATION        │ L6
              ├─────────────────────┤
              │ SESSION             │ L5
              ├─────────────────────┤
              │ TCP / UDP           │ L4
              │ PORT                │
              ├─────────────────────┤
              │ IP                  │ L3
              │ ROUTING             │
              ├─────────────────────┤
              │ MAC / FRAME         │ L2
              │ Wi-Fi / Ethernet    │
              ├─────────────────────┤
              │ BITS / SIGNAL       │ L1
              │ RADIO / ELECTRIC    │
              └──────────┬──────────┘
                         │
                         ▼
                     INTERNET
                         │
                         ▼
                  SERVER'S NETWORK
                         │
                    L1 → L7
                    REVERSE
                         │
                         ▼
                    SERVER APP
```

---

# 23. The Developer Connection

When you write:

```python
@app.get("/users")
def users():
    return {"users": [...]}
```

you are mainly working at the application level.

But underneath:

```text
FastAPI
   ↓
Uvicorn
   ↓
Python socket API
   ↓
Operating System
   ↓
TCP
   ↓
IP
   ↓
Wi-Fi/Ethernet
   ↓
Network hardware
   ↓
Physical signal
```

So your API is only the **top layer of a huge networking system**.

This is why concepts such as:

```text
localhost
IP
port
socket
TCP
HTTP
headers
cookies
Wi-Fi
router
NAT
firewall
```

are all connected.

---

# 24. Final Quick Revision

```text
L7 Application
→ What does the application want?
→ HTTP, DNS, SSH, etc.

L6 Presentation
→ How is the data represented?
→ Encoding, compression, encryption

L5 Session
→ How is an ongoing communication session managed?

L4 Transport
→ Which application/service?
→ TCP/UDP + PORT

L3 Network
→ Where is the destination?
→ IP + ROUTING

L2 Data Link
→ Which local device?
→ MAC + FRAME

L1 Physical
→ How do the bits physically travel?
→ Radio / Electricity / Light
```

### One-line memory trick:

```text
Application → Meaning
Presentation → Format
Session      → Conversation
Transport    → Port
Network      → IP
Data Link    → MAC
Physical     → Signal
```

### And the house analogy:

```text
Device       = House
IP address   = House address
Port         = Door
Application  = Service/person behind the door
MAC address  = Local identity/address used on the local network
```

The most important distinction to remember:

```text
MAC → "Which device locally?"
IP  → "Which device/network ultimately?"
Port → "Which application/service on that device?"
```

And the most important flow:

```text
Application
    ↓
TCP/UDP
    ↓
IP
    ↓
MAC
    ↓
Physical signal
```

At the destination:

```text
Physical signal
    ↓
MAC
    ↓
IP
    ↓
TCP/UDP
    ↓
Application
```
