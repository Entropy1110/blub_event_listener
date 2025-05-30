from web3 import Web3
import time
import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

# 설정값 가져오기
from config import HTTP_URL, CONTRACT_ADDRESS, SK_USER_SECRET

# Web3 초기화
web3 = Web3(Web3.HTTPProvider(HTTP_URL))

# 컨트랙트 ABI (변경 없음)
CONTRACT_ABI = [
    {
        "type": "event",
        "name": "VerifyLog",
        "inputs": [
            {"name": "_pA", "type": "uint256[2]", "indexed": False},
            {"name": "_pB", "type": "uint256[2][2]", "indexed": False},
            {"name": "_pC", "type": "uint256[2]", "indexed": False},
            {"name": "_pubSignals", "type": "uint256[6]", "indexed": False},
            {"name": "_encryptedCmd", "type": "bytes", "indexed": False}
        ],
        "anonymous": False
    }
]
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def decrypt_cmd_gcm(enc_bytes: bytes, sk_user: str) -> str:
    # Base64 디코딩 전처리
    b64_str = enc_bytes.decode('utf-8')
    raw = base64.b64decode(b64_str)

    # IV / Ciphertext+Tag 분리
    iv = raw[:12]
    ciphertext_and_tag = raw[12:]

    # 키 파생 (PBKDF2-SHA256)
    salt = b"some-salt-value"
    key = PBKDF2(
        sk_user.encode('utf-8'),
        salt,
        dkLen=32,
        count=100000,
        hmac_hash_module=SHA256
    )

    # AES-GCM 복호화
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    plaintext = cipher.decrypt_and_verify(
        ciphertext_and_tag[:-16],
        ciphertext_and_tag[-16:]
    )

    return plaintext.decode('utf-8', errors='replace')

def handle_event(event):
    enc = event['args']['_encryptedCmd']
    try:
        cmd = decrypt_cmd_gcm(enc, SK_USER_SECRET)
    except Exception as e:
        cmd = f"<복호화 실패: {e}>"

    print("\nNew VerifyLog Event")
    print(f"Block: {event['blockNumber']}")
    print(f"_pA: {event['args']['_pA']}")
    print(f"_pB: {event['args']['_pB']}")
    print(f"_pC: {event['args']['_pC']}")
    print(f"_pubSignals: {event['args']['_pubSignals']}")
    print(f"_encryptedCmd (hex): {enc.hex()}")
    print(f" Decrypted Command: {cmd}")
    print("-" * 50)

def get_latest_block():
    try:
        return web3.eth.block_number
    except Exception as e:
        print(f"Failed to get block number: {e}")
        return None

def listen_events():
    print("Starting event listener...")
    last_block = get_latest_block()
    if last_block is None:
        print("Could not fetch initial block number")
        return

    print(f"Current block: {last_block}")
    print("Ready to detect events!")

    while True:
        try:
            current_block = get_latest_block()
            if current_block is None:
                time.sleep(5)
                continue

            if current_block > last_block:
                print(f"\nScanning blocks {last_block + 1} to {current_block}")
                events = contract.events.VerifyLog.get_logs(
                    fromBlock=last_block + 1,
                    toBlock=current_block
                )
                if events:
                    print(f"Found {len(events)} event(s)")
                    for event in events:
                        handle_event(event)
                else:
                    print("No events found")
                last_block = current_block
            else:
                print(".", end="", flush=True)

            time.sleep(5)

        except KeyboardInterrupt:
            print("\nListener stopped by user")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(10)

if __name__ == "__main__":
    listen_events()

