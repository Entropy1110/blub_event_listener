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

'''def handle_event(event):
    try:
        enc_cmd_hex = event['args']['_encryptedCmd'].hex()
        decrypted = decrypt_command("0x" + enc_cmd_hex, SK_USER_SECRET)
        print("Decrypted Command:")
        print(json.dumps(decrypted, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
'''

def handle_event(event):
    try:
        enc_cmd_hex = event['args']['_encryptedCmd'].hex()
        decrypted = decrypt_command("0x" + enc_cmd_hex, SK_USER_SECRET)
        print("Decrypted Command:")
        print(json.dumps(decrypted, indent=2, ensure_ascii=False))

        device_id = decrypted.get("deviceId")
        action = decrypted.get("action")
        value = decrypted.get("value")  
        if device_id == 1001:
            if action == "set_temp":
                print(f"Living Room Thermostat >> 온도 설정 명령 (value={value})")
            elif action == "turn_off":
                print("Living Room Thermostat >> 전원 끄기 명령 수신됨")
            elif action == "force_error":
                print("Living Room Thermostat >> 강제 오류 명령 수신됨")
            else:
                print(f"Living Room Thermostat >> 알 수 없는 명령: {action}")

        elif device_id == 1002:
            if action == "turn_on":
                print("Kitchen Light >> 켜기 명령 수신됨")
            elif action == "turn_off":
                print("Kitchen Light >> 끄기 명령 수신됨")
            elif action == "set_brightness":
                print(f"Kitchen Light >> 밝기 설정 명령 수신됨 (value={value})")
            else:
                print(f"Kitchen Light >> 알 수 없는 명령: {action}")

        elif device_id == 1003:
            if action == "lock":
                print("Bedroom Door Lock >> 잠금 명령 수신됨")
            elif action == "unlock":
                print("Bedroom Door Lock >> 잠금 해제 명령 수신됨")
            else:
                print(f"Bedroom Door Lock >> 알 수 없는 명령: {action}")

        elif device_id == 1004:
            if action == "open":
                print("Garage Door Opener >> 문 열기 명령 수신됨")
            elif action == "close":
                print("Garage Door Opener >> 문 닫기 명령 수신됨")
            else:
                print(f"Garage Door Opener >> 알 수 없는 명령: {action}")

        elif device_id == 1005:
            if action == "start_record":
                print("Security Camera >> 녹화 시작 명령 수신됨")
            elif action == "stop_record":
                print("Security Camera >> 녹화 중지 명령 수신됨")
            else:
                print(f"Security Camera >> 알 수 없는 명령: {action}")

        else:
            print(f"알 수 없는 deviceId: {device_id}")

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

