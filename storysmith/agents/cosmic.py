"""Cosmic - Improvement Observer Agent.

A passive observer agent that collects data across the PatternForge ecosystem,
detects patterns and correlations, and provides insights for improvement.

Cosmic does not execute changes - it observes, analyzes, and proposes.

Design Principles:
- Observe everything, change nothing (passive)
- Accumulate knowledge over time (persistent memory)
- Cross-agent communication for deeper understanding
- Support Phase X initiatives (neural, ML, graph theory)
- Generate actionable insights on request
"""

import json
import statistics
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol
from collections import defaultdict


class ObservationSource(Enum):
    """Sources of observations."""
    PIPELINE = "pipeline"           # Pipeline execution events
    MVA = "mva"                     # Mathematical Validation Agent
    USER = "user"                   # User interactions
    SYSTEM = "system"              # System events (errors, performance)
    AGENT = "agent"                # Other agent activities
    EXTERNAL = "external"          # External tools (hashcat, john)


class InsightCategory(Enum):
    """Categories of insights."""
    PERFORMANCE = "performance"     # Speed, efficiency improvements
    ACCURACY = "accuracy"           # Correctness improvements
    USABILITY = "usability"         # User experience improvements
    ARCHITECTURE = "architecture"   # Structural improvements
    FEATURE = "feature"            # New capability opportunities
    RISK = "risk"                   # Potential issues detected


class ProposalStatus(Enum):
    """Status of improvement proposals."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    DEFERRED = "deferred"


@dataclass
class Observation:
    """A single observation from any source."""
    timestamp: str
    source: str
    event_type: str
    data: dict
    context: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class Pattern:
    """A detected pattern from observations."""
    pattern_id: str
    name: str
    description: str
    observations_count: int
    first_seen: str
    last_seen: str
    frequency: float  # occurrences per day
    correlation_strength: float  # 0.0 to 1.0
    related_patterns: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class Insight:
    """An actionable insight derived from patterns."""
    insight_id: str
    category: str
    title: str
    description: str
    evidence: list[str]  # pattern_ids that support this insight
    confidence: float  # 0.0 to 1.0
    impact: str  # low, medium, high, critical
    effort: str  # low, medium, high
    created_at: str
    tags: list[str] = field(default_factory=list)


@dataclass
class AgentQuery:
    """A query to another agent."""
    query_id: str
    timestamp: str
    target_agent: str
    question: str
    context: dict
    response: str | None = None
    response_timestamp: str | None = None


@dataclass
class Proposal:
    """An improvement proposal."""
    proposal_id: str
    title: str
    description: str
    category: str
    target: str  # What component/area this affects
    insights: list[str]  # insight_ids that led to this proposal
    rationale: str
    expected_impact: str
    implementation_notes: str
    status: str = "draft"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    decision_notes: str = ""


@dataclass
class RoadmapItem:
    """An item on the Phase X roadmap."""
    item_id: str
    title: str
    description: str
    phase: str  # "phase_x", "phase_y", etc.
    category: str  # neural, ml, graph_theory, etc.
    prerequisites: list[str]  # other item_ids
    proposals: list[str]  # related proposal_ids
    priority: int  # 1 = highest
    status: str  # planned, in_progress, completed, blocked
    notes: str = ""


class AgentInterface(Protocol):
    """Protocol for agents that Cosmic can query."""

    def answer_query(self, question: str, context: dict) -> str:
        """Answer a query from Cosmic."""
        ...


class Cosmic:
    """Cosmic - The Improvement Observer Agent.

    Observes the PatternForge ecosystem, detects patterns,
    and provides insights for continuous improvement.
    """

    def __init__(
        self,
        data_dir: Path | str = "cosmic",
        auto_save: bool = True,
    ):
        """Initialize Cosmic.

        Args:
            data_dir: Directory for persistent storage
            auto_save: Whether to auto-save after observations
        """
        self.data_dir = Path(data_dir)
        self.auto_save = auto_save

        # In-memory state
        self.observations: list[Observation] = []
        self.patterns: dict[str, Pattern] = {}
        self.insights: dict[str, Insight] = {}
        self.queries: list[AgentQuery] = []
        self.proposals: dict[str, Proposal] = {}
        self.roadmap: dict[str, RoadmapItem] = {}

        # Connected agents
        self.agents: dict[str, AgentInterface] = {}

        # Counters for ID generation
        self._observation_count = 0
        self._pattern_count = 0
        self._insight_count = 0
        self._query_count = 0
        self._proposal_count = 0
        self._roadmap_count = 0

        # Load existing state
        self._load_state()

    def _load_state(self) -> None:
        """Load existing state from disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load observations
        obs_file = self.data_dir / "observations.jsonl"
        if obs_file.exists():
            with open(obs_file) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.observations.append(Observation(**data))
            self._observation_count = len(self.observations)

        # Load patterns
        patterns_file = self.data_dir / "patterns.json"
        if patterns_file.exists():
            with open(patterns_file) as f:
                data = json.load(f)
            for pid, pdata in data.items():
                self.patterns[pid] = Pattern(**pdata)
            if self.patterns:
                self._pattern_count = max(int(p.split("_")[1]) for p in self.patterns.keys()) + 1

        # Load insights
        insights_file = self.data_dir / "insights.json"
        if insights_file.exists():
            with open(insights_file) as f:
                data = json.load(f)
            for iid, idata in data.items():
                self.insights[iid] = Insight(**idata)
            if self.insights:
                self._insight_count = max(int(i.split("_")[1]) for i in self.insights.keys()) + 1

        # Load queries
        queries_file = self.data_dir / "questions_log.jsonl"
        if queries_file.exists():
            with open(queries_file) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.queries.append(AgentQuery(**data))
            self._query_count = len(self.queries)

        # Load proposals
        proposals_dir = self.data_dir / "proposals"
        if proposals_dir.exists():
            for pfile in proposals_dir.glob("*.json"):
                with open(pfile) as f:
                    data = json.load(f)
                self.proposals[data["proposal_id"]] = Proposal(**data)
            if self.proposals:
                self._proposal_count = max(int(p.split("_")[1]) for p in self.proposals.keys()) + 1

        # Load roadmap
        roadmap_file = self.data_dir / "roadmap.json"
        if roadmap_file.exists():
            with open(roadmap_file) as f:
                data = json.load(f)
            for rid, rdata in data.items():
                self.roadmap[rid] = RoadmapItem(**rdata)
            if self.roadmap:
                self._roadmap_count = max(int(r.split("_")[1]) for r in self.roadmap.keys()) + 1

    def _save_state(self) -> None:
        """Save current state to disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Save patterns
        patterns_file = self.data_dir / "patterns.json"
        with open(patterns_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.patterns.items()}, f, indent=2)

        # Save insights
        insights_file = self.data_dir / "insights.json"
        with open(insights_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.insights.items()}, f, indent=2)

        # Save roadmap
        roadmap_file = self.data_dir / "roadmap.json"
        with open(roadmap_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.roadmap.items()}, f, indent=2)

    def _append_observation(self, obs: Observation) -> None:
        """Append an observation to the log."""
        self.observations.append(obs)

        if self.auto_save:
            obs_file = self.data_dir / "observations.jsonl"
            with open(obs_file, "a") as f:
                f.write(json.dumps(asdict(obs)) + "\n")

    def _append_query(self, query: AgentQuery) -> None:
        """Append a query to the log."""
        self.queries.append(query)

        if self.auto_save:
            queries_file = self.data_dir / "questions_log.jsonl"
            with open(queries_file, "a") as f:
                f.write(json.dumps(asdict(query)) + "\n")

    # =========================================================================
    # OBSERVATION COLLECTION
    # =========================================================================

    def observe(
        self,
        source: ObservationSource | str,
        event_type: str,
        data: dict,
        context: dict | None = None,
        tags: list[str] | None = None,
    ) -> Observation:
        """Record an observation from any source.

        Args:
            source: Where this observation came from
            event_type: Type of event (e.g., "pipeline_complete", "validation_fail")
            data: Event data
            context: Optional context information
            tags: Optional tags for categorization

        Returns:
            The recorded observation
        """
        if isinstance(source, ObservationSource):
            source = source.value

        obs = Observation(
            timestamp=datetime.now().isoformat(),
            source=source,
            event_type=event_type,
            data=data,
            context=context or {},
            tags=tags or [],
        )

        self._append_observation(obs)
        self._observation_count += 1

        return obs

    def observe_mva(self, validation_result: dict) -> Observation:
        """Convenience method to observe MVA validation results.

        Args:
            validation_result: Result from MVA validation

        Returns:
            The recorded observation
        """
        return self.observe(
            source=ObservationSource.MVA,
            event_type="validation_result",
            data=validation_result,
            tags=["mva", "validation"],
        )

    def observe_pipeline(
        self,
        stage: str,
        duration_ms: float,
        success: bool,
        details: dict | None = None,
    ) -> Observation:
        """Convenience method to observe pipeline events.

        Args:
            stage: Pipeline stage (ingest, analyze, forge, export, attack)
            duration_ms: Stage duration in milliseconds
            success: Whether the stage succeeded
            details: Additional details

        Returns:
            The recorded observation
        """
        return self.observe(
            source=ObservationSource.PIPELINE,
            event_type=f"stage_{stage}",
            data={
                "stage": stage,
                "duration_ms": duration_ms,
                "success": success,
                "details": details or {},
            },
            tags=["pipeline", stage],
        )

    def observe_user(
        self,
        action: str,
        details: dict | None = None,
    ) -> Observation:
        """Convenience method to observe user interactions.

        Args:
            action: User action (e.g., "command", "preference", "feedback")
            details: Action details

        Returns:
            The recorded observation
        """
        return self.observe(
            source=ObservationSource.USER,
            event_type=f"user_{action}",
            data=details or {},
            tags=["user", action],
        )

    # =========================================================================
    # AGENT COMMUNICATION
    # =========================================================================

    def register_agent(self, name: str, agent: AgentInterface) -> None:
        """Register an agent that Cosmic can query.

        Args:
            name: Agent name (e.g., "mva")
            agent: Agent instance implementing AgentInterface
        """
        self.agents[name] = agent

    def query_agent(
        self,
        agent_name: str,
        question: str,
        context: dict | None = None,
    ) -> str | None:
        """Query another agent for information.

        Args:
            agent_name: Name of the agent to query
            question: The question to ask
            context: Optional context for the question

        Returns:
            Agent's response, or None if agent not available
        """
        query_id = f"query_{self._query_count}"
        self._query_count += 1

        query = AgentQuery(
            query_id=query_id,
            timestamp=datetime.now().isoformat(),
            target_agent=agent_name,
            question=question,
            context=context or {},
        )

        # Try to get response
        if agent_name in self.agents:
            try:
                response = self.agents[agent_name].answer_query(question, context or {})
                query.response = response
                query.response_timestamp = datetime.now().isoformat()
            except Exception as e:
                query.response = f"Error: {e}"
                query.response_timestamp = datetime.now().isoformat()
        else:
            query.response = f"Agent '{agent_name}' not registered"
            query.response_timestamp = datetime.now().isoformat()

        self._append_query(query)

        return query.response

    # =========================================================================
    # PATTERN DETECTION
    # =========================================================================

    def analyze_patterns(self, scope: str = "all") -> list[Pattern]:
        """Analyze observations to detect patterns.

        Args:
            scope: Scope of analysis ("all", "recent", "mva", "pipeline", etc.)

        Returns:
            List of detected patterns
        """
        # Filter observations by scope
        if scope == "all":
            obs = self.observations
        elif scope == "recent":
            # Last 100 observations
            obs = self.observations[-100:]
        else:
            obs = [o for o in self.observations if o.source == scope or scope in o.tags]

        if not obs:
            return []

        new_patterns = []

        # Pattern: Repeated event types
        event_counts = defaultdict(list)
        for o in obs:
            event_counts[o.event_type].append(o)

        for event_type, occurrences in event_counts.items():
            if len(occurrences) >= 3:  # Need at least 3 to call it a pattern
                # Check if pattern already exists
                existing = [p for p in self.patterns.values() if p.name == f"recurring_{event_type}"]

                if existing:
                    # Update existing pattern
                    p = existing[0]
                    p.observations_count = len(occurrences)
                    p.last_seen = occurrences[-1].timestamp
                else:
                    # Create new pattern
                    pattern_id = f"pattern_{self._pattern_count}"
                    self._pattern_count += 1

                    # Calculate frequency (per day)
                    if len(occurrences) >= 2:
                        first_ts = datetime.fromisoformat(occurrences[0].timestamp)
                        last_ts = datetime.fromisoformat(occurrences[-1].timestamp)
                        days = max((last_ts - first_ts).total_seconds() / 86400, 0.001)
                        frequency = len(occurrences) / days
                    else:
                        frequency = 0.0

                    p = Pattern(
                        pattern_id=pattern_id,
                        name=f"recurring_{event_type}",
                        description=f"Event type '{event_type}' occurs frequently",
                        observations_count=len(occurrences),
                        first_seen=occurrences[0].timestamp,
                        last_seen=occurrences[-1].timestamp,
                        frequency=frequency,
                        correlation_strength=min(len(occurrences) / 10, 1.0),
                        tags=[event_type],
                    )
                    self.patterns[pattern_id] = p
                    new_patterns.append(p)

        # Pattern: Performance trends
        perf_obs = [o for o in obs if "duration_ms" in o.data]
        if len(perf_obs) >= 5:
            durations = [o.data["duration_ms"] for o in perf_obs]
            avg_duration = statistics.mean(durations)
            std_dev = statistics.stdev(durations) if len(durations) > 1 else 0

            # Check for high variance (inconsistent performance)
            if std_dev > avg_duration * 0.5:
                pattern_id = f"pattern_{self._pattern_count}"
                self._pattern_count += 1

                p = Pattern(
                    pattern_id=pattern_id,
                    name="high_performance_variance",
                    description=f"High variance in operation durations (avg={avg_duration:.1f}ms, std={std_dev:.1f}ms)",
                    observations_count=len(perf_obs),
                    first_seen=perf_obs[0].timestamp,
                    last_seen=perf_obs[-1].timestamp,
                    frequency=len(perf_obs),
                    correlation_strength=min(std_dev / avg_duration, 1.0),
                    tags=["performance", "variance"],
                )
                self.patterns[pattern_id] = p
                new_patterns.append(p)

        # Pattern: Failure clustering
        failure_obs = [o for o in obs if o.data.get("success") is False or o.data.get("result") == "fail"]
        if len(failure_obs) >= 2:
            # Check if failures are clustered in time
            failure_times = [datetime.fromisoformat(o.timestamp) for o in failure_obs]
            if len(failure_times) >= 2:
                time_diffs = [(failure_times[i+1] - failure_times[i]).total_seconds()
                             for i in range(len(failure_times)-1)]
                avg_gap = statistics.mean(time_diffs)

                if avg_gap < 60:  # Failures within 1 minute of each other
                    pattern_id = f"pattern_{self._pattern_count}"
                    self._pattern_count += 1

                    p = Pattern(
                        pattern_id=pattern_id,
                        name="clustered_failures",
                        description=f"Failures tend to cluster (avg gap: {avg_gap:.1f}s)",
                        observations_count=len(failure_obs),
                        first_seen=failure_obs[0].timestamp,
                        last_seen=failure_obs[-1].timestamp,
                        frequency=len(failure_obs),
                        correlation_strength=max(1 - avg_gap/60, 0.5),
                        tags=["failures", "clustering"],
                    )
                    self.patterns[pattern_id] = p
                    new_patterns.append(p)

        if self.auto_save:
            self._save_state()

        return new_patterns

    # =========================================================================
    # INSIGHT GENERATION
    # =========================================================================

    def generate_insights(self) -> list[Insight]:
        """Generate actionable insights from detected patterns.

        Returns:
            List of new insights
        """
        new_insights = []

        for pattern in self.patterns.values():
            # Skip patterns that already have insights
            existing_insights = [i for i in self.insights.values() if pattern.pattern_id in i.evidence]
            if existing_insights:
                continue

            insight = None

            # Insight from high variance pattern
            if pattern.name == "high_performance_variance":
                insight_id = f"insight_{self._insight_count}"
                self._insight_count += 1

                insight = Insight(
                    insight_id=insight_id,
                    category=InsightCategory.PERFORMANCE.value,
                    title="Inconsistent Operation Performance",
                    description="Operations show high variance in duration, suggesting inconsistent behavior that could be optimized.",
                    evidence=[pattern.pattern_id],
                    confidence=pattern.correlation_strength,
                    impact="medium",
                    effort="medium",
                    created_at=datetime.now().isoformat(),
                    tags=["performance", "optimization"],
                )

            # Insight from failure clustering
            elif pattern.name == "clustered_failures":
                insight_id = f"insight_{self._insight_count}"
                self._insight_count += 1

                insight = Insight(
                    insight_id=insight_id,
                    category=InsightCategory.RISK.value,
                    title="Cascading Failure Risk",
                    description="Failures tend to cluster, suggesting potential cascading issues that should be investigated.",
                    evidence=[pattern.pattern_id],
                    confidence=pattern.correlation_strength,
                    impact="high",
                    effort="high",
                    created_at=datetime.now().isoformat(),
                    tags=["reliability", "failures"],
                )

            # Insight from recurring events
            elif pattern.name.startswith("recurring_") and pattern.frequency > 10:
                insight_id = f"insight_{self._insight_count}"
                self._insight_count += 1

                event_type = pattern.name.replace("recurring_", "")
                insight = Insight(
                    insight_id=insight_id,
                    category=InsightCategory.FEATURE.value,
                    title=f"High-Frequency Event: {event_type}",
                    description=f"The event '{event_type}' occurs very frequently ({pattern.frequency:.1f}/day). Consider optimization or caching.",
                    evidence=[pattern.pattern_id],
                    confidence=min(pattern.frequency / 100, 0.9),
                    impact="low",
                    effort="low",
                    created_at=datetime.now().isoformat(),
                    tags=["frequency", "optimization"],
                )

            if insight:
                self.insights[insight.insight_id] = insight
                new_insights.append(insight)

        if self.auto_save:
            self._save_state()

        return new_insights

    # =========================================================================
    # PROPOSALS
    # =========================================================================

    def propose_improvement(
        self,
        title: str,
        description: str,
        category: InsightCategory | str,
        target: str,
        rationale: str,
        expected_impact: str,
        implementation_notes: str = "",
        related_insights: list[str] | None = None,
    ) -> Proposal:
        """Create an improvement proposal.

        Args:
            title: Proposal title
            description: Detailed description
            category: Category (performance, accuracy, usability, etc.)
            target: What component/area this affects
            rationale: Why this improvement is proposed
            expected_impact: Expected impact if implemented
            implementation_notes: Notes for implementation
            related_insights: List of insight_ids that led to this proposal

        Returns:
            The created proposal
        """
        proposal_id = f"proposal_{self._proposal_count}"
        self._proposal_count += 1

        if isinstance(category, InsightCategory):
            category = category.value

        proposal = Proposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            category=category,
            target=target,
            insights=related_insights or [],
            rationale=rationale,
            expected_impact=expected_impact,
            implementation_notes=implementation_notes,
        )

        self.proposals[proposal_id] = proposal

        # Save proposal to disk
        if self.auto_save:
            proposals_dir = self.data_dir / "proposals"
            proposals_dir.mkdir(exist_ok=True)
            with open(proposals_dir / f"{proposal_id}.json", "w") as f:
                json.dump(asdict(proposal), f, indent=2)

        return proposal

    def update_proposal_status(
        self,
        proposal_id: str,
        status: ProposalStatus | str,
        notes: str = "",
    ) -> Proposal | None:
        """Update the status of a proposal.

        Args:
            proposal_id: The proposal to update
            status: New status
            notes: Decision notes

        Returns:
            Updated proposal, or None if not found
        """
        if proposal_id not in self.proposals:
            return None

        proposal = self.proposals[proposal_id]

        if isinstance(status, ProposalStatus):
            status = status.value

        proposal.status = status
        proposal.decision_notes = notes
        proposal.updated_at = datetime.now().isoformat()

        # Save updated proposal
        if self.auto_save:
            proposals_dir = self.data_dir / "proposals"
            proposals_dir.mkdir(exist_ok=True)
            with open(proposals_dir / f"{proposal_id}.json", "w") as f:
                json.dump(asdict(proposal), f, indent=2)

        return proposal

    # =========================================================================
    # ROADMAP
    # =========================================================================

    def add_roadmap_item(
        self,
        title: str,
        description: str,
        phase: str,
        category: str,
        priority: int = 5,
        prerequisites: list[str] | None = None,
        proposals: list[str] | None = None,
    ) -> RoadmapItem:
        """Add an item to the Phase X roadmap.

        Args:
            title: Item title
            description: Detailed description
            phase: Phase identifier (e.g., "phase_x")
            category: Category (neural, ml, graph_theory, etc.)
            priority: Priority (1 = highest)
            prerequisites: List of roadmap item_ids that must complete first
            proposals: Related proposal_ids

        Returns:
            The created roadmap item
        """
        item_id = f"roadmap_{self._roadmap_count}"
        self._roadmap_count += 1

        item = RoadmapItem(
            item_id=item_id,
            title=title,
            description=description,
            phase=phase,
            category=category,
            prerequisites=prerequisites or [],
            proposals=proposals or [],
            priority=priority,
            status="planned",
        )

        self.roadmap[item_id] = item

        if self.auto_save:
            self._save_state()

        return item

    def update_roadmap_status(
        self,
        item_id: str,
        status: str,
        notes: str = "",
    ) -> RoadmapItem | None:
        """Update roadmap item status.

        Args:
            item_id: The roadmap item to update
            status: New status (planned, in_progress, completed, blocked)
            notes: Additional notes

        Returns:
            Updated item, or None if not found
        """
        if item_id not in self.roadmap:
            return None

        item = self.roadmap[item_id]
        item.status = status
        item.notes = notes

        if self.auto_save:
            self._save_state()

        return item

    # =========================================================================
    # REPORTING
    # =========================================================================

    def generate_report(self, report_type: str = "summary") -> str:
        """Generate a report.

        Args:
            report_type: Type of report ("summary", "patterns", "insights", "roadmap", "full")

        Returns:
            Formatted report string
        """
        lines = [
            "=" * 70,
            f"COSMIC REPORT - {report_type.upper()}",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 70,
        ]

        if report_type in ("summary", "full"):
            lines.extend([
                "",
                "OVERVIEW",
                "-" * 40,
                f"  Total observations: {len(self.observations)}",
                f"  Detected patterns: {len(self.patterns)}",
                f"  Generated insights: {len(self.insights)}",
                f"  Active proposals: {len([p for p in self.proposals.values() if p.status in ('draft', 'pending')])}",
                f"  Roadmap items: {len(self.roadmap)}",
                f"  Registered agents: {list(self.agents.keys())}",
            ])

        if report_type in ("patterns", "full"):
            lines.extend([
                "",
                "DETECTED PATTERNS",
                "-" * 40,
            ])
            for p in sorted(self.patterns.values(), key=lambda x: x.correlation_strength, reverse=True)[:10]:
                lines.append(f"  [{p.pattern_id}] {p.name}")
                lines.append(f"      Strength: {p.correlation_strength:.1%}, Occurrences: {p.observations_count}")

        if report_type in ("insights", "full"):
            lines.extend([
                "",
                "ACTIONABLE INSIGHTS",
                "-" * 40,
            ])
            for i in sorted(self.insights.values(), key=lambda x: x.confidence, reverse=True):
                lines.append(f"  [{i.insight_id}] {i.title}")
                lines.append(f"      Category: {i.category}, Impact: {i.impact}, Confidence: {i.confidence:.1%}")

        if report_type in ("roadmap", "full"):
            lines.extend([
                "",
                "PHASE X ROADMAP",
                "-" * 40,
            ])
            for item in sorted(self.roadmap.values(), key=lambda x: x.priority):
                status_icon = {"planned": " ", "in_progress": ">", "completed": "x", "blocked": "!"}
                icon = status_icon.get(item.status, "?")
                lines.append(f"  [{icon}] P{item.priority} - {item.title}")
                lines.append(f"      Phase: {item.phase}, Category: {item.category}")

        if report_type == "full":
            lines.extend([
                "",
                "PENDING PROPOSALS",
                "-" * 40,
            ])
            pending = [p for p in self.proposals.values() if p.status in ("draft", "pending")]
            for p in pending:
                lines.append(f"  [{p.proposal_id}] {p.title}")
                lines.append(f"      Status: {p.status}, Target: {p.target}")

        lines.extend([
            "",
            "=" * 70,
        ])

        return "\n".join(lines)

    def generate_targeted_analysis(self, target: str) -> str:
        """Generate a targeted analysis for a specific area.

        Args:
            target: What to analyze (e.g., "mva", "pipeline", "performance")

        Returns:
            Formatted analysis string
        """
        lines = [
            "=" * 70,
            f"COSMIC TARGETED ANALYSIS: {target.upper()}",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 70,
        ]

        # Filter relevant observations
        relevant_obs = [o for o in self.observations
                       if o.source == target or target in o.tags or target in o.event_type]

        lines.extend([
            "",
            f"OBSERVATIONS ({len(relevant_obs)} relevant)",
            "-" * 40,
        ])

        if relevant_obs:
            # Event type breakdown
            event_counts = defaultdict(int)
            for o in relevant_obs:
                event_counts[o.event_type] += 1

            lines.append("  Event types:")
            for event, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                lines.append(f"    {event}: {count}")

            # Success rate if applicable
            success_obs = [o for o in relevant_obs if "success" in o.data]
            if success_obs:
                success_count = sum(1 for o in success_obs if o.data.get("success"))
                lines.append(f"  Success rate: {success_count}/{len(success_obs)} ({100*success_count/len(success_obs):.1f}%)")

            # Performance stats if applicable
            perf_obs = [o for o in relevant_obs if "duration_ms" in o.data]
            if perf_obs:
                durations = [o.data["duration_ms"] for o in perf_obs]
                lines.append(f"  Performance: avg={statistics.mean(durations):.1f}ms, "
                           f"min={min(durations):.1f}ms, max={max(durations):.1f}ms")

        # Relevant patterns
        relevant_patterns = [p for p in self.patterns.values()
                           if target in p.tags or target in p.name]

        lines.extend([
            "",
            f"PATTERNS ({len(relevant_patterns)} relevant)",
            "-" * 40,
        ])
        for p in relevant_patterns:
            lines.append(f"  {p.name}: {p.description}")

        # Relevant insights
        relevant_insights = [i for i in self.insights.values()
                           if target in i.tags or target in i.title.lower()]

        lines.extend([
            "",
            f"INSIGHTS ({len(relevant_insights)} relevant)",
            "-" * 40,
        ])
        for i in relevant_insights:
            lines.append(f"  [{i.category}] {i.title}")

        lines.extend([
            "",
            "=" * 70,
        ])

        return "\n".join(lines)
