from fastapi import APIRouter
import logging
import subprocess
import re


router = APIRouter()

logger = logging.getLogger(__name__)


def get_cpu_temperature() -> float | None:
    try:
        # Ubuntu server program to show server stats
        result = subprocess.run(
            ["landscape-sysinfo"], capture_output=True, text=True, timeout=10
        )

        match = re.search(r"Temperature:\s+(\d+\.?\d*)\s*C", result.stdout)

        if match:
            temp = float(match.group(1))
            return temp
        else:
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None


@router.get("/")
async def get_server_status():
    cpu_temp = get_cpu_temperature()

    return {"cpuTemp": str(cpu_temp) if cpu_temp is not None else "unknown"}
