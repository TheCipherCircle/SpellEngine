# Scribe Evolution Plan: Knowledge Graph Architect

## Vision

Transform Scribe from a careful file curator into an intelligent knowledge manager that understands Obsidian's graph model and can propose structural improvements to Hashtopia.

## Target Capabilities

### 1. Obsidian Awareness
- Parse YAML frontmatter (metadata, aliases, tags)
- Extract `[[wikilinks]]` and `[[wikilinks|with aliases]]`
- Extract `#tags` and nested `#tags/subtags`
- Understand backlinks (what links TO a page)
- Map the knowledge graph structure

### 2. Hashtopia Deep Scan
- Index all pages with metadata
- Build connection graph (who links to whom)
- Analyze tag taxonomy (frequency, hierarchy, gaps)
- Identify orphan pages (no incoming/outgoing links)
- Detect content clusters and silos
- Map learning paths (sequential content)

### 3. Intelligent Proposals
- **Tag Normalization**: Inconsistent tags → unified taxonomy
- **Missing Links**: Related content that should connect
- **Learning Paths**: Suggested reading order for topics
- **Hash Type Currency**: Flag outdated benchmark data
- **Concept Clustering**: Group related materials

### 4. Benchmark Data Currency
- Track hash type performance claims in Hashtopia
- Compare against PatternForge benchmark observations
- Flag discrepancies for review
- Propose updates with evidence

## Implementation Phases

### Phase 1: Obsidian Parser
Add to Scribe:
- `parse_frontmatter(content)` → dict of metadata
- `extract_wikilinks(content)` → list of linked pages
- `extract_tags(content)` → list of tags
- `ObsidianPage` dataclass with structured representation

### Phase 2: Knowledge Graph Builder
Add to Scribe:
- `deep_scan()` → builds full graph of Hashtopia
- `KnowledgeGraph` class with:
  - pages: dict of ObsidianPage
  - forward_links: page → [linked pages]
  - backlinks: page → [pages that link here]
  - tag_index: tag → [pages with tag]
- `get_orphans()` → pages with no connections
- `get_clusters()` → groups of interconnected pages

### Phase 3: Analysis Engine
Add to Scribe:
- `analyze_tags()` → tag usage report, inconsistencies
- `analyze_connections()` → graph health metrics
- `find_missing_links()` → content that should connect
- `suggest_learning_path(topic)` → ordered reading list

### Phase 4: Structural Proposals
Add to Scribe:
- `propose_retag(old, new)` → batch tag rename proposal
- `propose_taxonomy()` → full tag restructure proposal
- `propose_connections()` → missing wikilink proposals
- `generate_graph_report()` → full analysis document

### Phase 5: Benchmark Integration
Connect Scribe to MVA/Cosmic:
- Subscribe to benchmark observations
- Match against Hashtopia hash type pages
- Auto-generate discrepancy reports
- Propose updates when data changes

## Data Structures

```python
@dataclass
class ObsidianPage:
    path: str
    title: str
    content: str
    frontmatter: dict
    tags: list[str]
    wikilinks: list[str]
    headings: list[tuple[int, str]]  # (level, text)

@dataclass
class KnowledgeGraph:
    pages: dict[str, ObsidianPage]
    forward_links: dict[str, list[str]]
    backlinks: dict[str, list[str]]
    tag_index: dict[str, list[str]]

@dataclass
class TagAnalysis:
    tag: str
    count: int
    pages: list[str]
    similar_tags: list[str]  # potential duplicates
    suggested_parent: str | None  # for hierarchy

@dataclass
class ConnectionProposal:
    source_page: str
    target_page: str
    reason: str
    confidence: float
    evidence: list[str]  # shared tags, similar content, etc.
```

## Success Metrics

1. **Graph Connectivity**: % of pages with ≥2 connections
2. **Tag Consistency**: % of tags following taxonomy
3. **Data Currency**: % of hash type pages with recent benchmarks
4. **Orphan Reduction**: # of isolated pages → 0
5. **Learning Path Coverage**: Key topics have defined paths

## First Task: Hashtopia Deep Dive

Before building, Scribe needs to understand what it's working with:

1. Scan entire Hashtopia-PatternForge vault
2. Build initial knowledge graph
3. Generate analysis report:
   - Total pages, tags, links
   - Tag frequency distribution
   - Most/least connected pages
   - Orphan pages
   - Current tag taxonomy
4. Present findings for review

This informs which features to prioritize.
