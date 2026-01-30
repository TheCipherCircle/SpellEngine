"""Password generator for Hashtopia-driven encounters.

Generates passwords from keyspace definitions using PatternForge engines.
This bridges the SpellEngine encounter system with PatternForge's
SCARAB analysis and EntropySmith generation capabilities.
"""

import hashlib
import random
import re
import tempfile
from pathlib import Path
from typing import Literal

from spellengine.adventures.keyspace import (
    ComplexityLevel,
    DiscoveryMethod,
    GenerationStrategy,
    KeyspaceDefinition,
    KeyspaceMeta,
)


class KeyspacePasswordGenerator:
    """Generates passwords from keyspace definitions using PatternForge.

    This generator creates passwords that match keyspace constraints,
    ensuring players using proper analysis tools will discover them
    naturally through the documented methodology.
    """

    def __init__(
        self,
        corpus_path: Path,
        use_patternforge: bool = True,
    ) -> None:
        """Initialize the password generator.

        Args:
            corpus_path: Path to the training corpus file
            use_patternforge: Whether to use PatternForge engines (if available)
        """
        self.corpus_path = Path(corpus_path)
        self.use_patternforge = use_patternforge

        # Load corpus into memory for fast access
        self._corpus: list[str] = []
        self._words: list[str] = []
        self._load_corpus()

        # PatternForge integration (lazy loaded)
        self._model_bundle = None
        self._generator = None

    def _load_corpus(self) -> None:
        """Load the training corpus from file."""
        if not self.corpus_path.exists():
            raise FileNotFoundError(f"Corpus not found: {self.corpus_path}")

        with open(self.corpus_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                self._corpus.append(line)

        # Extract pure word entries (no digits, no symbols)
        word_pattern = re.compile(r"^[a-zA-Z]+$")
        self._words = [w for w in self._corpus if word_pattern.match(w)]

    def _get_patternforge_model(self):
        """Lazily initialize PatternForge model bundle."""
        if self._model_bundle is not None:
            return self._model_bundle

        try:
            from patternforge.engines.scarab import SCARABAnalyzer

            analyzer = SCARABAnalyzer(
                mask_limit=500,
                min_mask_count=1,
                enable_tokens=True,
                enable_grammar=False,  # Grammar not needed for basic generation
            )

            self._model_bundle = analyzer.analyze(
                corpus_id="training_corpus",
                model_id="spellengine_model",
                corpus_path=self.corpus_path,
                name="SpellEngine Training Model",
            )

            return self._model_bundle
        except ImportError:
            # PatternForge not available, will use fallback
            return None

    def generate_for_keyspace(
        self,
        keyspace: KeyspaceDefinition,
        count: int = 1,
    ) -> list[str]:
        """Generate password(s) matching keyspace constraints.

        Args:
            keyspace: Keyspace definition with constraints
            count: Number of passwords to generate

        Returns:
            List of generated passwords
        """
        candidates = []

        # Try PatternForge if available and enabled
        if self.use_patternforge:
            candidates = self._generate_with_patternforge(keyspace, count)

        # Fallback to built-in generation
        if not candidates:
            candidates = self._generate_fallback(keyspace, count)

        return candidates[:count]

    def _generate_with_patternforge(
        self,
        keyspace: KeyspaceDefinition,
        count: int,
    ) -> list[str]:
        """Generate using PatternForge EntropySmith engine."""
        try:
            from patternforge.engines.entropysmith import EntropySmithGenerator
            from patternforge.models.artifacts import ConstraintParams

            model = self._get_patternforge_model()
            if model is None:
                return []

            # Map keyspace strategy to EntropySmith strategy
            strategy_map = {
                GenerationStrategy.MUTATIONS: "mutations",
                GenerationStrategy.GRAMMAR: "grammar",
                GenerationStrategy.SAMPLING: "sampling",
                GenerationStrategy.HYBRID: "hybrid",
            }

            # Set up constraints
            constraints = ConstraintParams(
                min_length=keyspace.min_length,
                max_length=keyspace.max_length,
            )

            # Create generator
            generator = EntropySmithGenerator(
                budget=count * 10,  # Generate extra for filtering
                strategy=strategy_map.get(keyspace.strategy, "mutations"),
                deduplicate=True,
                constraints=constraints,
            )

            # Generate candidates
            with tempfile.TemporaryDirectory() as tmpdir:
                artifacts = generator.generate(
                    model=model,
                    run_id="keyspace_gen",
                    output_dir=Path(tmpdir),
                    corpus_path=self.corpus_path,
                )

                # Read generated candidates
                candidates_file = Path(tmpdir) / "candidates.txt"
                if candidates_file.exists():
                    raw_lines = candidates_file.read_text().strip().split("\n")
                    # Filter out comments, empty lines, and invalid entries
                    candidates = [
                        line for line in raw_lines
                        if line and not line.startswith("#") and len(line) >= keyspace.min_length
                    ]

                    # Filter by mask if specified
                    if keyspace.mask:
                        candidates = [c for c in candidates if self._matches_mask(c, keyspace.mask)]

                    # Filter by token structure if specified
                    if keyspace.tokens:
                        token_filtered = self._filter_by_tokens(candidates, keyspace.tokens)
                        if token_filtered:
                            candidates = token_filtered

                    # If still no candidates after filtering, return empty to trigger fallback
                    if candidates:
                        return candidates[:count]

        except (ImportError, Exception):
            # PatternForge not available or error
            pass

        return []

    def _generate_fallback(
        self,
        keyspace: KeyspaceDefinition,
        count: int,
    ) -> list[str]:
        """Generate passwords using built-in logic (no PatternForge).

        This fallback ensures the system works even without PatternForge,
        while still respecting keyspace constraints.
        """
        candidates: list[str] = []

        # Filter corpus by length constraints
        valid_passwords = [
            p for p in self._corpus
            if keyspace.min_length <= len(p) <= keyspace.max_length
        ]

        # Filter by mask if specified
        if keyspace.mask:
            valid_passwords = [
                p for p in valid_passwords
                if self._matches_mask(p, keyspace.mask)
            ]

        # Filter by complexity
        if keyspace.complexity == ComplexityLevel.SIMPLE:
            # Simple: prefer single words or pure digits
            simple_pattern = re.compile(r"^([a-z]+|[A-Z]+|\d+)$")
            simple_candidates = [p for p in valid_passwords if simple_pattern.match(p)]
            if simple_candidates:
                valid_passwords = simple_candidates

        elif keyspace.complexity == ComplexityLevel.COMPOUND:
            # Compound: word+digit or capitalized patterns
            compound_pattern = re.compile(r"^[A-Za-z]+\d+$|^[A-Z][a-z]+\d+$")
            compound_candidates = [p for p in valid_passwords if compound_pattern.match(p)]
            if compound_candidates:
                valid_passwords = compound_candidates

        elif keyspace.complexity == ComplexityLevel.TRANSFORMED:
            # Transformed: leet speak or special characters
            transform_pattern = re.compile(r"[@$!#%^&*_\-]|[0-9].*[a-zA-Z].*[0-9]")
            transform_candidates = [p for p in valid_passwords if transform_pattern.search(p)]
            if transform_candidates:
                valid_passwords = transform_candidates

        # Apply token filters if specified
        if keyspace.tokens:
            valid_passwords = self._filter_by_tokens(valid_passwords, keyspace.tokens)

        # If we have valid passwords, sample from them
        if valid_passwords:
            if count >= len(valid_passwords):
                candidates = valid_passwords[:]
            else:
                candidates = random.sample(valid_passwords, count)
        else:
            # Generate synthetic passwords if no matches
            candidates = self._generate_synthetic(keyspace, count)

        return candidates

    def _matches_mask(self, password: str, mask: str) -> bool:
        """Check if a password matches a hashcat-style mask.

        Mask notation:
        - ?l = lowercase (a-z)
        - ?u = uppercase (A-Z)
        - ?d = digit (0-9)
        - ?s = symbol
        - ?a = any printable
        - Literal characters match themselves
        """
        if len(password) != len(mask) // 2 and "?" in mask:
            # Mask with placeholders has different length semantics
            pass

        # Parse mask into regex pattern
        pattern_parts = []
        i = 0
        while i < len(mask):
            if mask[i] == "?" and i + 1 < len(mask):
                char_class = mask[i + 1]
                if char_class == "l":
                    pattern_parts.append("[a-z]")
                elif char_class == "u":
                    pattern_parts.append("[A-Z]")
                elif char_class == "d":
                    pattern_parts.append("[0-9]")
                elif char_class == "s":
                    pattern_parts.append(r"[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?\\`~]")
                elif char_class == "a":
                    pattern_parts.append(".")
                else:
                    pattern_parts.append(re.escape(char_class))
                i += 2
            else:
                pattern_parts.append(re.escape(mask[i]))
                i += 1

        pattern = "^" + "".join(pattern_parts) + "$"
        return bool(re.match(pattern, password))

    def _filter_by_tokens(
        self,
        passwords: list[str],
        tokens: list[str],
    ) -> list[str]:
        """Filter passwords by token structure.

        Token types:
        - WORD: alphabetic characters
        - DIGIT: numeric characters
        - YEAR: 4-digit year (1900-2100)
        - SYMBOL: special characters
        """
        result = []
        for password in passwords:
            if self._has_token_structure(password, tokens):
                result.append(password)
        return result

    def _has_token_structure(self, password: str, tokens: list[str]) -> bool:
        """Check if password has the specified token structure."""
        # Build a regex pattern from tokens
        patterns = {
            "WORD": r"[a-zA-Z]+",
            "DIGIT": r"\d+",
            "YEAR": r"(19|20)\d{2}",
            "SYMBOL": r"[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?\\`~]+",
        }

        pattern_str = "^"
        for token in tokens:
            if token.upper() in patterns:
                pattern_str += patterns[token.upper()]
            else:
                # Literal token
                pattern_str += re.escape(token)
        pattern_str += "$"

        return bool(re.match(pattern_str, password))

    def _generate_synthetic(
        self,
        keyspace: KeyspaceDefinition,
        count: int,
    ) -> list[str]:
        """Generate synthetic passwords when corpus doesn't have matches."""
        candidates = []

        # Get base words that fit length constraints
        max_word_len = keyspace.max_length - 4  # Leave room for suffixes
        base_words = [
            w for w in self._words
            if len(w) >= 4 and len(w) <= max(6, max_word_len)
        ]

        if not base_words:
            base_words = ["password", "dragon", "master", "monkey", "shadow",
                         "sunshine", "princess", "welcome", "secret", "magic"]

        # Common years for year-based patterns
        years = ["2024", "2023", "2022", "2021", "2020", "1999", "1998", "1997"]
        digits = ["1", "12", "123", "99", "21", "69", "77", "88"]
        symbols = ["!", "@", "#", "_", "-"]

        for _ in range(count):
            word = random.choice(base_words)

            if keyspace.complexity == ComplexityLevel.SIMPLE:
                candidates.append(word.lower())

            elif keyspace.complexity == ComplexityLevel.COMPOUND:
                # Check if tokens hint at YEAR vs DIGIT
                tokens = keyspace.tokens or []
                if "YEAR" in [t.upper() for t in tokens]:
                    suffix = random.choice(years)
                else:
                    suffix = random.choice(digits)
                # Capitalize the word
                candidates.append(word.capitalize() + suffix)

            elif keyspace.complexity == ComplexityLevel.TRANSFORMED:
                # Apply leet transformations more consistently
                leet_map = {"a": "@", "e": "3", "i": "1", "o": "0", "s": "$"}
                transformed = ""
                # Apply at least one transformation
                applied = False
                for c in word:
                    if c.lower() in leet_map and (not applied or random.random() > 0.5):
                        transformed += leet_map[c.lower()]
                        applied = True
                    else:
                        transformed += c

                # Capitalize first letter
                if transformed and transformed[0].islower():
                    transformed = transformed[0].upper() + transformed[1:]

                # Check if SYMBOL is in tokens
                tokens = keyspace.tokens or []
                has_symbol = "SYMBOL" in [t.upper() for t in tokens]
                has_year = "YEAR" in [t.upper() for t in tokens]

                if has_symbol and has_year:
                    symbol = random.choice(symbols)
                    year = random.choice(years)
                    transformed = transformed + symbol + year
                elif has_symbol:
                    suffix = random.choice(["!", "@1", "#123", "_99", "!2024"])
                    transformed = transformed + suffix
                elif has_year:
                    year = random.choice(years)
                    transformed = transformed + year + "!"
                else:
                    suffix = random.choice(["!", "123!", "_2024", "@1"])
                    transformed = transformed + suffix

                candidates.append(transformed)

        return candidates

    def generate_hash(
        self,
        password: str,
        hash_type: Literal["md5", "sha1", "sha256", "sha512"] = "md5",
    ) -> str:
        """Generate a hash for a password.

        Args:
            password: The plaintext password
            hash_type: Hash algorithm to use

        Returns:
            Hex-encoded hash string
        """
        password_bytes = password.encode("utf-8")

        if hash_type == "md5":
            return hashlib.md5(password_bytes).hexdigest()
        elif hash_type == "sha1":
            return hashlib.sha1(password_bytes).hexdigest()
        elif hash_type == "sha256":
            return hashlib.sha256(password_bytes).hexdigest()
        elif hash_type == "sha512":
            return hashlib.sha512(password_bytes).hexdigest()
        else:
            raise ValueError(f"Unsupported hash type: {hash_type}")

    def generate_encounter_password(
        self,
        keyspace: KeyspaceDefinition,
        hash_type: str = "md5",
    ) -> tuple[str, str, KeyspaceMeta]:
        """Generate a complete encounter password with hash and metadata.

        Args:
            keyspace: Keyspace definition
            hash_type: Hash algorithm to use

        Returns:
            Tuple of (password, hash, keyspace_meta)
        """
        passwords = self.generate_for_keyspace(keyspace, count=1)
        if not passwords:
            raise ValueError("Failed to generate password for keyspace")

        password = passwords[0]
        hash_value = self.generate_hash(password, hash_type)

        meta = KeyspaceMeta(
            discovery_method=keyspace.discovery_method,
            tier=keyspace.tier,
            complexity=keyspace.complexity,
            source=keyspace.source,
        )

        return password, hash_value, meta
