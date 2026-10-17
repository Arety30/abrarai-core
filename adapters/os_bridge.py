import os
import subprocess
import platform
import logging

class OSBridge:
    """
    Handles cross-platform path normalization, file safety checks,
    and sanitized shell executions across Ubuntu, Windows, and Android environments.
    """
    def __init__(self):
        self.os_type = platform.system().lower()
        # Restrict command execution to a strict whitelist for security
        self.command_whitelist = {
            "ubuntu": ["ls", "pwd", "mkdir", "rmdir", "echo"],
            "windows": ["dir", "cd", "mkdir", "echo"],
            "darwin": ["ls", "pwd", "mkdir", "echo"],
            "linux": ["ls", "pwd", "mkdir", "echo"] # Fallback/Android termux
        }

    def normalize_path(self, target_path):
        """Converts any path layout to match the host machine system formatting."""
        return os.path.normpath(target_path)

    def execute_sanitized_command(self, base_command, arguments=None):
        """
        Validates a command against the platform whitelist and runs it 
        safely without exposing the shell to injection vulnerabilities.
        """
        platform_key = "ubuntu" if "ubuntu" in platform.version().lower() else self.os_type
        whitelist = self.command_whitelist.get(platform_key, self.command_whitelist.get("linux", []))

        if base_command not in whitelist:
            logging.error(f"Execution Blocked: Command '{base_command}' is not whitelisted for platform '{platform_key}'.")
            return {"success": False, "error": "Unauthorized command sequence"}

        cmd_array = [base_command]
        if arguments:
            if isinstance(arguments, list):
                cmd_array.extend(arguments)
            else:
                cmd_array.append(str(arguments))

        try:
            logging.info(f"OSBridge executing sanitized array: {cmd_array}")
            # Run without shell=True to neutralize injection risks entirely
            result = subprocess.run(cmd_array, capture_output=True, text=True, check=True)
            return {"success": True, "output": result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            logging.error(f"OSBridge execution failed: {e.stderr}")
            return {"success": False, "error": e.stderr.strip()}
        except Exception as e:
            logging.error(f"Unexpected bridge error: {str(e)}")
            return {"success": False, "error": str(e)}
