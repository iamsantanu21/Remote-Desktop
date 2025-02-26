import socket
import cv2
import pickle
import struct

# Connect to server
server_ip = "10.10.166.113"  # Change this to the actual Windows IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, 9999))
print("Connected to server.")

while True:
    # Receive image size
    data_size = struct.unpack("Q", client_socket.recv(8))[0]

    # Receive image data
    data = b""
    while len(data) < data_size:
        data += client_socket.recv(4096)

    # Decode image
    frame = pickle.loads(data)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # Display
    cv2.imshow("Remote Desktop", frame)
    if cv2.waitKey(1) == ord("q"):
        break

client_socket.send("exit".encode())
client_socket.close()
cv2.destroyAllWindows()
