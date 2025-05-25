# decryptor.py

import json
from binascii import unhexlify
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

SALT = b"some-salt-value"
ITERATIONS = 100000
KEY_LENGTH_BYTES = 32
IV_LENGTH_BYTES = 12
AUTH_TAG_LENGTH_BYTES = 16

def derive_key(passphrase_str: str) -> bytes:
    passphrase_bytes = passphrase_str.encode('utf-8')
    return PBKDF2(
        password=passphrase_bytes,
        salt=SALT,
        dkLen=KEY_LENGTH_BYTES,
        count=ITERATIONS,
        hmac_hash_module=SHA256
    )

def decrypt_command(hex_encoded_encrypted_data: str, sk_user_passphrase: str) -> dict:
    base64_encoded_str = unhexlify(hex_encoded_encrypted_data.replace("0x", "")).decode('utf-8')
    encrypted_data_with_iv_and_tag = b64decode(base64_encoded_str)

    if len(encrypted_data_with_iv_and_tag) < IV_LENGTH_BYTES + AUTH_TAG_LENGTH_BYTES:
        raise ValueError("Encrypted data is too short to contain IV and Auth Tag.")

    iv = encrypted_data_with_iv_and_tag[:IV_LENGTH_BYTES]
    ciphertext_with_tag = encrypted_data_with_iv_and_tag[IV_LENGTH_BYTES:]
    actual_ciphertext = ciphertext_with_tag[:-AUTH_TAG_LENGTH_BYTES]
    auth_tag = ciphertext_with_tag[-AUTH_TAG_LENGTH_BYTES:]

    key = derive_key(sk_user_passphrase)

    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    plaintext_bytes = cipher.decrypt_and_verify(actual_ciphertext, auth_tag)

    return json.loads(plaintext_bytes.decode('utf-8'))
