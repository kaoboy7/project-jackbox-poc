# producer.py
import asyncio from aioredis
import create_connection, Channel
import websocketsasync 

async def subscribe_to_redis(path):    
    conn = await create_connection(('localhost', 6379))    
    # Set up a subscribe channel    
    channel = Channel('lightlevel{}'.format(path), is_pattern=False)   
    await conn.execute_pubsub('subscribe', channel)    
    return channel, conn

async def browser_server(websocket, path):    
    channel, conn = await subscribe_to_redis(path)   
    try:        
        while True:            
            # Wait until data is published to this channel            
            message = await channel.get()            
            # Send unicode decoded data over to the websocket client            
            await websocket.send(message.decode('utf-8'))    
    except websockets.exceptions.ConnectionClosed:        
        # Free up channel if websocket goes down        
        await conn.execute_pubsub('unsubscribe', channel)        
        conn.close()
        
if __name__ == '__main__':    # Runs a server process on 8767. Just do 'python producer.py'    
    loop = asyncio.get_event_loop()    
    loop.set_debug(True)    
    ws_server = websockets.serve(browser_server, 'localhost', 8767)    
    loop.run_until_complete(ws_server)    
    loop.run_forever()

