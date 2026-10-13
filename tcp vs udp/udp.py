import asyncio

class MyudpserverProtocol :
    def connection_made(self ,transport) :
        self.transport = transport 


    def datagram_received(self, data, addr) :
        message = data.decode()
        print(f"Received {message} from {addr}")
        
        self.transport.sendto(b"Hello from UDP Server", addr)
    

async def main() :
    loop = asyncio.get_running_loop()
    
    transport , protocol = await loop.create_datagram_endpoint(
        lambda : MyudpserverProtocol(),
        local_addr = ('127.0.0.1', 8080)


    )
    print("UDP server started runnnig on port 8080")

    try :
        await asyncio.sleep(3600)
    finally :
        transport.close()

if __name__ == "__main__" :
    asyncio.run(main())
