#!/usr/bin/env python
"""
The Websocket Server, Which handles the WebSocket Protocol,
"""
import asyncio
import websockets
import pyautogui
import os
import psutil
import json
import threading
# import ssl
# import pathlib
import http.server
import socketserver

from config import CMD_PATH

def get_commands(file_path: str) -> dict:
  if not os.path.isfile(file_path):
    return False
  file = open(file_path, 'r').read()
  data = json.loads(file)
  return data


async def consumer_handler(websocket, path):
  print("Consumer Process")
  commands = get_commands(CMD_PATH)
  while True:
    message = await websocket.recv()
    data = json.loads(message)
    print(data)
    if data['type'] == 'type_keys':
      if (message:=data['cmd']) in commands:
        pyautogui.hotkey(*commands[message])
      else:
        print(f'Command not found {message}')
    elif data['type'] == 'type_key':
      print(f"type_key event recieved, with key {data['key']}")
      pyautogui.press([data['key']])

async def producer_handler(websocket, path):
  print("[] Producer Process")
  while True:
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()[2]
    await websocket.send(
      json.dumps({
        'ram': ram,
        'cpu': cpu
      })
    )
    await asyncio.sleep(2)

async def server(websocket, path):
  consumer_task = asyncio.ensure_future(
    consumer_handler(websocket, path))
  producer_task = asyncio.ensure_future(
    producer_handler(websocket, path))
  done, pending = await asyncio.wait(
    [consumer_task, producer_task],
    return_when=asyncio.FIRST_COMPLETED,
  )
  for task in pending:
    task.cancel()



def main():
  print("Starting Server 0.0.0.0:5678")
  # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
  # localhost_pem = os.path.join(os.getcwd(), "privkey.pem")
  # print(pathlib.Path(__file__))
  # ssl_context.load_cert_chain(localhost_pem)

  start_server = websockets.serve(
    server, 
    '0.0.0.0', 
    5678,
    # ssl=ssl_context
  )
  # web_server_thread = threading.Thread(target=run_web_server, args=())
  # web_server_thread.start()
  asyncio.get_event_loop().run_until_complete(start_server)
  asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
  main()

