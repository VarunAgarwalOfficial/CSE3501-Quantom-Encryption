import socket 
import random

# Common code for both
PADDING_LITRAL = " "  # Placeholder for padding in the message
KEY_BATCH = 7  # Number of bits in each batch of the binary key
FIRST_KEY_LENGTH = 500  # Length of the initial key

def binary_to_decimal(binary):
    """
    Converts binary to decimal.
    """
    decimal, i = 0, 0
    while binary != 0:
        dec = binary % 10
        decimal += dec * pow(2, i)
        binary //= 10
        i += 1
    return decimal   

def generate_key(key):
    """
    Generates the final key by converting binary key batches to decimal.
    """
    final_key = [binary_to_decimal(int(key[i : i + KEY_BATCH])) for i in range(0, len(key), KEY_BATCH)]
    return final_key

def xor_encrypt(message, final_key):
    """
    Encrypts the message using XOR with the final key.
    """
    encrypted_msg = "".join(chr(ord(message[i]) ^ final_key[i % len(final_key)]) for i in range(len(message)))
    return encrypted_msg

HEADER = 64  # Message header size
PORT = 5050  # Communication port
SERVER = socket.gethostbyname(socket.gethostname())  # Server IP address
ADDR = (SERVER, PORT)  # Server address
FORMAT = 'utf-8'  # Encoding format

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

FILTERS = ["R", "D"]  # List of filters

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    
    key = []  # Binary key
    filters_used = []  # List of filters used
    
    # Receiving the initial key
    for i in range(FIRST_KEY_LENGTH):
        msg = conn.recv(1).decode(FORMAT)
        choice = random.choice(FILTERS)
        filters_used.append(choice)
        
        # Building the binary key based on the filters
        if choice.lower() == msg.lower():
            key.append(0 if msg.islower() else 1)
        else:
            key.append(random.choice([0, 1]))

    # Getting list of filters used
    accepted_filters = []
    final_key = []
    
    # Receiving the filters used during key generation
    for i in range(FIRST_KEY_LENGTH):
        msg = conn.recv(1).decode(FORMAT)
        
        if msg == filters_used[i]:
            accepted_filters.append("1")
            final_key.append(key[i])
        else:
            accepted_filters.append("0")
    
    # Returning the accepted filters
    conn.send("".join(accepted_filters).encode(FORMAT))
    print("".join(map(str, final_key)))

    batch_size = int(conn.recv(2).decode(FORMAT))

    final_key = "".join(map(str, final_key))
    final_key = generate_key(final_key)    
    print(f"Final key created using the binary key with key batch : {KEY_BATCH} is : {final_key}")

    # Receiving the encrypted message
    final_message = conn.recv(batch_size * len(final_key)).decode(FORMAT)
    print(f"Batch Size of the message received: {batch_size}")
    print(f"Message received: {final_message}")

    # Decrypting the message using the final key
    decrypted_message = xor_encrypt(final_message, final_key)
    print(f"Message decrypted using the key is: {decrypted_message}")

    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    
    while True:
        conn, addr = server.accept()
        handle_client(conn, addr)

print("[STARTING] Server is starting...")
start()
