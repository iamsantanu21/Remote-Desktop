import socket
import cv2
import pickle
import struct
import pyautogui
import time

server_ip = "10.10.32.175"  # Replace with actual server IP

# Create UDP Client Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 10**6)  # Increase buffer size

# Send Initial Connection Packet
client_socket.sendto("CONNECT".encode(), (server_ip, 9999))
print("✅ Connected to server.")

PACKET_SIZE = 1400  # Match server's reduced packet size

def receive_data(sock, total_chunks):
    """Receive all chunks of data and reassemble."""
    data = b""
    for _ in range(total_chunks):
        try:
            chunk, _ = sock.recvfrom(PACKET_SIZE)
            data += chunk
        except socket.timeout:
            print("⚠️ Warning: Packet timeout, skipping frame.")
            return None  # Drop frame if incomplete
    return data

try:
    while True:
        # Receive total chunk count
        try:
            total_chunks_data, _ = client_socket.recvfrom(8)
            total_chunks = struct.unpack("Q", total_chunks_data)[0]
        except struct.error:
            print("⚠️ Warning: Corrupted chunk count received, skipping frame.")
            continue

        # Receive full image in chunks
        data = receive_data(client_socket, total_chunks)
        if data is None:  # Drop corrupted frame
            continue

        try:
            frame = pickle.loads(data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        except pickle.UnpicklingError:
            print("❌ Error: Incomplete frame received, skipping.")
            continue

        # Show Frame
        cv2.imshow("Live Remote Desktop", frame)

        # Send Mouse Position (Throttled)
        x, y = pyautogui.position()
        time.sleep(0.02)  # Small delay to prevent fast updates causing jitter
        client_socket.sendto(f"MOUSE_MOVE {x} {y}".encode(), (server_ip, 9999))

        # Quit on 'q' Press
        if cv2.waitKey(1) == ord("q"):
            break
except Exception as e:
    print(f"❌ Error: {e}")

client_socket.close()
cv2.destroyAllWindows()
