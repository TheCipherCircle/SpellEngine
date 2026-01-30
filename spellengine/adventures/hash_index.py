"""Campaign Hash Index for theatrical cracking.

Pre-computes an index of all hashes in a campaign for instant lookup,
enabling the theatrical cracking animation to reveal passwords
character-by-character without actually calling external tools.

This is the "boss encounter" experience - dramatic, timed reveals
that make password cracking feel like defeating a dungeon boss.
"""

from typing import TYPE_CHECKING

from spellengine.adventures.models import DifficultyLevel

if TYPE_CHECKING:
    from spellengine.adventures.models import Campaign, Encounter, EncounterVariant


class HashLookupResult:
    """Result of a hash lookup in the campaign index."""

    def __init__(
        self,
        found: bool,
        solution: str = "",
        encounter_id: str = "",
        difficulty: DifficultyLevel | None = None,
        hash_type: str = "",
        hints: list[str] | None = None,
    ):
        self.found = found
        self.solution = solution
        self.encounter_id = encounter_id
        self.difficulty = difficulty
        self.hash_type = hash_type
        self.hints = hints or []


class CampaignHashIndex:
    """Pre-computed index of all hashes in a campaign.

    Enables instant lookup of hash -> solution for theatrical cracking.
    This lets us show the dramatic character-by-character reveal without
    actually running hashcat/john.

    Think of it as the "boss health bar" - we know the answer, we just
    need to make defeating it feel epic.
    """

    def __init__(self, campaign: "Campaign") -> None:
        """Build the hash index for a campaign.

        Args:
            campaign: Campaign to index
        """
        self.campaign = campaign
        self._hash_to_solution: dict[str, HashLookupResult] = {}
        self._build_index()

    def _build_index(self) -> None:
        """Build the hash -> solution index from all encounters."""
        for chapter in self.campaign.chapters:
            for encounter in chapter.encounters:
                # Index the base encounter hash
                if encounter.hash and encounter.solution:
                    self._index_hash(
                        hash_value=encounter.hash,
                        solution=encounter.solution,
                        encounter_id=encounter.id,
                        hash_type=encounter.hash_type or "md5",
                        hint=encounter.hint,
                    )

                # Index difficulty variants
                if encounter.variants:
                    for difficulty, variant in encounter.variants.items():
                        self._index_hash(
                            hash_value=variant.hash,
                            solution=variant.solution,
                            encounter_id=encounter.id,
                            difficulty=difficulty,
                            hash_type=variant.hash_type,
                            hint=variant.hint,
                        )

    def _index_hash(
        self,
        hash_value: str,
        solution: str,
        encounter_id: str,
        hash_type: str,
        hint: str | None = None,
        difficulty: DifficultyLevel | None = None,
    ) -> None:
        """Add a hash to the index.

        Args:
            hash_value: The hash string
            solution: The plaintext solution
            encounter_id: Which encounter this belongs to
            hash_type: Type of hash (md5, sha1, etc.)
            hint: Optional hint text
            difficulty: Optional difficulty level for variants
        """
        # Normalize hash to lowercase
        hash_key = hash_value.lower().strip()

        self._hash_to_solution[hash_key] = HashLookupResult(
            found=True,
            solution=solution,
            encounter_id=encounter_id,
            difficulty=difficulty,
            hash_type=hash_type,
            hints=[hint] if hint else [],
        )

    def lookup(self, hash_value: str) -> HashLookupResult:
        """Look up a hash in the index.

        Args:
            hash_value: Hash to look up

        Returns:
            HashLookupResult with solution if found
        """
        hash_key = hash_value.lower().strip()
        return self._hash_to_solution.get(
            hash_key,
            HashLookupResult(found=False),
        )

    def get_theatrical_hints(self, hash_value: str) -> list[str]:
        """Get theatrical hints for a hash during cracking.

        These are displayed progressively during the crack animation
        to build tension.

        Args:
            hash_value: Hash being cracked

        Returns:
            List of hint strings to display progressively
        """
        result = self.lookup(hash_value)
        if not result.found:
            return []

        hints = []

        # Hash type hint
        hints.append(f"Analyzing target... {result.hash_type.upper()} detected")

        # Length hint
        solution_len = len(result.solution)
        hints.append(f"Password length: {solution_len} characters")

        # Character composition hints
        has_lower = any(c.islower() for c in result.solution)
        has_upper = any(c.isupper() for c in result.solution)
        has_digit = any(c.isdigit() for c in result.solution)
        has_special = any(not c.isalnum() for c in result.solution)

        composition = []
        if has_lower:
            composition.append("lowercase")
        if has_upper:
            composition.append("uppercase")
        if has_digit:
            composition.append("digits")
        if has_special:
            composition.append("special chars")

        if composition:
            hints.append(f"Contains: {', '.join(composition)}")

        # First character hint (for dramatic reveal start)
        hints.append(f"First character: {result.solution[0]}***")

        return hints

    def get_progressive_reveal(
        self,
        hash_value: str,
        progress: float,
    ) -> str:
        """Get the progressive character reveal for theatrical cracking.

        Args:
            hash_value: Hash being cracked
            progress: Progress from 0.0 to 1.0

        Returns:
            Partially revealed password string
        """
        result = self.lookup(hash_value)
        if not result.found:
            return "????????"

        solution = result.solution
        reveal_count = int(len(solution) * progress)

        # Build the reveal string
        revealed = solution[:reveal_count]
        hidden = "*" * (len(solution) - reveal_count)

        return revealed + hidden

    @property
    def hash_count(self) -> int:
        """Get the total number of indexed hashes."""
        return len(self._hash_to_solution)

    def get_stats(self) -> dict:
        """Get statistics about the hash index.

        Returns:
            Dict with index statistics
        """
        hash_types: dict[str, int] = {}
        difficulties: dict[str, int] = {}

        for result in self._hash_to_solution.values():
            # Count hash types
            ht = result.hash_type.upper()
            hash_types[ht] = hash_types.get(ht, 0) + 1

            # Count difficulties
            diff = result.difficulty.value if result.difficulty else "base"
            difficulties[diff] = difficulties.get(diff, 0) + 1

        return {
            "total_hashes": self.hash_count,
            "hash_types": hash_types,
            "difficulties": difficulties,
        }


def create_hash_index(campaign: "Campaign") -> CampaignHashIndex:
    """Create a hash index for a campaign.

    Args:
        campaign: Campaign to index

    Returns:
        CampaignHashIndex instance
    """
    return CampaignHashIndex(campaign)
