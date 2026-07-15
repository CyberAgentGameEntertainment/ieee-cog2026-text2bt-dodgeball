import socket
from time import sleep
from editor_agent.Config import CONFIG

def fetch_bt_deserialization_result(bt_path: str) -> str:
    """
    Fetches the behavior tree deserialization result from Unity via socket communication.
    """
    
    UNITY_PORT = 5001

    data = None
    for _ in range(
        3 if not CONFIG.WAIT_UNITY else 10
    ):
        try:
            with socket.create_connection(('localhost', UNITY_PORT)) as sock:
                request = str(bt_path).replace('\\', '/')
                sock.sendall(request.encode('utf-8'))
                data = sock.recv(2**25).decode('utf-8')
                break
        except (Exception):
            sleep(
                3 if not CONFIG.WAIT_UNITY else 30
            )

    if data is not None:
        return data
    else:
        raise ConnectionError("Failed to connect to Unity for behavior tree deserialization.")

if __name__ == "__main__":
    bt_path = "Assets/BehaviorTree/BehaviorTree.json"
    result = fetch_bt_deserialization_result(bt_path)
    print(f"Deserialization result for {bt_path}: {result}")
