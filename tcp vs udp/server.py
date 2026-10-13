import asyncio



async def handle_client(reader, writer) :
    address = writer.get_extra_info("peername")
    print(f"client connected from address => {address}")

    try :
        while True :
            data =  await reader.read(1024)

            if not data :
                break

            message = data.decode()
            print(f"Received => {message}")
            
            writer.write(f"Server Received : {message}".encode())
            await writer.drain()

    finally :
        writer.close()
        await writer.wait_closed()
        print(f"Connection closed => {address}")



async def main() :
    server = await asyncio.start_server(
        handle_client,
        host = '127.0.0.1',
        port = 8080

    )

    print("Tcp server started on port 8080")
    
    async with server :
        await server.serve_forever()


if __name__ == "__main__" :
    asyncio.run(main())

