import socket
import cv2
import pickle
import struct
import ssl
import pyautogui

# Server IP (Replace with actual Windows server IP)
server_ip = "10.10.166.113"

# Create Client Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SSL Context (Disable Strict Verification for Testing)
context = ssl.create_default_context()
context.check_hostname = False  # Disable hostname check
context.verify_mode = ssl.CERT_NONE  # Disable certificate verification

# Connect to Server
conn = context.wrap_socket(client_socket)
conn.connect((server_ip, 9999))
print("✅ Connected to server.")

def receive_data(conn, size):
    """Helper function to receive exact bytes"""
    data = b""
    while len(data) < size:
        packet = conn.recv(min(4096, size - len(data)))
        if not packet:
            return None  # Connection closed
        data += packet
    return data

try:
    while True:
        # Receive frame size (8 bytes)
        data_size_bytes = receive_data(conn, 8)
        if not data_size_bytes:
            break  # Stop if no data

        data_size = struct.unpack("Q", data_size_bytes)[0]

        # Receive full image data
        data = receive_data(conn, data_size)
        if not data:
            break

        # Decode and Show Frame
        frame = pickle.loads(data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        cv2.imshow("Live Remote Desktop", frame)

        # Send Mouse Position
        x, y = pyautogui.position()
        conn.sendall(f"MOUSE_MOVE {x} {y}".encode())

        if cv2.waitKey(1) == ord("q"):
            break
except Exception as e:
    print(f"❌ Error: {e}")

conn.close()
cv2.destroyAllWindows()
