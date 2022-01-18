"""
A front-end for CQHTTP (running on ws mode).
"""

import json
import asyncio
import websockets


class QQBotWS():
    """
    Websocket connected to CQHTTP (running on websocket mode).
    """
    
    def __init__(self, config=None):
        self.config = config
        if config:
            self.url = config['cqhttp-url'].rstrip('/') + '/'
            self.groups = config['groups'] if 'groups' in config else None
            self.friends = config['friends'] if 'friends' in config else None
            self.name = config['qqbot-name'] if 'qqbot-name' in config else None
        self.listen_groups = set()
        self.listen_friends = set()
        self.group_aliases = {}
        self.post_groups = []
        self.post_friends = []
        if self.groups:
            for group in self.groups:
                if group['listen']:
                    self.listen_groups.add(group['group-id'])
                    if 'alias' in group:
                        self.group_aliases[group['group-id']] = group['alias']
                if group['post']:
                    self.post_groups.append(group['group-id'])
        if self.friends:
            for friend in self.friends:
                if friend['listen']:
                    self.listen_friends.add(friend['user-id'])
                if friend['post']:
                    self.post_friends.append(friend['user-id'])
        self.ws_valid = False
    
    
    async def _send_group_msg(self, group_id, message):
        """
        A simple wrap for websocket api "send_group_msg"
        """
        obj = {
            'action': 'send_group_msg',
            'params': {
                'group_id': group_id,
                'message': message,
            }
        }
        data = json.dumps(obj)
        print('qq send: ' + data)
        await self.ws.send(data)

    
    async def _send_private_msg(self, user_id, message):
        """
        A simple wrap for websocket api "send_private_msg"
        """
        obj = {
            'action': 'send_private_msg',
            'params': {
                'user_id': user_id,
                'message': message,
            }
        }
        data = json.dumps(obj)
        print('qq send: ' + data)
        await self.ws.send(data)

    
    async def run(self, mcws):
        # TODO: add retry mechanism
        self.ws = await websockets.connect(self.url)
        response = await self.ws.recv()
        print('qq connect: ' + response)
        self.ws_valid = True
        while True:
            recv_data = await self.ws.recv()
            data = json.loads(recv_data)
            if 'retcode' in data:
                # is a response to "send"
                print('qq recv: ' + recv_data)
                # do nothing
            else:
                # is an event
                if data['post_type'] == 'message':
                    post_str = ''
                    # TODO: handle anonymous
                    if data['message_type'] == 'group' and data['sub_type'] == 'normal':
                        group_id = data['group_id']
                        if group_id not in self.listen_groups:
                            continue
                        if group_id in self.group_aliases:
                            post_str += '[Group {}] '.format(self.group_aliases[group_id])
                        else:
                            post_str += '[Group {}] '.format(group_id)
                    elif data['message_type'] == 'private':
                        user_id = data['user_id']
                        if user_id not in self.listen_friends:
                            continue
                    sender = data['sender']['card'] if data['sender']['card'] else data['sender']['nickname']
                    message = data['message']
                    post_str += '{}: {}'.format(sender, message)
                    await mcws.post(post_str)

    
    async def stop(self):
        await self.ws.close()
    
    
    async def post(self, message):
        if self.ws_valid:
            for group in self.post_groups:
                await self._send_group_msg(group, message)
            for friend in self.post_friends:
                await self._send_private_msg(friend, message)
