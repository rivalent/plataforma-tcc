import time
from datetime import datetime, timezone

def format_response(data=None, start_time: float = 0.0, message: str = "Success", error: str = ""):
    elapsed = int((time.time() - start_time) * 1000) if start_time else 0

    return {
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "elapsed": elapsed,
        "error": error,
        "data": data
    }
