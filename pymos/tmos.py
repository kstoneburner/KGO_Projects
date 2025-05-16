import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime

async def handle_client(reader, writer):
    try:
        data = await reader.readline()
        if not data:
            return  # No data received, close the connection
        
        # Parse XML data
        root = ET.fromstring(data.decode())
        message_text = root.find('message').text
        
        print(f"[{datetime.now()}] Received: {message_text}")
        
        # Send confirmation back to client
        writer.write("XML received successfully!\n")
        await writer.drain()
    except ET.ParseError as e:
        print(f"Failed to parse XML data: {e}")
    except ConnectionResetError:
        pass  # Client closed the connection abruptly

async def main():
    server = await asyncio.start_server(
        handle_client, 'localhost', 12345)
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())