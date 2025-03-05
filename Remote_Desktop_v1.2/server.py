import socket
import cv2
import pickle
import struct
import pyautogui
import numpy as np
import threading
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

# Setup Mouse and Keyboard Controllers
mouse = MouseController()
keyboard = KeyboardController()

# Create UDP Server Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("0.0.0.0", 9999))  # Listen on all interfaces
print("✅ Server is running... Waiting for connections.")

clients = set()  # Store clients to send frames to all connected users


def send_screen():
    """Continuously capture and send screen frames."""
    while True:
        try:
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Encode Frame
            _, encoded_frame = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
            data = pickle.dumps(encoded_frame)

            # Send Frame Size and Data to All Clients
            for client in clients:
                server_socket.sendto(struct.pack("Q", len(data)), client)
                server_socket.sendto(data, client)
        except Exception as e:
            print(f"❌ Error Sending Frame: {e}")


def handle_client():
    """Receive mouse/keyboard commands from clients."""
    while True:
        try:
            command, client_addr = server_socket.recvfrom(1024)  # Receive command
            clients.add(client_addr)  # Register client
            process_command(command.decode())  # Process command
        except Exception as e:
            print(f"❌ Error Receiving Command: {e}")


def process_command(command):
    """Process received mouse and keyboard commands."""
    try:
        parts = command.split()
        action = parts[0]

        if action == "MOUSE_MOVE":
            x, y = int(parts[1]), int(parts[2])
            mouse.position = (x, y)

        elif action == "MOUSE_CLICK":
            mouse.click(Button.left)

        elif action == "KEY_PRESS":
            key = parts[1]
            if hasattr(Key, key):
                keyboard.press(getattr(Key, key))
                keyboard.release(getattr(Key, key))
            else:
                keyboard.press(key)
                keyboard.release(key)

    except Exception as e:
        print(f"❌ Command Error: {e}")


# Start Threads
threading.Thread(target=send_screen, daemon=True).start()
threading.Thread(target=handle_client, daemon=True).start()

# Keep Server Running
while True:
    pass
