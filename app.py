import asyncio
from flask import Flask, request, redirect, url_for, session
import redis
import websockets
import sys

ws_port = '5001'
domain = 'localhost'
# redis_state_updated = 'state_updated'

app = Flask(__name__)

app.secret_key = 'SOME_SECRET_KEY'
# s = { "sum" : 0 }
s = { }

r = redis.Redis(
    host='localhost',
    port=6379,
)
pubsub = r.pubsub()

# async def handler(websocket):
#     def redis_handler(msg):
#         websocket.send(msg)

#     pubsub.subscribe({redis_state_updated: redis_handler})
#     pubsub.run_in_thread(sleep_time=.01)

    # async for message in websocket:
    #     await websocket.send(message)

# async def main():
#     async with websockets.serve(handler, "localhost", ws_port):
#         await asyncio.Future()  # run forever
 
@app.route("/")
def index():
    return "<div>Home</div>"

@app.route("/channel/<string:channel_id>")
def channel_index(channel_id):
    # async with websockets.connect("ws://localhost:8765") as websocket:
    #     await websocket.send("Hello world!")
    #     await websocket.recv()
    initiate_channel(channel_id)

    if 'username' in session:
        # channel = session["channel"] if 'channel' in session else None
        channel = channel_id
        template = f'''
            <script>
                websocket = new WebSocket("ws://{domain}:{ws_port}?channel_id={channel_id}");
                websocket.addEventListener('error', (event) => {{
                    console.log('WebSocket error: ', event)
                }});         

                websocket.onmessage = (event) => {{
                    console.log(event.data);
                    console.log("ON MESSAGE")
                    // debugger

                    fetch("http://localhost:5000/channel/{channel_id}/sum").then(function(response) {{
                      console.log("lalala")
                      return response.json();
                    }}).then(function(data){{
                      console.log(data)
                      const element = document.getElementById("sum")
                      const span = document.createElement("span");
                      span.innerText = data["sum"]
                      span.id = "sum"
                      element.replaceWith(span)
                    }})

                    // location.reload();
                }}

                websocket.onopen = (event) => {{
                    console.log("Opened new socket connectoin");
                    console.log(event)
                }}


                websocket.addEventListener('input', () => {{
                  console.log("Got a new reload")
                  location.reload();
                }});
            </script>
            <div>Logged in as {session["username"]}</div>
            <div>Channel joined is {channel}</div>
            <div>Sum is <span id="sum">{s[channel_id]['sum']}</span></div>
        '''
        return template
    
    return 'You are not logged in'
    # r.publish('foo', 'LALALALLAALLLA')
    # return "<p>Hello, World!</p>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''    

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/hello')
def hello():
    return 'Hello, World!'


# @app.route('/action', methods=['GET', 'POST'])
# def action_post():
#     s['sum'] += 1
#     r.publish(redis_state_updated, 'updated')
#     return 'Added'

@app.route('/channel/<string:channel_id>/sum/add', methods=['GET', 'POST'])
def channel_sum_add_post(channel_id):
    initiate_channel(channel_id)
    s[channel_id]['sum'] += 1
    r.publish(f"channel_id_{channel_id}", 'updated')

    return 'Added'

@app.route('/channel/<string:channel_id>/sum', methods=['GET'])
def channel_sum_get(channel_id):
    initiate_channel(channel_id)

    return {"sum": s[channel_id]['sum']}

@app.route('/channel/<string:channel_id>/join')
def channel_join(channel_id):
    session['channel'] = channel_id
    return redirect(url_for('index'))

@app.route
def channel_leave():
    session['channel'] = None
    return redirect(url_for('index'))

def initiate_channel(channel_id):
    if channel_id not in s:
        s[channel_id] = {}
        s[channel_id]['sum'] = 0

    
# if len(sys.argv) == 2:
#     if sys.argv[1] == 'run_socket':
#         asyncio.run(main())

