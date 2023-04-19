
import asyncio
import websockets
import redis
import re

ws_port = '5001'

r = redis.Redis(
    host='localhost',
    port=6379,
)
pubsub = r.pubsub()
redis_state_updated = 'state_updated'
# pubsub.subscribe('state_updated')

# async def subscribe_to_redis(path):    
#     conn = await create_connection(('localhost', 6379))    
#     # Set up a subscribe channel    
#     channel = Channel('lightlevel{}'.format(path), is_pattern=False)   
#     await conn.execute_pubsub('subscribe', channel)    
#     return channel, conn



# def redis_handler(websocket, msg):
#     websocket.send(msg)


# create redis handler that will send websocket

# r = redis.Redis(...)
# p = r.pubsub()
# p.subscribe('my-first-channel', 'my-second-channel', ...)
# p.get_message()

channel_connections = {}

async def handler(websocket):
    # await websocket.send(msg)

    # pubsub.subscribe('state_updated')

    print("new connectoin!!!!!!!")
    print(websocket.path)

    channel_id = re.findall('.*channel_id=(.*)', websocket.path)[0]
    print(f"found Channel Id {channel_id}")
    # print(websocket.url)

    pubsub = r.pubsub()
    subsub_channel = f"channel_id_{channel_id}"
    pubsub.subscribe(subsub_channel)

    try:        
        while True:            
            # Wait until data is published to this channel            
            message = pubsub.get_message()
            # Send unicode decoded data over to the websocket client  
            print(message)
            if (message != None and 'data' in message):
                print('sending message to websocket')
                await websocket.send(str(message['data']))
            await asyncio.sleep(3)
            
    except websockets.exceptions.ConnectionClosed as e:        
        # Free up channel if websocket goes down     
        print(e)
        print("websockets exception found")
        pubsub.unsubscribe(subsub_channel)

    # breakpoint()

    # pubsub.subscribe(state_updated= redis_handler)
    # pubsub.subscribe({"test": lambda x : x + 1})
    # pubsub.subscribe()
    # pubsub.run_in_thread(sleep_time=.01)

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with websockets.serve(handler, "localhost", ws_port):
        await asyncio.Future()  # run forever

asyncio.run(main())
