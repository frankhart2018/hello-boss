from fastapi import APIRouter
from pydantic import BaseModel


class ReverseProxyEntry(BaseModel):
    server_name: str


router = APIRouter()

NGINX_REV_PROXY_ENTRIES_PATH = "/etc/nginx/sites-available/reverse-proxy"


@router.get("/reverse-proxy/entries", tags=["nginx"])
async def get_reverse_proxy_entries():
    with open(NGINX_REV_PROXY_ENTRIES_PATH, "r") as f:
        lines = f.readlines()

    reverse_proxy_entries = []
    for line in lines:
        naked_line = line.strip()
        if naked_line.startswith("server_name"):
            server_name = naked_line.split()[1].split(";")[0]
            reverse_proxy_entries.append(
                ReverseProxyEntry(server_name=server_name).model_dump()
            )

    return {"reverse_proxy": reverse_proxy_entries}
