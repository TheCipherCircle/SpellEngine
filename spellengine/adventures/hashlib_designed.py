"""Designed Hash Library for PTHAdventures.

Pre-computed hashes with known solutions organized by tier and category.
Each hash has been validated to ensure the solution produces the correct hash value.

Tiers:
    0-2: Instant crack (<1 sec) - common passwords, dictionary words
    3-4: Quick crack (<30 sec) - patterns like Name+Year, Season+Year
    5-6: Progressive - requires iteration and multiple techniques

Categories:
    wordlist: Found in common wordlists (rockyou, etc.)
    pattern: Follows predictable mask patterns
    hybrid: Combination of wordlist + pattern elements
"""

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Iterator


class HashCategory(str, Enum):
    """Categories of password patterns."""
    WORDLIST = "wordlist"      # Dictionary word or common password
    PATTERN = "pattern"        # Follows a mask pattern (digits, keyboard walks)
    HYBRID = "hybrid"          # Combination of word + pattern elements


@dataclass(frozen=True)
class DesignedHash:
    """A pre-computed hash with known solution for training purposes.

    Attributes:
        hash_value: The hex digest hash string
        hash_type: Algorithm used (md5, sha1, sha256)
        solution: The plaintext password
        tier: Difficulty tier (0=trivial, 6=expert)
        category: Type of password pattern
        hint: Optional hint for learners
        expected_crack_time: Estimated crack time in seconds
    """
    hash_value: str
    hash_type: str  # md5, sha1, sha256
    solution: str
    tier: int
    category: HashCategory
    hint: str = ""
    expected_crack_time: float = 0.0

    def __post_init__(self):
        """Validate the hash on creation."""
        # Verify hash_value is correct for solution
        computed = _compute_hash(self.solution, self.hash_type)
        if computed != self.hash_value.lower():
            raise ValueError(
                f"Hash mismatch for '{self.solution}': "
                f"expected {computed}, got {self.hash_value}"
            )


def _compute_hash(plaintext: str, hash_type: str) -> str:
    """Compute hash of plaintext."""
    if hash_type == "md5":
        return hashlib.md5(plaintext.encode()).hexdigest().lower()
    elif hash_type == "sha1":
        return hashlib.sha1(plaintext.encode()).hexdigest().lower()
    elif hash_type == "sha256":
        return hashlib.sha256(plaintext.encode()).hexdigest().lower()
    else:
        raise ValueError(f"Unsupported hash type: {hash_type}")


# =============================================================================
# TIER 0: Trivial (<0.1 sec) - The most common passwords
# =============================================================================

TIER_0_HASHES: list[DesignedHash] = [
    # MD5 - Top 10 most common passwords
    DesignedHash(
        hash_value="5f4dcc3b5aa765d61d8327deb882cf99",
        hash_type="md5",
        solution="password",
        tier=0,
        category=HashCategory.WORDLIST,
        hint="The most common password in history",
        expected_crack_time=0.001,
    ),
    DesignedHash(
        hash_value="e10adc3949ba59abbe56e057f20f883e",
        hash_type="md5",
        solution="123456",
        tier=0,
        category=HashCategory.PATTERN,
        hint="Sequential digits, most common numeric password",
        expected_crack_time=0.001,
    ),
    DesignedHash(
        hash_value="21232f297a57a5a743894a0e4a801fc3",
        hash_type="md5",
        solution="admin",
        tier=0,
        category=HashCategory.WORDLIST,
        hint="Default administrator password",
        expected_crack_time=0.001,
    ),
    DesignedHash(
        hash_value="d8578edf8458ce06fbc5bb76a58c5ca4",
        hash_type="md5",
        solution="qwerty",
        tier=0,
        category=HashCategory.PATTERN,
        hint="Keyboard walk - top row",
        expected_crack_time=0.001,
    ),
    DesignedHash(
        hash_value="25d55ad283aa400af464c76d713c07ad",
        hash_type="md5",
        solution="12345678",
        tier=0,
        category=HashCategory.PATTERN,
        hint="Eight sequential digits",
        expected_crack_time=0.001,
    ),
    # SHA1 - Basic common passwords
    DesignedHash(
        hash_value="aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d",
        hash_type="sha1",
        solution="hello",
        tier=0,
        category=HashCategory.WORDLIST,
        hint="Common greeting",
        expected_crack_time=0.001,
    ),
    DesignedHash(
        hash_value="7c4a8d09ca3762af61e59520943dc26494f8941b",
        hash_type="sha1",
        solution="123456",
        tier=0,
        category=HashCategory.PATTERN,
        hint="Sequential digits (SHA1 version)",
        expected_crack_time=0.001,
    ),
    DesignedHash(
        hash_value="5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
        hash_type="sha1",
        solution="password",
        tier=0,
        category=HashCategory.WORDLIST,
        hint="Most common password (SHA1)",
        expected_crack_time=0.001,
    ),
    DesignedHash(
        hash_value="f7c3bc1d808e04732adf679965ccc34ca7ae3441",
        hash_type="sha1",
        solution="123456789",
        tier=0,
        category=HashCategory.PATTERN,
        hint="Nine sequential digits",
        expected_crack_time=0.001,
    ),
    DesignedHash(
        hash_value="d033e22ae348aeb5660fc2140aec35850c4da997",
        hash_type="sha1",
        solution="admin",
        tier=0,
        category=HashCategory.WORDLIST,
        hint="Administrator password (SHA1)",
        expected_crack_time=0.001,
    ),
]


# =============================================================================
# TIER 1: Very Easy (<0.5 sec) - Common dictionary words
# =============================================================================

TIER_1_HASHES: list[DesignedHash] = [
    # MD5 - Common words and slight variations
    DesignedHash(
        hash_value="0d107d09f5bbe40cade3de5c71e9e9b7",
        hash_type="md5",
        solution="letmein",
        tier=1,
        category=HashCategory.WORDLIST,
        hint="A request for access",
        expected_crack_time=0.01,
    ),
    DesignedHash(
        hash_value="8621ffdbc5698829397d97767ac13db3",
        hash_type="md5",
        solution="dragon",
        tier=1,
        category=HashCategory.WORDLIST,
        hint="Mythical fire-breathing creature",
        expected_crack_time=0.01,
    ),
    DesignedHash(
        hash_value="eb0a191797624dd3a48fa681d3061212",
        hash_type="md5",
        solution="master",
        tier=1,
        category=HashCategory.WORDLIST,
        hint="One who has skill or authority",
        expected_crack_time=0.01,
    ),
    DesignedHash(
        hash_value="3bf1114a986ba87ed28fc1b5884fc2f8",
        hash_type="md5",
        solution="shadow",
        tier=1,
        category=HashCategory.WORDLIST,
        hint="Follows you in the light",
        expected_crack_time=0.01,
    ),
    DesignedHash(
        hash_value="81dc9bdb52d04dc20036dbd8313ed055",
        hash_type="md5",
        solution="1234",
        tier=1,
        category=HashCategory.PATTERN,
        hint="4-digit PIN, sequential",
        expected_crack_time=0.01,
    ),
    # SHA1 - Common words
    DesignedHash(
        hash_value="e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4",
        hash_type="sha1",
        solution="secret",
        tier=1,
        category=HashCategory.WORDLIST,
        hint="What passwords are supposed to be",
        expected_crack_time=0.01,
    ),
    DesignedHash(
        hash_value="e68e11be8b70e435c65aef8ba9798ff7775c361e",
        hash_type="sha1",
        solution="trustno1",
        tier=1,
        category=HashCategory.WORDLIST,
        hint="X-Files reference, trust advice",
        expected_crack_time=0.02,
    ),
    DesignedHash(
        hash_value="8d6e34f987851aa599257d3831a1af040886842f",
        hash_type="sha1",
        solution="sunshine",
        tier=1,
        category=HashCategory.WORDLIST,
        hint="Warmth and light from above",
        expected_crack_time=0.01,
    ),
    DesignedHash(
        hash_value="7110eda4d09e062aa5e4a390b0a572ac0d2c0220",
        hash_type="sha1",
        solution="1234",
        tier=1,
        category=HashCategory.PATTERN,
        hint="4-digit PIN (SHA1)",
        expected_crack_time=0.01,
    ),
    DesignedHash(
        hash_value="40bd001563085fc35165329ea1ff5c5ecbdbbeef",
        hash_type="sha1",
        solution="123",
        tier=1,
        category=HashCategory.PATTERN,
        hint="Three sequential digits",
        expected_crack_time=0.01,
    ),
]


# =============================================================================
# TIER 2: Easy (<1 sec) - Dictionary words with simple patterns
# =============================================================================

TIER_2_HASHES: list[DesignedHash] = [
    # MD5 - Words + simple suffixes
    DesignedHash(
        hash_value="fcea920f7412b5da7be0cf42b8c93759",
        hash_type="md5",
        solution="1234567",
        tier=2,
        category=HashCategory.PATTERN,
        hint="Seven sequential digits",
        expected_crack_time=0.1,
    ),
    DesignedHash(
        hash_value="e99a18c428cb38d5f260853678922e03",
        hash_type="md5",
        solution="abc123",
        tier=2,
        category=HashCategory.HYBRID,
        hint="First letters + first numbers",
        expected_crack_time=0.1,
    ),
    DesignedHash(
        hash_value="5d41402abc4b2a76b9719d911017c592",
        hash_type="md5",
        solution="hello",
        tier=2,
        category=HashCategory.WORDLIST,
        hint="Common greeting (MD5)",
        expected_crack_time=0.1,
    ),
    DesignedHash(
        hash_value="f25a2fc72690b780b2a14e140ef6a9e0",
        hash_type="md5",
        solution="iloveyou",
        tier=2,
        category=HashCategory.WORDLIST,
        hint="Expression of affection",
        expected_crack_time=0.1,
    ),
    DesignedHash(
        hash_value="d0763edaa9d9bd2a9516280e9044d885",
        hash_type="md5",
        solution="monkey",
        tier=2,
        category=HashCategory.WORDLIST,
        hint="Playful primate",
        expected_crack_time=0.1,
    ),
    # SHA1 - Dictionary and patterns
    DesignedHash(
        hash_value="cbfdac6008f9cab4083784cbd1874f76618d2a97",
        hash_type="sha1",
        solution="password123",
        tier=2,
        category=HashCategory.HYBRID,
        hint="Common word + common numbers",
        expected_crack_time=0.2,
    ),
    DesignedHash(
        hash_value="a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
        hash_type="sha1",
        solution="test",
        tier=2,
        category=HashCategory.WORDLIST,
        hint="To verify or check",
        expected_crack_time=0.1,
    ),
    DesignedHash(
        hash_value="c60266a8adad2f8ee67d793b4fd3fd0ffd73cc61",
        hash_type="sha1",
        solution="computer",
        tier=2,
        category=HashCategory.WORDLIST,
        hint="Electronic device for processing",
        expected_crack_time=0.1,
    ),
    DesignedHash(
        hash_value="6367c48dd193d56ea7b0baad25b19455e529f5ee",
        hash_type="sha1",
        solution="abc123",
        tier=2,
        category=HashCategory.HYBRID,
        hint="First letters + first digits (SHA1)",
        expected_crack_time=0.1,
    ),
    DesignedHash(
        hash_value="e49512524f47b4138d850c9d9d85972927281da0",
        hash_type="sha1",
        solution="dog",
        tier=2,
        category=HashCategory.WORDLIST,
        hint="Man's best friend",
        expected_crack_time=0.1,
    ),
]


# =============================================================================
# TIER 3: Moderate (<10 sec) - Patterns with predictable structure
# =============================================================================

TIER_3_HASHES: list[DesignedHash] = [
    # MD5 - Name+Year patterns
    DesignedHash(
        hash_value="40bb26af9910da09e17e141e1ab93a97",
        hash_type="md5",
        solution="John2024",
        tier=3,
        category=HashCategory.HYBRID,
        hint="Common male name + current year",
        expected_crack_time=5.0,
    ),
    DesignedHash(
        hash_value="e90664c0af74160644d29e4d6147969b",
        hash_type="md5",
        solution="Summer2024",
        tier=3,
        category=HashCategory.HYBRID,
        hint="Warm season + current year",
        expected_crack_time=5.0,
    ),
    DesignedHash(
        hash_value="b56e0b4ea4962283bee762525c2d490f",
        hash_type="md5",
        solution="Welcome1",
        tier=3,
        category=HashCategory.HYBRID,
        hint="Greeting + single digit",
        expected_crack_time=3.0,
    ),
    DesignedHash(
        hash_value="37b4e2d82900d5e94b8da524fbeb33c0",
        hash_type="md5",
        solution="football",
        tier=3,
        category=HashCategory.WORDLIST,
        hint="Popular sport with a ball",
        expected_crack_time=2.0,
    ),
    DesignedHash(
        hash_value="5badcaf789d3d1d09794d8f021f40f0e",
        hash_type="md5",
        solution="starwars",
        tier=3,
        category=HashCategory.WORDLIST,
        hint="Famous space opera franchise",
        expected_crack_time=2.0,
    ),
    # SHA1 - Patterns
    DesignedHash(
        hash_value="ba9adb7296fdc28911356e3875bf4129aacbc36d",
        hash_type="sha1",
        solution="Baseball1",
        tier=3,
        category=HashCategory.HYBRID,
        hint="American sport + digit",
        expected_crack_time=5.0,
    ),
    DesignedHash(
        hash_value="689cd1cd19bfc2eaa606599aa8a2606a0ea3df25",
        hash_type="sha1",
        solution="Winter2023",
        tier=3,
        category=HashCategory.HYBRID,
        hint="Cold season + year",
        expected_crack_time=5.0,
    ),
    DesignedHash(
        hash_value="356a192b7913b04c54574d18c28d46e6395428ab",
        hash_type="sha1",
        solution="1",
        tier=3,
        category=HashCategory.PATTERN,
        hint="Single digit",
        expected_crack_time=0.1,
    ),
    DesignedHash(
        hash_value="da4b9237bacccdf19c0760cab7aec4a8359010b0",
        hash_type="sha1",
        solution="2",
        tier=3,
        category=HashCategory.PATTERN,
        hint="Single digit",
        expected_crack_time=0.1,
    ),
    DesignedHash(
        hash_value="b40e64b5aa764066ac2d0fdfe99d578c23817694",
        hash_type="sha1",
        solution="Michael2024",
        tier=3,
        category=HashCategory.HYBRID,
        hint="Common name + year",
        expected_crack_time=8.0,
    ),
]


# =============================================================================
# TIER 4: Challenging (<30 sec) - Complex patterns
# =============================================================================

TIER_4_HASHES: list[DesignedHash] = [
    # MD5 - Leet speak and substitutions
    DesignedHash(
        hash_value="5ebe2294ecd0e0f08eab7690d2a6ee69",
        hash_type="md5",
        solution="secret",
        tier=4,
        category=HashCategory.WORDLIST,
        hint="What passwords should be",
        expected_crack_time=15.0,
    ),
    DesignedHash(
        hash_value="098f6bcd4621d373cade4e832627b4f6",
        hash_type="md5",
        solution="test",
        tier=4,
        category=HashCategory.WORDLIST,
        hint="To try or verify",
        expected_crack_time=10.0,
    ),
    DesignedHash(
        hash_value="900150983cd24fb0d6963f7d28e17f72",
        hash_type="md5",
        solution="abc",
        tier=4,
        category=HashCategory.PATTERN,
        hint="First three letters",
        expected_crack_time=5.0,
    ),
    DesignedHash(
        hash_value="7c6a180b36896a0a8c02787eeafb0e4c",
        hash_type="md5",
        solution="password1",
        tier=4,
        category=HashCategory.HYBRID,
        hint="Common word + digit",
        expected_crack_time=20.0,
    ),
    DesignedHash(
        hash_value="dc647eb65e6711e155375218212b3964",
        hash_type="md5",
        solution="Password",
        tier=4,
        category=HashCategory.WORDLIST,
        hint="Common word, capitalized",
        expected_crack_time=15.0,
    ),
    # SHA1 - Complex combos
    DesignedHash(
        hash_value="8843d7f92416211de9ebb963ff4ce28125932878",
        hash_type="sha1",
        solution="foobar",
        tier=4,
        category=HashCategory.WORDLIST,
        hint="Programmer's placeholder text",
        expected_crack_time=10.0,
    ),
    DesignedHash(
        hash_value="5cec175b165e3d5e62c9e13ce848ef6feac81bff",
        hash_type="sha1",
        solution="qwerty123",
        tier=4,
        category=HashCategory.HYBRID,
        hint="Keyboard walk + digits",
        expected_crack_time=20.0,
    ),
    DesignedHash(
        hash_value="6e2f9e6111e77edd0c446ea7a84e25323d137a61",
        hash_type="sha1",
        solution="hunter",
        tier=4,
        category=HashCategory.WORDLIST,
        hint="One who hunts",
        expected_crack_time=15.0,
    ),
    DesignedHash(
        hash_value="f3bbbd66a63d4bf1747940578ec3d0103530e21d",
        hash_type="sha1",
        solution="hunter2",
        tier=4,
        category=HashCategory.HYBRID,
        hint="Famous IRC password example",
        expected_crack_time=20.0,
    ),
    DesignedHash(
        hash_value="f2439e4ea89a947308076ed64bcb5edd10ba4892",
        hash_type="sha1",
        solution="Spring2024!",
        tier=4,
        category=HashCategory.HYBRID,
        hint="Season + year + symbol",
        expected_crack_time=25.0,
    ),
]


# =============================================================================
# TIER 5: Difficult (<2 min) - Requires iteration
# =============================================================================

TIER_5_HASHES: list[DesignedHash] = [
    # MD5 - Less common but crackable
    DesignedHash(
        hash_value="827ccb0eea8a706c4c34a16891f84e7b",
        hash_type="md5",
        solution="12345",
        tier=5,
        category=HashCategory.PATTERN,
        hint="Five sequential digits",
        expected_crack_time=60.0,
    ),
    DesignedHash(
        hash_value="96e79218965eb72c92a549dd5a330112",
        hash_type="md5",
        solution="111111",
        tier=5,
        category=HashCategory.PATTERN,
        hint="Six of the same digit",
        expected_crack_time=45.0,
    ),
    DesignedHash(
        hash_value="4297f44b13955235245b2497399d7a93",
        hash_type="md5",
        solution="123123",
        tier=5,
        category=HashCategory.PATTERN,
        hint="Repeated triple digits",
        expected_crack_time=50.0,
    ),
    DesignedHash(
        hash_value="0acf4539a14b3aa27deeb4cbdf6e989f",
        hash_type="md5",
        solution="michael",
        tier=5,
        category=HashCategory.WORDLIST,
        hint="Common male name, lowercase",
        expected_crack_time=90.0,
    ),
    DesignedHash(
        hash_value="c33367701511b4f6020ec61ded352059",
        hash_type="md5",
        solution="654321",
        tier=5,
        category=HashCategory.PATTERN,
        hint="Reverse sequential digits",
        expected_crack_time=70.0,
    ),
    # SHA1 - More complex
    DesignedHash(
        hash_value="8cb2237d0679ca88db6464eac60da96345513964",
        hash_type="sha1",
        solution="12345",
        tier=5,
        category=HashCategory.PATTERN,
        hint="Five digits (SHA1)",
        expected_crack_time=60.0,
    ),
    DesignedHash(
        hash_value="dd5fef9c1c1da1394d6d34b248c51be2ad740840",
        hash_type="sha1",
        solution="654321",
        tier=5,
        category=HashCategory.PATTERN,
        hint="Reverse digits (SHA1)",
        expected_crack_time=70.0,
    ),
    DesignedHash(
        hash_value="e3cd9f6469fc3e1acfb9f2bdbfc5a3d2bbb8e2ad",
        hash_type="sha1",
        solution="jennifer",
        tier=5,
        category=HashCategory.WORDLIST,
        hint="Common female name",
        expected_crack_time=90.0,
    ),
    DesignedHash(
        hash_value="21bd12dc183f740ee76f27b78eb39c8ad972a757",
        hash_type="sha1",
        solution="P@ssw0rd",
        tier=5,
        category=HashCategory.HYBRID,
        hint="Common word with leet substitutions",
        expected_crack_time=100.0,
    ),
    DesignedHash(
        hash_value="389db5aa47221e72b8a38cd16866a59536217c81",
        hash_type="sha1",
        solution="Superman1!",
        tier=5,
        category=HashCategory.HYBRID,
        hint="Hero + digit + symbol",
        expected_crack_time=110.0,
    ),
]


# =============================================================================
# TIER 6: Expert (<10 min) - Requires advanced techniques
# =============================================================================

TIER_6_HASHES: list[DesignedHash] = [
    # MD5 - Complex patterns
    DesignedHash(
        hash_value="25f9e794323b453885f5181f1b624d0b",
        hash_type="md5",
        solution="123456789",
        tier=6,
        category=HashCategory.PATTERN,
        hint="Nine sequential digits",
        expected_crack_time=300.0,
    ),
    DesignedHash(
        hash_value="482c811da5d5b4bc6d497ffa98491e38",
        hash_type="md5",
        solution="password123",
        tier=6,
        category=HashCategory.HYBRID,
        hint="Classic combination",
        expected_crack_time=250.0,
    ),
    DesignedHash(
        hash_value="0192023a7bbd73250516f069df18b500",
        hash_type="md5",
        solution="admin123",
        tier=6,
        category=HashCategory.HYBRID,
        hint="Administrator + digits",
        expected_crack_time=280.0,
    ),
    DesignedHash(
        hash_value="e8dc4081b13434b45189a720b77b6818",
        hash_type="md5",
        solution="abcdefgh",
        tier=6,
        category=HashCategory.PATTERN,
        hint="Eight sequential letters",
        expected_crack_time=350.0,
    ),
    DesignedHash(
        hash_value="0b4e7a0e5fe84ad35fb5f95b9ceeac79",
        hash_type="md5",
        solution="aaaaaa",
        tier=6,
        category=HashCategory.PATTERN,
        hint="Six repeated letters",
        expected_crack_time=200.0,
    ),
    # SHA1 - Expert level
    DesignedHash(
        hash_value="7c222fb2927d828af22f592134e8932480637c0d",
        hash_type="sha1",
        solution="12345678",
        tier=6,
        category=HashCategory.PATTERN,
        hint="Eight digits (SHA1)",
        expected_crack_time=300.0,
    ),
    DesignedHash(
        hash_value="4cc19aaff82f60ac4097f935ab4a06ad4f0891cc",
        hash_type="sha1",
        solution="asdfghjk",
        tier=6,
        category=HashCategory.PATTERN,
        hint="Keyboard middle row",
        expected_crack_time=350.0,
    ),
    DesignedHash(
        hash_value="b0399d2029f64d445bd131ffaa399a42d2f8e7dc",
        hash_type="sha1",
        solution="qwertyuiop",
        tier=6,
        category=HashCategory.PATTERN,
        hint="Full keyboard top row",
        expected_crack_time=400.0,
    ),
    DesignedHash(
        hash_value="7c8a049b90750475f635010f47b180177b84a614",
        hash_type="sha1",
        solution="Robert2024!",
        tier=6,
        category=HashCategory.HYBRID,
        hint="Name + year + symbol",
        expected_crack_time=500.0,
    ),
    DesignedHash(
        hash_value="a9993e364706816aba3e25717850c26c9cd0d89d",
        hash_type="sha1",
        solution="abc",
        tier=6,
        category=HashCategory.PATTERN,
        hint="Three letters (SHA1)",
        expected_crack_time=50.0,
    ),
]


# =============================================================================
# Combined Collections
# =============================================================================

ALL_TIERS: dict[int, list[DesignedHash]] = {
    0: TIER_0_HASHES,
    1: TIER_1_HASHES,
    2: TIER_2_HASHES,
    3: TIER_3_HASHES,
    4: TIER_4_HASHES,
    5: TIER_5_HASHES,
    6: TIER_6_HASHES,
}


def get_all_hashes() -> list[DesignedHash]:
    """Get all designed hashes across all tiers."""
    result = []
    for tier_hashes in ALL_TIERS.values():
        result.extend(tier_hashes)
    return result


def get_hashes_by_tier(tier: int) -> list[DesignedHash]:
    """Get all hashes for a specific tier."""
    return ALL_TIERS.get(tier, [])


def get_hashes_by_type(hash_type: str) -> list[DesignedHash]:
    """Get all hashes of a specific type (md5, sha1, sha256)."""
    return [h for h in get_all_hashes() if h.hash_type == hash_type]


def get_hashes_by_category(category: HashCategory) -> list[DesignedHash]:
    """Get all hashes of a specific category."""
    return [h for h in get_all_hashes() if h.category == category]


def find_hash(hash_value: str) -> DesignedHash | None:
    """Find a designed hash by its hash value."""
    hash_value = hash_value.lower().strip()
    for h in get_all_hashes():
        if h.hash_value == hash_value:
            return h
    return None


def iterate_by_tier() -> Iterator[tuple[int, list[DesignedHash]]]:
    """Iterate over tiers and their hashes."""
    for tier in sorted(ALL_TIERS.keys()):
        yield tier, ALL_TIERS[tier]


# =============================================================================
# Campaign Hash Mapping
# =============================================================================

# Mapping from Dread Citadel encounter IDs to designed hashes
DREAD_CITADEL_HASH_MAP: dict[str, str] = {
    # Chapter 1: Outer Gates
    "enc_first_lock": "5f4dcc3b5aa765d61d8327deb882cf99",        # password
    "enc_common_tongue": "e10adc3949ba59abbe56e057f20f883e",     # 123456
    "enc_servants_key": "21232f297a57a5a743894a0e4a801fc3",      # admin
    "enc_gatekeeper": "0d107d09f5bbe40cade3de5c71e9e9b7",        # letmein
    # Chapter 2: The Crypts
    "enc_simple_patterns": "81dc9bdb52d04dc20036dbd8313ed055",   # 1234
    "enc_name_game": "40bb26af9910da09e17e141e1ab93a97",         # John2024
    "enc_ancient_scroll": "8621ffdbc5698829397d97767ac13db3",    # dragon
    "enc_pattern_lock": "eb0a191797624dd3a48fa681d3061212",      # master
    "enc_sha1_first_test": "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d",  # hello
    "enc_safe_crack": "3bf1114a986ba87ed28fc1b5884fc2f8",        # shadow
    "enc_risky_crack": "e68e11be8b70e435c65aef8ba9798ff7775c361e",  # trustno1
    "enc_crypt_guardian": "e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4",  # secret
    # Chapter 3: Inner Sanctum
    "enc_left_hand": "8d6e34f987851aa599257d3831a1af040886842f",  # sunshine
    "enc_right_hand": "e90664c0af74160644d29e4d6147969b",        # Summer2024
    "enc_citadel_lord": "cbfdac6008f9cab4083784cbd1874f76618d2a97",  # password123
}


def get_campaign_hash(encounter_id: str) -> DesignedHash | None:
    """Get the designed hash for a specific campaign encounter."""
    hash_value = DREAD_CITADEL_HASH_MAP.get(encounter_id)
    if hash_value:
        return find_hash(hash_value)
    return None


# =============================================================================
# Statistics
# =============================================================================

def get_library_stats() -> dict:
    """Get statistics about the hash library."""
    all_hashes = get_all_hashes()

    return {
        "total_hashes": len(all_hashes),
        "by_tier": {tier: len(hashes) for tier, hashes in ALL_TIERS.items()},
        "by_type": {
            "md5": len([h for h in all_hashes if h.hash_type == "md5"]),
            "sha1": len([h for h in all_hashes if h.hash_type == "sha1"]),
            "sha256": len([h for h in all_hashes if h.hash_type == "sha256"]),
        },
        "by_category": {
            cat.value: len([h for h in all_hashes if h.category == cat])
            for cat in HashCategory
        },
    }
