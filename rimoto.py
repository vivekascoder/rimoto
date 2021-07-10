#!/usr/bin/env python

import asyncio
import websockets
import pyautogui
import os
import json

from config import CMD_PATH

def get_commands(file_path: str) -> dict:
  if not os.path.isfile(file_path):
    return False
  file = open(file_path, 'r').read()
  data = json.loads(file)
  return data


async def server(websocket, path):
  commands = get_commands(CMD_PATH)
  while True:
    message = await websocket.recv()
    if message in commands:
      pyautogui.hotkey(*commands[message])
    else:
      print('Command not found %' %(message))

def main():
  print("Starting Server 0.0.0.0:5678")
  start_server = websockets.serve(server, '0.0.0.0', 5678)
  asyncio.get_event_loop().run_until_complete(start_server)
  asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
  main()

