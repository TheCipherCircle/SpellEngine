"""Hash validation for adventure encounters.

Validates player guesses against actual MD5/SHA1/SHA256 hashes
instead of plaintext comparison.
"""

import hashlib
from typing import Literal

HashType = Literal["md5", "sha1", "sha256"]

SUPPORTED_HASH_TYPES: dict[str, int] = {
    "md5": 32,
    "sha1": 40,
    "sha256": 64,
}


def compute_hash(plaintext: str, hash_type: HashType) -> str:
    """Compute hash of plaintext.

    Args:
        plaintext: The password/answer to hash
        hash_type: Type of hash (md5, sha1, sha256)

    Returns:
        Lowercase hex digest of the hash
    """
    if hash_type == "md5":
        return hashlib.md5(plaintext.encode()).hexdigest().lower()
    elif hash_type == "sha1":
        return hashlib.sha1(plaintext.encode()).hexdigest().lower()
    elif hash_type == "sha256":
        return hashlib.sha256(plaintext.encode()).hexdigest().lower()
    else:
        raise ValueError(f"Unsupported hash type: {hash_type}")


def validate_crack(answer: str, target_hash: str, hash_type: HashType) -> bool:
    """Validate if answer produces the target hash.

    Args:
        answer: Player's guess (plaintext)
        target_hash: The hash to crack
        hash_type: Type of hash (md5, sha1, sha256)

    Returns:
        True if answer hashes to target_hash
    """
    if not target_hash or not hash_type:
        return False

    computed = compute_hash(answer, hash_type)
    return computed == target_hash.lower().strip()


def detect_hash_type(hash_string: str) -> HashType | None:
    """Attempt to detect hash type from string length.

    Args:
        hash_string: A hex hash string

    Returns:
        Detected hash type or None if unknown
    """
    hash_string = hash_string.strip().lower()

    # Must be valid hex
    try:
        int(hash_string, 16)
    except ValueError:
        return None

    length = len(hash_string)

    for hash_type, expected_length in SUPPORTED_HASH_TYPES.items():
        if length == expected_length:
            return hash_type  # type: ignore

    return None


def generate_hash_for_solution(solution: str, hash_type: HashType = "md5") -> str:
    """Generate a hash for a solution (useful for campaign authors).

    Args:
        solution: The plaintext solution
        hash_type: Type of hash to generate

    Returns:
        Hex digest hash string
    """
    return compute_hash(solution, hash_type)
