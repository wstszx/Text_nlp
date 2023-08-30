import asyncio
import json
import adbutils
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from websockets import serve
import os

async def adb_handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        if data['action'] == 'connect':
            adb_device = await connect_adb(data['ip'], data['port'], data['rsa_key_path'])
            if adb_device:
                await websocket.send(json.dumps({'status': 'connected'}))
            else:
                await websocket.send(json.dumps({'status': 'error'}))
        elif data['action'] == 'tap':
            if adb_device:
                await tap(adb_device, data['x'], data['y'])
                await websocket.send(json.dumps({'status': 'tapped'}))
            else:
                await websocket.send(json.dumps({'status': 'error'}))
        elif data['action'] == 'swipe':
            if adb_device:
                await swipe(adb_device, data['x1'], data['y1'], data['x2'], data['y2'])
                await websocket.send(json.dumps({'status': 'swiped'}))
            else:
                await websocket.send(json.dumps({'status': 'error'}))
        elif data['action'] == 'key':
            if adb_device:
                await key(adb_device, data['keycode'])
                await websocket.send(json.dumps({'status': 'key sent'}))
            else:
                await websocket.send(json.dumps({'status': 'error'}))

        # Send screen capture
        d = adbutils.adb.device(adb_device.serial)
        image = d.screencap()
        await websocket.send(json.dumps({'type': 'display', 'image': image}))

async def connect_adb(ip, port, rsa_key_path):
    print(os.path.exists(rsa_key_path))
    signer = PythonRSASigner.FromRSAKeyPath(rsa_key_path)
    adb_device = AdbDeviceTcp(ip, port)
    await adb_device.connect(rsa_keys=[signer], auth_timeout_s=1)
    if adb_device.is_connected():
        return adb_device
    else:
        return None

async def tap(adb_device, x, y):
    await adb_device.shell(f'input tap {x} {y}')

async def swipe(adb_device, x1, y1, x2, y2):
    await adb_device.shell(f'input swipe {x1} {y1} {x2} {y2}')

async def key(adb_device, keycode):
    await adb_device.shell(f'input keyevent {keycode}')

start_server = serve(adb_handler, "localhost", 8766)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
