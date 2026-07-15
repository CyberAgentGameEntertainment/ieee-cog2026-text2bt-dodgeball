from time import sleep
import json
import socket
from dataclasses import dataclass
import pathlib
from editor_agent.Config import CONFIG


@dataclass
class UnityCompileResultRaw:
    type: str
    message: str
    file: str
    line: int
    column: int

@dataclass
class UnityCompileResult:
    message: str
    filename: str
    line_raw: str
    line: int

def fetch_unity_compile() -> list[UnityCompileResult]:
    UNITY_PORT = 5000

    # fetch data
    for _ in range(
        3 if not CONFIG.WAIT_UNITY else 10
    ):
        try:
            with socket.create_connection(('localhost', UNITY_PORT)) as sock:
                sock.sendall(b'GET_COMPILE_STATUS\n')
                data = sock.recv(2**25).decode('utf-8')
                break
        except (Exception):
            sleep(
                3 if not CONFIG.WAIT_UNITY else 30
            )
    else:
        raise ConnectionError("Failed to connect to Unity for compile status.")
    
    # parse data
    data = json.loads(data)
    messages = data.get('messages', [])
    results_raw = [UnityCompileResultRaw(**msg) for msg in messages]

    # process data
    results = []
    for res in results_raw:
        line_raw = _fetch_line(res.file, res.line)
        filename = pathlib.Path(res.file).name
        result = UnityCompileResult(
            message=res.message,
            filename=filename,
            line_raw=line_raw,
            line=res.line
        )
        results.append(result)

    return results

def _fetch_line(filename: str, line_number: int) -> str:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if 0 < line_number <= len(lines):
                return lines[line_number - 1].strip()
    except Exception:
        return "<<line fetching failed>>"

if __name__ == "__main__":
    compile_results = fetch_unity_compile()
    for res in compile_results:
        print(f"{res.filename}:{res.line}: {res.message}")
        print(f"    {res.line_raw}")
