import yaml
import asyncio
from aioconsole import ainput
from qqbot import QQBotWS
from multichat import MultiChatWS


async def console_control(qqws, mcws):
    while True:
        cmd = await ainput()
        if cmd == 'quit':
            await qqws.stop()
            await mcws.stop()
            break  # stop event loop


def main():
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.full_load(f.read())
    print('Loaded config: ' + str(config))
    qqws = QQBotWS(config)
    mcws = MultiChatWS(config)
    loop = asyncio.get_event_loop()
    loop.create_task(qqws.run(mcws))
    loop.create_task(mcws.run(qqws))
    loop.run_until_complete(console_control(qqws, mcws))


if __name__ == '__main__':
    main()
