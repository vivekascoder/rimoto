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
    print(f"[] Message Recieved. {message}")
    if message in commands:
      pyautogui.hotkey(*commands[message])
    else:
      print('Command not found %' %(message))

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
  start_server = websockets.serve(server, '0.0.0.0', 5678)
  asyncio.get_event_loop().run_until_complete(start_server)
  asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
  main()

