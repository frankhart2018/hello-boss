import os


def get_required_env(key: str) -> str:
    if os.getenv(key) is None:
        raise ValueError(f"Environment variable '{key}' not set!")

    return os.getenv(key)


OUTPUT_DIR = os.path.join(get_required_env("OUTPUT_DIR"), "static")
os.makedirs(OUTPUT_DIR, exist_ok=True)
