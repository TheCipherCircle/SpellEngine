"""
PatternForge Cracker Integration for SpellEngine

Routes all hash cracking through PatternForge, which in turn uses
hashcat/john. This teaches players the real tools.

PROPRIETARY - All Rights Reserved
Copyright (c) 2026 The Cipher Circle
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class CrackResult:
    """Result from a crack attempt."""

    success: bool
    plaintext: str = ""
    tool: str = ""
    time_seconds: float = 0.0
    error: str = ""
    command: str = ""  # The command that was run (for learning)

    @classmethod
    def from_json(cls, data: dict, command: str = "") -> "CrackResult":
        """Create from PatternForge JSON output."""
        status = data.get("status", "NOT_FOUND")
        return cls(
            success=status == "CRACKED",
            plaintext=data.get("plain", ""),
            tool=data.get("tool", "unknown"),
            time_seconds=data.get("time", 0.0),
            command=command,
        )

    @classmethod
    def error_result(cls, error: str, command: str = "") -> "CrackResult":
        """Create an error result."""
        return cls(
            success=False,
            error=error,
            command=command,
        )


def verify_password(
    hash_value: str,
    password: str,
    hash_type: str | None = None,
    on_progress: Callable[[str], None] | None = None,
) -> CrackResult:
    """Verify a password guess against a hash using PatternForge.

    Creates a temporary wordlist with just the guess and runs
    PatternForge crack against it.

    Args:
        hash_value: The hash to crack
        password: The password guess to verify
        hash_type: Optional hash type hint (md5, sha1, sha256)
        on_progress: Optional callback for progress messages

    Returns:
        CrackResult with success/failure
    """
    # Create temp file with the single password guess
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(password + '\n')
        wordlist_path = f.name

    try:
        # Build command
        cmd = [
            sys.executable, "-m", "patternforge", "crack",
            hash_value,
            "--wordlist", wordlist_path,
            "--json",
        ]

        # Add hash type if provided
        if hash_type:
            type_map = {"md5": 0, "sha1": 100, "sha256": 1400}
            if hash_type.lower() in type_map:
                cmd.extend(["--type", str(type_map[hash_type.lower()])])

        cmd_str = f"patternforge crack {hash_value[:16]}... --wordlist <guess>"

        if on_progress:
            on_progress("Verifying with PatternForge...")

        # Run PatternForge
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                return CrackResult.from_json(data, cmd_str)
            except json.JSONDecodeError:
                return CrackResult.error_result(
                    "Invalid JSON from PatternForge",
                    cmd_str
                )
        else:
            # Check if it's a "not found" vs error
            if "NOT_FOUND" in result.stdout or result.returncode == 0:
                return CrackResult(
                    success=False,
                    command=cmd_str,
                )
            return CrackResult.error_result(
                result.stderr or "PatternForge failed",
                cmd_str
            )

    except subprocess.TimeoutExpired:
        return CrackResult.error_result("Verification timed out", cmd_str)
    except FileNotFoundError:
        return CrackResult.error_result(
            "PatternForge not installed",
            "pip install patternforge"
        )
    except Exception as e:
        return CrackResult.error_result(str(e), cmd_str)
    finally:
        # Clean up temp file
        try:
            Path(wordlist_path).unlink()
        except Exception:
            pass


def crack_hash(
    hash_value: str,
    hash_type: str | None = None,
    wordlist: str = "common",
    tool: str = "auto",
    on_progress: Callable[[str], None] | None = None,
    timeout: int = 60,
) -> CrackResult:
    """Crack a hash using PatternForge.

    Runs a full crack attempt with the specified wordlist.

    Args:
        hash_value: The hash to crack
        hash_type: Optional hash type hint (md5, sha1, sha256)
        wordlist: Wordlist to use (bundled name or path)
        tool: Tool preference (auto, hashcat, john)
        on_progress: Optional callback for progress messages
        timeout: Timeout in seconds

    Returns:
        CrackResult with the cracked password or failure
    """
    # Build command
    cmd = [
        sys.executable, "-m", "patternforge", "crack",
        hash_value,
        "--wordlist", wordlist,
        "--tool", tool,
        "--json",
    ]

    # Add hash type if provided
    if hash_type:
        type_map = {"md5": 0, "sha1": 100, "sha256": 1400}
        if hash_type.lower() in type_map:
            cmd.extend(["--type", str(type_map[hash_type.lower()])])

    # Build display command (for learning)
    cmd_str = f"patternforge crack {hash_value[:16]}... --wordlist {wordlist}"
    if tool != "auto":
        cmd_str += f" --tool {tool}"

    if on_progress:
        on_progress(f"Running: {cmd_str}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode == 0 and result.stdout:
            try:
                data = json.loads(result.stdout)
                crack_result = CrackResult.from_json(data, cmd_str)

                # Add the equivalent hashcat/john command for learning
                if crack_result.tool:
                    if "hashcat" in crack_result.tool.lower():
                        type_flag = ""
                        if hash_type:
                            type_map = {"md5": 0, "sha1": 100, "sha256": 1400}
                            type_flag = f"-m {type_map.get(hash_type.lower(), 0)} "
                        crack_result.command = f"hashcat {type_flag}{hash_value[:16]}... {wordlist}.txt"
                    elif "john" in crack_result.tool.lower():
                        crack_result.command = f"john --wordlist={wordlist}.txt hash.txt"

                return crack_result
            except json.JSONDecodeError:
                return CrackResult.error_result(
                    "Invalid JSON from PatternForge",
                    cmd_str
                )
        else:
            if "NOT_FOUND" in (result.stdout or ""):
                return CrackResult(
                    success=False,
                    command=cmd_str,
                )
            return CrackResult.error_result(
                result.stderr or "Crack failed",
                cmd_str
            )

    except subprocess.TimeoutExpired:
        return CrackResult.error_result(
            f"Crack timed out after {timeout}s",
            cmd_str
        )
    except FileNotFoundError:
        return CrackResult.error_result(
            "PatternForge not installed",
            "pip install patternforge"
        )
    except Exception as e:
        return CrackResult.error_result(str(e), cmd_str)


def check_patternforge() -> bool:
    """Check if PatternForge is available."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "patternforge", "--version"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_available_wordlists() -> list[str]:
    """Get list of available bundled wordlists."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "patternforge", "wordlists"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            # Parse output for wordlist names
            lines = result.stdout.strip().split('\n')
            wordlists = []
            for line in lines:
                # Look for lines that look like wordlist entries
                line = line.strip()
                if line and not line.startswith(('─', '╭', '╰', '│', ' ')):
                    # Extract just the name
                    parts = line.split()
                    if parts:
                        wordlists.append(parts[0])
            return wordlists
    except Exception:
        pass
    return ["common", "rockyou", "names"]  # Fallback defaults
