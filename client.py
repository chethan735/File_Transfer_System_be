import socket
import hashlib
import os

SERVER_IP = "127.0.0.1"
PORT = 5000
CHUNK_SIZE = 1024

def calculate_checksum(data):
    """Calculate SHA256 checksum"""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()

def send_file(file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Send file name and size
    client_socket.sendall(file_name.encode())
    client_socket.sendall(str(file_size).encode())

    # Read file and send in chunks
    with open(file_path, "rb") as f:
        seq_num = 0
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            seq_num_bytes = seq_num.to_bytes(4, 'big')
            client_id_bytes = (PORT % 10000).to_bytes(4, 'big')
            client_socket.sendall(seq_num_bytes + client_id_bytes + chunk)
            seq_num += 1

            # Wait for ACK
            ack = client_socket.recv(4)
            if not ack or int.from_bytes(ack, 'big') != seq_num - 1:
                print(f"[!] Packet loss detected, resending {seq_num-1}")
                f.seek(seq_num - 1 * CHUNK_SIZE)
                seq_num -= 1  # Resend previous chunk

    # Receive checksum
    received_checksum = client_socket.recv(64).decode()

    # Receive file back
    received_data = bytearray()
    expected_seq = 0
    while len(received_data) < file_size:
        packet = client_socket.recv(CHUNK_SIZE + 8)
        if not packet:
            break

        seq_num = int.from_bytes(packet[:4], 'big')
        client_id = int.from_bytes(packet[4:8], 'big')
        chunk_data = packet[8:]

        # Request retransmission if out of order
        if seq_num == expected_seq:
            received_data.extend(chunk_data)
            expected_seq += 1
        else:
            print(f"[!] Out-of-order packet {seq_num}, expected {expected_seq}")

    # Verify checksum
    computed_checksum = calculate_checksum(received_data)
    if computed_checksum == received_checksum:
        print("[✓] File Transfer Successful")
    else:
        print("[✗] File Corruption Detected")

    client_socket.close()

if __name__ == "__main__":
    file_path = input("Enter file path to send: ")
    send_file(file_path)
