"""Mathematical Validation Agent (MVA).

A specialized agent that validates mathematical accuracy across the PatternForge
pipeline. Maintains confidence scores, tracks performance, and exports observations
for future ML/neural network training.

Design Principles:
- Validation time must be proportional to workflow time
- Hash type is the primary indicator for expected duration
- Observations are exportable for training future models
- Self-validates when uncertain, self-remediates when validation fails
"""

import json
import math
import os
import time
import hashlib
import hmac
import psutil
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class ValidationStatus(Enum):
    """Result status of a validation check."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIPPED = "skipped"
    ABORTED = "aborted"


class ConfidenceLevel(Enum):
    """Confidence level categories."""
    HIGH = "high"          # 95%+ - spot check 1 in 100
    MEDIUM = "medium"      # 70-94% - validate 1 in 10
    LOW = "low"            # <70% - validate every run
    CRITICAL = "critical"  # 0% - halt workflow


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    component: str
    status: ValidationStatus
    expected: Any
    actual: Any
    discrepancy: float | None = None
    message: str = ""
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ComponentConfidence:
    """Confidence tracking for a single component."""
    component: str
    confidence: float = 0.5  # Start at 50%
    validations_total: int = 0
    validations_passed: int = 0
    validations_failed: int = 0
    last_validated: str | None = None
    last_result: str | None = None

    @property
    def level(self) -> ConfidenceLevel:
        """Get confidence level category."""
        if self.confidence >= 0.95:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.70:
            return ConfidenceLevel.MEDIUM
        elif self.confidence > 0:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.CRITICAL

    def record_pass(self) -> None:
        """Record a passed validation, incrementing confidence."""
        self.validations_total += 1
        self.validations_passed += 1
        # Asymptotic approach to 1.0
        self.confidence = self.confidence + (1.0 - self.confidence) * 0.05
        self.last_validated = datetime.now().isoformat()
        self.last_result = "pass"

    def record_fail(self) -> None:
        """Record a failed validation, dropping confidence."""
        self.validations_total += 1
        self.validations_failed += 1
        # Trust drops fast
        self.confidence *= 0.7
        self.last_validated = datetime.now().isoformat()
        self.last_result = "fail"

    def record_critical(self) -> None:
        """Record a critical failure, zeroing confidence."""
        self.validations_total += 1
        self.validations_failed += 1
        self.confidence = 0.0
        self.last_validated = datetime.now().isoformat()
        self.last_result = "critical"


@dataclass
class ObservationRecord:
    """A single observation record for export/training."""
    timestamp: str
    component: str
    hash_type: str | None
    corpus_size: int | None
    workflow_duration_ms: float
    validation_duration_ms: float
    result: str
    confidence_before: float
    confidence_after: float
    discrepancy: float | None = None
    details: dict = field(default_factory=dict)


@dataclass
class TimingBaseline:
    """Timing baseline for a hash type or operation."""
    hash_type: str
    operation: str
    mean_ms: float
    std_dev_ms: float
    sample_count: int
    last_updated: str


# Hash type speed categories (passwords per second on typical GPU)
HASH_TYPE_SPEED = {
    # Fast hashes
    0: "fast",       # MD5
    100: "fast",     # SHA1
    1000: "fast",    # NTLM
    5600: "fast",    # NTLMv2
    # Medium hashes
    1400: "medium",  # SHA256
    1700: "medium",  # SHA512
    # Slow hashes
    500: "slow",     # MD5crypt
    1800: "slow",    # SHA512crypt
    3200: "slow",    # bcrypt
    # Very slow hashes
    13400: "very_slow",  # Argon2
}

# Validation time budgets by hash speed category
VALIDATION_BUDGETS = {
    "fast": {"spot_ms": 50, "light_ms": 200, "standard_ms": 500, "deep_pct": 0.02},
    "medium": {"spot_ms": 100, "light_ms": 500, "standard_ms": 1000, "deep_pct": 0.03},
    "slow": {"spot_ms": 200, "light_ms": 1000, "standard_ms": 2000, "deep_pct": 0.05},
    "very_slow": {"spot_ms": 500, "light_ms": 2000, "standard_ms": 5000, "deep_pct": 0.10},
}


class MathValidationAgent:
    """Mathematical Validation Agent for PatternForge pipeline.

    Validates mathematical accuracy, tracks confidence, exports observations.
    """

    def __init__(
        self,
        observations_dir: Path | str = "observations",
        auto_save: bool = True,
    ):
        """Initialize the Mathematical Validation Agent.

        Args:
            observations_dir: Directory for exportable observation data
            auto_save: Whether to auto-save observations after each validation
        """
        self.observations_dir = Path(observations_dir)
        self.auto_save = auto_save

        # Component confidence tracking
        self.confidence_scores: dict[str, ComponentConfidence] = {}

        # Timing baselines (learned over time)
        self.timing_baselines: dict[str, TimingBaseline] = {}

        # Current validation run state
        self.current_workflow: str | None = None
        self.workflow_start_time: float | None = None

        # Observation history (in-memory buffer)
        self._observation_buffer: list[ObservationRecord] = []

        # Load existing state if available
        self._load_state()

    def _load_state(self) -> None:
        """Load existing confidence scores and timing baselines."""
        self.observations_dir.mkdir(parents=True, exist_ok=True)

        # Load confidence scores
        confidence_file = self.observations_dir / "confidence_scores.json"
        if confidence_file.exists():
            try:
                with open(confidence_file) as f:
                    data = json.load(f)
                for name, values in data.items():
                    self.confidence_scores[name] = ComponentConfidence(**values)
            except (json.JSONDecodeError, TypeError):
                pass  # Start fresh if corrupted

        # Load timing baselines
        timing_file = self.observations_dir / "timing_baselines.json"
        if timing_file.exists():
            try:
                with open(timing_file) as f:
                    data = json.load(f)
                for key, values in data.items():
                    self.timing_baselines[key] = TimingBaseline(**values)
            except (json.JSONDecodeError, TypeError):
                pass

    def _save_state(self) -> None:
        """Save confidence scores and timing baselines."""
        self.observations_dir.mkdir(parents=True, exist_ok=True)

        # Save confidence scores
        confidence_file = self.observations_dir / "confidence_scores.json"
        data = {name: asdict(conf) for name, conf in self.confidence_scores.items()}
        with open(confidence_file, "w") as f:
            json.dump(data, f, indent=2)

        # Save timing baselines
        timing_file = self.observations_dir / "timing_baselines.json"
        data = {key: asdict(baseline) for key, baseline in self.timing_baselines.items()}
        with open(timing_file, "w") as f:
            json.dump(data, f, indent=2)

    def _append_observation(self, record: ObservationRecord) -> None:
        """Append an observation record to the history file."""
        self._observation_buffer.append(record)

        if self.auto_save:
            history_file = self.observations_dir / "validation_history.jsonl"
            with open(history_file, "a") as f:
                f.write(json.dumps(asdict(record)) + "\n")

    def _append_anomaly(self, record: ObservationRecord, reason: str) -> None:
        """Append an anomaly record."""
        anomaly_file = self.observations_dir / "anomalies.jsonl"
        anomaly_data = asdict(record)
        anomaly_data["anomaly_reason"] = reason
        with open(anomaly_file, "a") as f:
            f.write(json.dumps(anomaly_data) + "\n")

    def get_confidence(self, component: str) -> ComponentConfidence:
        """Get or create confidence tracker for a component."""
        if component not in self.confidence_scores:
            self.confidence_scores[component] = ComponentConfidence(component=component)
        return self.confidence_scores[component]

    def get_validation_budget_ms(
        self,
        hash_type: int | None = None,
        workflow_duration_ms: float = 1000,
    ) -> float:
        """Calculate validation time budget based on context.

        Args:
            hash_type: Hashcat mode number (affects speed category)
            workflow_duration_ms: Duration of the workflow being validated

        Returns:
            Maximum milliseconds to spend on validation
        """
        # Determine speed category (note: hash_type=0 is valid, so check for None explicitly)
        speed = HASH_TYPE_SPEED.get(hash_type, "medium") if hash_type is not None else "medium"
        budget = VALIDATION_BUDGETS[speed]

        # Scale by workflow duration
        if workflow_duration_ms < 1000:
            return budget["spot_ms"]
        elif workflow_duration_ms < 10000:
            return budget["light_ms"]
        elif workflow_duration_ms < 60000:
            return budget["standard_ms"]
        else:
            return workflow_duration_ms * budget["deep_pct"]

    def should_validate(self, component: str) -> bool:
        """Determine if we should validate this component based on confidence.

        High confidence components are spot-checked less frequently.
        """
        conf = self.get_confidence(component)
        level = conf.level

        if level == ConfidenceLevel.CRITICAL:
            return True  # Always validate critical
        elif level == ConfidenceLevel.LOW:
            return True  # Always validate low confidence
        elif level == ConfidenceLevel.MEDIUM:
            # Validate 1 in 10
            return (conf.validations_total % 10) == 0
        else:  # HIGH
            # Validate 1 in 100
            return (conf.validations_total % 100) == 0

    # =========================================================================
    # SAFETY CONTROLS
    # =========================================================================

    def check_system_health(self) -> tuple[bool, str | None]:
        """Check for system health issues that should abort workflow.

        Returns:
            (is_healthy, error_message)
        """
        # Check memory
        memory = psutil.virtual_memory()
        if memory.percent > 95:
            return False, f"Memory pressure critical: {memory.percent}% used"

        # Check disk
        disk = psutil.disk_usage(str(self.observations_dir))
        if disk.percent > 98:
            return False, f"Disk nearly full: {disk.percent}% used"

        # Check if disk has enough space for observations (at least 10MB)
        if disk.free < 10 * 1024 * 1024:
            return False, f"Disk space critically low: {disk.free / 1024 / 1024:.1f}MB free"

        return True, None

    def abort_workflow(self, reason: str) -> None:
        """Abort the current workflow due to critical issue."""
        anomaly_record = ObservationRecord(
            timestamp=datetime.now().isoformat(),
            component="system",
            hash_type=None,
            corpus_size=None,
            workflow_duration_ms=0,
            validation_duration_ms=0,
            result="aborted",
            confidence_before=0,
            confidence_after=0,
            details={"abort_reason": reason},
        )
        self._append_anomaly(anomaly_record, reason)
        raise RuntimeError(f"MVA ABORT: {reason}")

    # =========================================================================
    # VALIDATION METHODS
    # =========================================================================

    def validate_mask_extraction(
        self,
        password: str,
        extracted_mask: str,
    ) -> ValidationResult:
        """Validate that a password produces the correct mask.

        Args:
            password: The original password
            extracted_mask: The mask extracted by SCARAB

        Returns:
            ValidationResult with pass/fail status
        """
        start_time = time.perf_counter()

        # Independently compute the expected mask
        expected_mask = ""
        for char in password:
            if char.islower():
                expected_mask += "?l"
            elif char.isupper():
                expected_mask += "?u"
            elif char.isdigit():
                expected_mask += "?d"
            else:
                expected_mask += "?s"

        duration_ms = (time.perf_counter() - start_time) * 1000

        if extracted_mask == expected_mask:
            status = ValidationStatus.PASS
            discrepancy = None
            message = "Mask extraction correct"
        else:
            status = ValidationStatus.FAIL
            discrepancy = 1.0  # Binary fail
            message = f"Expected {expected_mask}, got {extracted_mask}"

        return ValidationResult(
            component="scarab_mask_generator",
            status=status,
            expected=expected_mask,
            actual=extracted_mask,
            discrepancy=discrepancy,
            message=message,
            duration_ms=duration_ms,
        )

    def validate_keyspace_calculation(
        self,
        mask: str,
        calculated_keyspace: int,
        charset_sizes: dict[str, int] | None = None,
    ) -> ValidationResult:
        """Validate keyspace calculation for a mask.

        Args:
            mask: The mask string (e.g., "?l?l?l?d?d")
            calculated_keyspace: The keyspace calculated by the pipeline
            charset_sizes: Custom charset sizes (default: standard hashcat)

        Returns:
            ValidationResult with pass/fail status
        """
        start_time = time.perf_counter()

        # Default charset sizes (hashcat standard)
        sizes = charset_sizes or {
            "l": 26,   # lowercase
            "u": 26,   # uppercase
            "d": 10,   # digits
            "s": 33,   # special
            "a": 95,   # all printable
            "b": 256,  # binary
            "h": 16,   # hex lower
            "H": 16,   # hex upper
        }

        # Compute expected keyspace
        expected_keyspace = 1
        i = 0
        while i < len(mask):
            if mask[i] == "?" and i + 1 < len(mask):
                char_class = mask[i + 1]
                if char_class in sizes:
                    expected_keyspace *= sizes[char_class]
                i += 2
            else:
                # Literal character
                i += 1

        duration_ms = (time.perf_counter() - start_time) * 1000

        if calculated_keyspace == expected_keyspace:
            status = ValidationStatus.PASS
            discrepancy = None
            message = "Keyspace calculation correct"
        else:
            status = ValidationStatus.FAIL
            discrepancy = abs(calculated_keyspace - expected_keyspace) / expected_keyspace
            message = f"Expected {expected_keyspace}, got {calculated_keyspace}"

        return ValidationResult(
            component="keyspace_calculator",
            status=status,
            expected=expected_keyspace,
            actual=calculated_keyspace,
            discrepancy=discrepancy,
            message=message,
            duration_ms=duration_ms,
        )

    def validate_distribution_sum(
        self,
        distribution: dict[str, float],
        expected_sum: float = 100.0,
        tolerance: float = 0.01,
    ) -> ValidationResult:
        """Validate that a percentage distribution sums correctly.

        Args:
            distribution: Dict of category -> percentage
            expected_sum: Expected sum (default 100%)
            tolerance: Acceptable deviation

        Returns:
            ValidationResult with pass/fail status
        """
        start_time = time.perf_counter()

        actual_sum = sum(distribution.values())
        discrepancy = abs(actual_sum - expected_sum)

        duration_ms = (time.perf_counter() - start_time) * 1000

        if discrepancy <= tolerance:
            status = ValidationStatus.PASS
            message = f"Distribution sums to {actual_sum:.2f}%"
        else:
            status = ValidationStatus.FAIL
            message = f"Distribution sums to {actual_sum:.2f}%, expected {expected_sum}%"

        return ValidationResult(
            component="distribution_calculator",
            status=status,
            expected=expected_sum,
            actual=actual_sum,
            discrepancy=discrepancy,
            message=message,
            duration_ms=duration_ms,
        )

    def validate_hash_computation(
        self,
        password: str,
        expected_hash: str,
        hash_type: str,
        **kwargs,
    ) -> ValidationResult:
        """Validate that hash(password) produces expected hash.

        Args:
            password: The plaintext password
            expected_hash: The expected hash value
            hash_type: Type of hash ("md5", "sha1", "sha256", "ntlmv2", etc.)
            **kwargs: Additional parameters (username, domain for NTLMv2, etc.)

        Returns:
            ValidationResult with pass/fail status
        """
        start_time = time.perf_counter()

        try:
            if hash_type == "md5":
                computed = hashlib.md5(password.encode()).hexdigest()
            elif hash_type == "sha1":
                computed = hashlib.sha1(password.encode()).hexdigest()
            elif hash_type == "sha256":
                computed = hashlib.sha256(password.encode()).hexdigest()
            elif hash_type == "sha512":
                computed = hashlib.sha512(password.encode()).hexdigest()
            elif hash_type == "ntlmv2":
                computed = self._compute_ntlmv2(
                    password,
                    kwargs.get("username", ""),
                    kwargs.get("domain", ""),
                    kwargs.get("server_challenge", ""),
                    kwargs.get("client_challenge", ""),
                )
            else:
                return ValidationResult(
                    component="hash_computation",
                    status=ValidationStatus.SKIPPED,
                    expected=expected_hash,
                    actual=None,
                    message=f"Unsupported hash type: {hash_type}",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                )

            duration_ms = (time.perf_counter() - start_time) * 1000

            # Compare (case-insensitive for hex hashes)
            if computed.lower() == expected_hash.lower():
                status = ValidationStatus.PASS
                discrepancy = None
                message = "Hash computation verified"
            else:
                status = ValidationStatus.FAIL
                discrepancy = 1.0
                message = f"Hash mismatch"

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            status = ValidationStatus.FAIL
            computed = None
            discrepancy = 1.0
            message = f"Hash computation error: {e}"

        return ValidationResult(
            component="hash_computation",
            status=status,
            expected=expected_hash,
            actual=computed,
            discrepancy=discrepancy,
            message=message,
            duration_ms=duration_ms,
        )

    def _compute_ntlmv2(
        self,
        password: str,
        username: str,
        domain: str,
        server_challenge: str,
        client_challenge: str,
    ) -> str:
        """Compute NTLMv2 hash for validation.

        Returns the full hashcat-format hash string.
        """
        try:
            from Crypto.Hash import MD4
        except ImportError:
            raise RuntimeError("pycryptodome required for NTLMv2 validation")

        # Convert challenges from hex
        server_challenge_bytes = bytes.fromhex(server_challenge)
        client_challenge_bytes = bytes.fromhex(client_challenge)

        # Step 1: NT Hash = MD4(UTF-16LE(password))
        password_utf16 = password.encode("utf-16-le")
        md4 = MD4.new()
        md4.update(password_utf16)
        nt_hash = md4.digest()

        # Step 2: NTLMv2 Hash = HMAC-MD5(NT_Hash, UPPER(username) + domain)
        user_domain = (username.upper() + domain).encode("utf-16-le")
        ntlmv2_hash = hmac.new(nt_hash, user_domain, "md5").digest()

        # Step 3: Blob (simplified)
        blob = client_challenge_bytes

        # Step 4: NTProofStr = HMAC-MD5(NTLMv2_Hash, server_challenge + blob)
        nt_proof_str = hmac.new(ntlmv2_hash, server_challenge_bytes + blob, "md5").digest()

        # Return hashcat format
        return "{}::{}:{}:{}:{}".format(
            username,
            domain,
            server_challenge,
            nt_proof_str.hex(),
            blob.hex(),
        )

    def validate_optindex(
        self,
        mask: str,
        occurrence: int,
        total_corpus: int,
        calculated_optindex: float,
    ) -> ValidationResult:
        """Validate OptIndex calculation.

        Uses improved formula: (occurrence / total_corpus) / log10(keyspace + 1)

        Args:
            mask: The mask string
            occurrence: How many passwords match this mask
            total_corpus: Total passwords in corpus
            calculated_optindex: The OptIndex calculated by pipeline

        Returns:
            ValidationResult with pass/fail status
        """
        start_time = time.perf_counter()

        # Calculate keyspace
        keyspace = 1
        sizes = {"l": 26, "u": 26, "d": 10, "s": 33, "a": 95}
        i = 0
        while i < len(mask):
            if mask[i] == "?" and i + 1 < len(mask):
                char_class = mask[i + 1]
                if char_class in sizes:
                    keyspace *= sizes[char_class]
                i += 2
            else:
                i += 1

        # Improved OptIndex formula
        coverage = occurrence / total_corpus
        expected_optindex = coverage / math.log10(keyspace + 1)

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Allow 1% tolerance
        tolerance = 0.01
        discrepancy = abs(calculated_optindex - expected_optindex)

        if discrepancy <= tolerance * expected_optindex:
            status = ValidationStatus.PASS
            message = "OptIndex calculation correct"
        else:
            status = ValidationStatus.FAIL
            message = f"Expected {expected_optindex:.6f}, got {calculated_optindex:.6f}"

        return ValidationResult(
            component="optindex_calculator",
            status=status,
            expected=expected_optindex,
            actual=calculated_optindex,
            discrepancy=discrepancy,
            message=message,
            duration_ms=duration_ms,
        )

    # =========================================================================
    # VALIDATION ORCHESTRATION
    # =========================================================================

    def validate_component(
        self,
        component: str,
        validator: Callable[[], ValidationResult],
        hash_type: int | None = None,
        workflow_duration_ms: float = 1000,
        corpus_size: int | None = None,
        force: bool = False,
    ) -> ValidationResult | None:
        """Orchestrate validation of a component with confidence tracking.

        Args:
            component: Name of the component being validated
            validator: Callable that performs the actual validation
            hash_type: Hashcat mode for budget calculation
            workflow_duration_ms: Duration of workflow being validated
            corpus_size: Size of corpus (for observations)
            force: Force validation regardless of confidence

        Returns:
            ValidationResult if validated, None if skipped
        """
        # Check system health first
        healthy, error = self.check_system_health()
        if not healthy:
            self.abort_workflow(error)

        # Get confidence tracker
        conf = self.get_confidence(component)
        confidence_before = conf.confidence

        # Decide whether to validate
        if not force and not self.should_validate(component):
            return None  # Skip based on confidence

        # Get time budget
        budget_ms = self.get_validation_budget_ms(hash_type, workflow_duration_ms)

        # Run validation
        start_time = time.perf_counter()
        result = validator()
        actual_duration_ms = (time.perf_counter() - start_time) * 1000

        # Check if we exceeded budget
        if actual_duration_ms > budget_ms * 2:
            self._append_anomaly(
                ObservationRecord(
                    timestamp=datetime.now().isoformat(),
                    component=component,
                    hash_type=str(hash_type) if hash_type else None,
                    corpus_size=corpus_size,
                    workflow_duration_ms=workflow_duration_ms,
                    validation_duration_ms=actual_duration_ms,
                    result="warning",
                    confidence_before=confidence_before,
                    confidence_after=conf.confidence,
                    details={"budget_ms": budget_ms},
                ),
                f"Validation exceeded budget: {actual_duration_ms:.1f}ms > {budget_ms:.1f}ms",
            )

        # Update confidence based on result
        if result.status == ValidationStatus.PASS:
            conf.record_pass()
        elif result.status == ValidationStatus.FAIL:
            conf.record_fail()
            if conf.level == ConfidenceLevel.CRITICAL:
                self._append_anomaly(
                    ObservationRecord(
                        timestamp=datetime.now().isoformat(),
                        component=component,
                        hash_type=str(hash_type) if hash_type else None,
                        corpus_size=corpus_size,
                        workflow_duration_ms=workflow_duration_ms,
                        validation_duration_ms=actual_duration_ms,
                        result="critical",
                        confidence_before=confidence_before,
                        confidence_after=conf.confidence,
                        discrepancy=result.discrepancy,
                        details={"message": result.message},
                    ),
                    f"Component confidence dropped to critical: {result.message}",
                )

        # Record observation
        observation = ObservationRecord(
            timestamp=datetime.now().isoformat(),
            component=component,
            hash_type=str(hash_type) if hash_type else None,
            corpus_size=corpus_size,
            workflow_duration_ms=workflow_duration_ms,
            validation_duration_ms=actual_duration_ms,
            result=result.status.value,
            confidence_before=confidence_before,
            confidence_after=conf.confidence,
            discrepancy=result.discrepancy,
            details={"message": result.message},
        )
        self._append_observation(observation)

        # Save state
        if self.auto_save:
            self._save_state()

        return result

    # =========================================================================
    # SELF-VALIDATION & REMEDIATION
    # =========================================================================

    def self_validate(self) -> bool:
        """Validate the agent's own calculations.

        Returns:
            True if self-validation passes
        """
        # Test mask extraction
        test_cases = [
            ("Password1", "?u?l?l?l?l?l?l?l?d"),
            ("abc123", "?l?l?l?d?d?d"),
            ("ABC!@#", "?u?u?u?s?s?s"),
        ]

        for password, expected_mask in test_cases:
            result = self.validate_mask_extraction(password, expected_mask)
            if result.status != ValidationStatus.PASS:
                return False

        # Test keyspace calculation
        keyspace_tests = [
            ("?l?l?l", 26 * 26 * 26),
            ("?d?d?d?d", 10000),
            ("?u?l?d", 26 * 26 * 10),
        ]

        for mask, expected_ks in keyspace_tests:
            result = self.validate_keyspace_calculation(mask, expected_ks)
            if result.status != ValidationStatus.PASS:
                return False

        # Test distribution sum
        result = self.validate_distribution_sum({"a": 50.0, "b": 30.0, "c": 20.0})
        if result.status != ValidationStatus.PASS:
            return False

        return True

    def self_remediate(self) -> bool:
        """Attempt to remediate issues detected during self-validation.

        Returns:
            True if remediation successful
        """
        # For now, remediation means resetting to known-good state
        # Future: could include more sophisticated recovery

        # Clear potentially corrupted state
        self.confidence_scores.clear()
        self.timing_baselines.clear()

        # Re-run self-validation
        return self.self_validate()

    # =========================================================================
    # REPORTING
    # =========================================================================

    def generate_report(
        self,
        workflow_name: str = "Unknown",
        hash_type: str | None = None,
    ) -> str:
        """Generate a summary report.

        Args:
            workflow_name: Name of the workflow being reported
            hash_type: Hash type used in workflow

        Returns:
            Formatted report string
        """
        report_lines = [
            "MATHEMATICAL VALIDATION REPORT",
            "=" * 60,
            f"Timestamp: {datetime.now().isoformat()}",
            f"Workflow: {workflow_name}",
            f"Hash Type: {hash_type or 'N/A'}",
            "",
            "COMPONENT CONFIDENCE SCORES",
            "-" * 40,
        ]

        for name, conf in sorted(self.confidence_scores.items()):
            level = conf.level.value.upper()
            report_lines.append(
                f"  {name}: {conf.confidence:.1%} ({level}) "
                f"[{conf.validations_passed}/{conf.validations_total} passed]"
            )

        report_lines.extend([
            "",
            "RECENT OBSERVATIONS",
            "-" * 40,
        ])

        for obs in self._observation_buffer[-10:]:
            report_lines.append(
                f"  [{obs.timestamp[:19]}] {obs.component}: {obs.result} "
                f"({obs.validation_duration_ms:.1f}ms)"
            )

        report_lines.extend([
            "",
            "SYSTEM STATUS",
            "-" * 40,
        ])

        healthy, error = self.check_system_health()
        if healthy:
            report_lines.append("  System healthy")
        else:
            report_lines.append(f"  WARNING: {error}")

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(self.observations_dir))
        report_lines.extend([
            f"  Memory: {memory.percent}% used",
            f"  Disk: {disk.percent}% used",
            "",
            f"Observations exported: {self.observations_dir}/",
            "=" * 60,
        ])

        return "\n".join(report_lines)

    def propose_improvement(
        self,
        component: str,
        current_formula: str,
        proposed_formula: str,
        rationale: str,
        expected_impact: str,
    ) -> None:
        """Record an improvement proposal for discussion.

        Args:
            component: Component to improve
            current_formula: Current mathematical approach
            proposed_formula: Proposed improvement
            rationale: Why this change is suggested
            expected_impact: What impact is expected
        """
        proposals_file = self.observations_dir / "improvement_proposals.json"

        # Load existing proposals
        proposals = []
        if proposals_file.exists():
            try:
                with open(proposals_file) as f:
                    proposals = json.load(f)
            except json.JSONDecodeError:
                proposals = []

        # Add new proposal
        proposals.append({
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "current_formula": current_formula,
            "proposed_formula": proposed_formula,
            "rationale": rationale,
            "expected_impact": expected_impact,
            "status": "pending",
        })

        # Save
        with open(proposals_file, "w") as f:
            json.dump(proposals, f, indent=2)

    # =========================================================================
    # CROSS-AGENT COMMUNICATION
    # =========================================================================

    def answer_query(self, question: str, context: dict | None = None) -> str:
        """Answer a query from another agent (e.g., Cosmic).

        Args:
            question: The question being asked
            context: Optional context for the question

        Returns:
            String response to the query
        """
        question_lower = question.lower()

        # Status queries
        if "status" in question_lower:
            total_validations = sum(c.validations_total for c in self.confidence_scores.values())
            total_passed = sum(c.validations_passed for c in self.confidence_scores.values())
            total_failed = sum(c.validations_failed for c in self.confidence_scores.values())

            if total_validations == 0:
                return "MVA Status: No validations performed yet. Ready to validate."

            pass_rate = total_passed / total_validations * 100
            avg_confidence = sum(c.confidence for c in self.confidence_scores.values()) / len(self.confidence_scores) if self.confidence_scores else 0.5

            return (
                f"MVA Status: {total_validations} validations performed. "
                f"Pass rate: {pass_rate:.1f}% ({total_passed} passed, {total_failed} failed). "
                f"Average confidence: {avg_confidence:.1%}. "
                f"Components tracked: {list(self.confidence_scores.keys())}."
            )

        # Confidence queries
        if "confidence" in question_lower:
            if not self.confidence_scores:
                return "No confidence scores recorded yet."

            scores = [
                f"  {c.component}: {c.confidence:.1%} ({c.validations_passed}/{c.validations_total})"
                for c in self.confidence_scores.values()
            ]
            return "Component confidence scores:\n" + "\n".join(scores)

        # Component-specific queries
        for component_name in self.confidence_scores:
            if component_name in question_lower:
                c = self.confidence_scores[component_name]
                return (
                    f"Component '{component_name}': confidence={c.confidence:.1%}, "
                    f"validations={c.validations_total} (passed={c.validations_passed}, failed={c.validations_failed}), "
                    f"last_result={c.last_result}, last_validated={c.last_validated}"
                )

        # Capability queries
        if "can" in question_lower or "capable" in question_lower or "what" in question_lower:
            return (
                "MVA validates mathematical accuracy across the pipeline including: "
                "mask extraction, keyspace calculation, distribution analysis, "
                "OptIndex formula, and hash computations (including NTLMv2). "
                "I maintain confidence scores per component and calibrate validation "
                "intensity based on hash type speed categories."
            )

        # Default response
        return (
            "I am the Mathematical Validation Agent (MVA). "
            "I validate mathematical correctness across the pipeline, "
            "maintain confidence scores, and export observations for training. "
            "Ask me about: status, confidence, component names, or capabilities."
        )
