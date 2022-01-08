"""
A front-end for MultiChat.
"""

import json
import asyncio
import websockets


class MultiChatWS():
    """
    Websocket connected to MultiChat-Server.
    """

    def __init__(self, config=None):
        self.config = config
        if config:
            self.url = config['multichat-url'].rstrip('/') + '/'
            self.key = config['multichat-key']

    
    async def run(self, qqws):
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
        while True:
            recv_data = await self.ws.recv()
            data = json.loads(recv_data)
            source = data['source-client-name']
            content = data['content']
            post_str = '[{}]{}'.format(source, content)
            await qqws.post(post_str)

    
    async def stop(self):
        await self.ws.close()
    
    
    async def post(self, message):
        obj = {
            'content': message,
        }
        data = json.dumps(obj)
        print('mc send' + data)
        await self.ws.send(data)
        