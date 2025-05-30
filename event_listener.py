from web3 import Web3
import time
from config import HTTP_URL, CONTRACT_ADDRESS, SK_USER_SECRET
from decryptor import decrypt_command
import json


# Alchemy HTTP 엔드포인트 (WebSocket 대신 HTTP 사용)
web3 = Web3(Web3.HTTPProvider(HTTP_URL))

# 컨트랙트 정보
CONTRACT_ADDRESS = "0xb7Da4867E20dc2205c95F851C87eaf5f8e771a20"
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

def handle_event(event):
    try:
        enc_cmd_hex = event['args']['_encryptedCmd'].hex()
        decrypted = decrypt_command("0x" + enc_cmd_hex, SK_USER_SECRET)
        print("Decrypted Command:")
        print(json.dumps(decrypted, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Decryption failed: {e}")

def get_latest_block():
    """최신 블록 번호 조회"""
    try:
        return web3.eth.block_number
    except Exception as e:
        print(f"Failed to get block number: {e}")
        return None

def listen_events():
    """실시간 이벤트 감지"""
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
                print(f"Scanning blocks {last_block + 1} to {current_block}")
                
                events = contract.events.VerifyLog.get_logs(
                    from_block=last_block + 1,
                    to_block=current_block
                )
                
                if events:
                    print(f"Found {len(events)} event(s)")
                    for event in events:
                        handle_event(event)

                last_block = current_block

            time.sleep(5)  # 5초 간격으로 폴링

        except KeyboardInterrupt:
            print("\nListener stopped by user")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(10)  # 오류 발생 시 10초 대기

if __name__ == "__main__":
    listen_events()

