"""
A front-end for MultiChat.
"""

import json
import asyncio
import websockets

RETRY_INTERVAL = 10 # 10s

class MultiChatWS():
    """
    Websocket connected to MultiChat-Server.
    """

    def __init__(self, config=None):
        self.config = config
        if config:
            self.url = config['multichat-url'].rstrip('/') + '/'
            self.key = config['multichat-key']
        self.ws_valid = False

    
    async def _run(self, qqws):
        self.ws = await websockets.connect(self.url)
        # register
        register_obj = {
            'action': 'register',
            'client-name': 'QQ-' + qqws.name if qqws.name else 'QQ',
            'secret-key': self.key
        }
        await self.ws.send(json.dumps(register_obj))
        ack = await self.ws.recv()
        print('mc connect: ' + ack)
        ack = json.loads(ack)
        if ack['action'] == 'register-ack':
            self.ws_valid = True
        while True:
            recv_data = await self.ws.recv()
            data = json.loads(recv_data)
            if data['action'] == 'forwarding-message':
                source = data['source-client-name']
                content = data['content']
                post_str = '[{}] {}'.format(source, content)
                await qqws.post(post_str)
        
    
    async def run(self, qqws):
        while True:
            try:
                await self._run(qqws)
            except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError):
                pass
            # error occurred.
            self.ws_valid = False
            print('[ERROR] MCWS DISCONNECTED. RETRY IN {}s.'.format(RETRY_INTERVAL))
            await asyncio.sleep(RETRY_INTERVAL)

    
    async def stop(self):
        await self.ws.close()
    
    
    async def post(self, message):
        if self.ws_valid:
            obj = {
                'action': 'client-message',
                'content': message,
            }
            data = json.dumps(obj)
            print('mc send: ' + data)
            await self.ws.send(data)
        