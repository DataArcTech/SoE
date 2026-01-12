from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import logging
# logging.basicConfig(filename='outputs/crypto.log',
#                     filemode='a',
#                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                     datefmt='%H:%M:%S',
#                     level=logging.ERROR)

crypto_key = "WmZq4t7w!z%C&F)J"

# Basic encryption and decryption by Presidio
def presidio_encryption(key, content, method):
    pass

def presidio_decryption(key, encrypted_content):
    from presidio_anonymizer.operators import Decrypt #  using AES cypher in CBC mode

    # Restore the original entity value
    result = Decrypt().operate(text=encrypted_content, params={"key": crypto_key})
    print(result)
    return

### RSA encrytion and decryption example
def example():
    """
    RSA for object and concepts
    """
    # Generate RSA keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    print(private_key)
    public_key = private_key.public_key()
    print(public_key)

    # Encrypt entity data (e.g., a secret about an object)
    ciphertext = public_key.encrypt(
        b"Secret about an object",
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

    # Decrypt
    decrypted_data = private_key.decrypt(
        ciphertext,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    print("results:", decrypted_data)

# AES in ECB mode - encryption and decryption
def encrypt_aes_ecb(k, text):
    """"
    key and plaintext are binary type
    key example: b'WmZq4t7w!z%C&F)J'  # AES key must be 16, 24, or 32 bytes long
    """
    key = k.encode('utf-8')
    plaintext = text.encode('utf-8')
    
    # AES encryption setup (ECB mode)
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())

    # Padding the plaintext (PKCS7)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()

    # Encrypt the padded plaintext
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # # Convert ciphertext (bytes) to a Base64-encoded string
    ciphertext_base64 = base64.b64encode(ciphertext).decode('utf-8')

    return ciphertext_base64

def decrypt_aes_ecb(key, ciphertext):
    key = key.encode('utf-8')
    try:
        ciphertext = base64.b64decode(ciphertext.encode('utf-8'))
    except ValueError as e:
        print(f"Base64 format error: {e}")
        logging.exception('Error: ')
        logging.exception(f'The ciphertext {ciphertext} is not in base64 format.')

    # Decrypt the ciphertext
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    try:
        decrypted_padded_text = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove padding after decryption
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_text = unpadder.update(decrypted_padded_text) + unpadder.finalize()
    except Exception as e:
        print(f"Error: {e}")
        logging.exception(f"Error: {e}")
        logging.exception(f'The ciphertext {ciphertext} cannot be decrypted.')
        decrypted_text = b'Error'
    
    return decrypted_text

def replace_base64_with_tokens(text, token_map=None):
    if token_map is None:
        base64_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/="
        token_map = {char: f"ci_{char}" for char in base64_characters}
    replaced_text = "".join([token_map.get(char, char) for char in text])
    return replaced_text

def recover_back2_base64(replaced_text, token_map=None):
    if token_map is None:
        base64_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/="
        token_map = {char: f"ci_{char}" for char in base64_characters}
    # Create a reverse mapping: ci_A -> A, ci_B -> B, etc.
    reverse_map = {v: k for k, v in token_map.items()}
    
    # Reconstruct the original text
    original_text = replaced_text
    for token, char in reverse_map.items():
        original_text = original_text.replace(token, char)
    
    return original_text

if __name__ == "__main__":
    
    encrypted_content = "PFfHjIii/C5ujk8xoeIi+KtvS4d/hynu9yqCDrWglJs="
    presidio_decryption(crypto_key, encrypted_content)

    for i in range(5):
        ciphertext_base64 = encrypt_aes_ecb(crypto_key, '李鹏')
        print(ciphertext_base64)
        ciphertext_base64='mImR4c7ojFsZYfmP1FdeWg=='
        decrypted_text = decrypt_aes_ecb(crypto_key, ciphertext_base64)
        print(f"Decrypted text: {decrypted_text.decode()}")