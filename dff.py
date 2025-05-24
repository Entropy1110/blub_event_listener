from web3 import Web3
import time

# Alchemy HTTP 엔드포인트 (WebSocket 대신 HTTP 사용)
HTTP_URL = ""
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
    """이벤트 데이터를 포맷팅하여 출력"""
    print("\n🔔 New VerifyLog Event")
    print(f"📌 Block: {event['blockNumber']}")
    print(f"🔄 _pA: {event['args']['_pA']}")
    print(f"🔄 _pB: {event['args']['_pB']}")
    print(f"🔄 _pC: {event['args']['_pC']}")
    print(f"📡 _pubSignals: {event['args']['_pubSignals']}")
    print(f"🔒 _encryptedCmd (hex): {event['args']['_encryptedCmd'].hex()}")
    print("-" * 50)

def get_latest_block():
    """최신 블록 번호 조회"""
    try:
        return web3.eth.block_number
    except Exception as e:
        print(f"⚠️ Failed to get block number: {e}")
        return None

def listen_events():
    """실시간 이벤트 감지"""
    print("🔍 Starting event listener...")
    last_block = get_latest_block()
    
    if last_block is None:
        print("❌ Could not fetch initial block number")
        return

    print(f"⏳ Current block: {last_block}")
    print("🚀 Ready to detect events!")

    while True:
        try:
            current_block = get_latest_block()
            if current_block is None:
                time.sleep(5)
                continue

            if current_block > last_block:
                print(f"\n🔎 Scanning blocks {last_block + 1} to {current_block}")
                
                events = contract.events.VerifyLog.get_logs(
                    fromBlock=last_block + 1,
                    toBlock=current_block
                )
                
                if events:
                    print(f"🎯 Found {len(events)} event(s)")
                    for event in events:
                        handle_event(event)
                else:
                    print("⏭️ No events found")

                last_block = current_block
            else:
                print(".", end="", flush=True)  # 진행 상태 표시

            time.sleep(5)  # 5초 간격으로 폴링

        except KeyboardInterrupt:
            print("\n🛑 Listener stopped by user")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")
            time.sleep(10)  # 오류 발생 시 10초 대기

if __name__ == "__main__":
    listen_events()

