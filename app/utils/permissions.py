import subprocess


def check_sudo_permissions(commands: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["sudo", "-n", "-l"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return False, "No sudo permissions configured or password required"

        output = result.stdout.lower()

        missing_commands = []
        for cmd in commands:
            if cmd.lower() not in output and "nopasswd: all" not in output:
                missing_commands.append(cmd)

        if missing_commands:
            return (
                False,
                f"Missing NOPASSWD sudo access for: {', '.join(missing_commands)}",
            )

        return True, "All required sudo permissions available"

    except subprocess.TimeoutExpired:
        return False, "Sudo check timed out"
    except Exception as e:
        return False, f"Failed to check sudo permissions: {str(e)}"
