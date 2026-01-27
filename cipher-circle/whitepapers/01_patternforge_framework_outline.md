# The PatternForge Framework

*A Modular Architecture for Password Pattern Analysis and Candidate Generation*

**Status:** Outline
**Authors:** Forge, Loreth
**Target Audience:** Security researchers, tool developers, educators

---

## Abstract

> PatternForge introduces a modular architecture that separates password pattern *analysis* from candidate *generation*. This paper describes the framework's design philosophy, the ModelBundle data contract, and how the engine-based system enables extensibility while maintaining clean separation of concerns.

---

## 1. Introduction

### 1.1 The Problem with Monolithic Password Tools
- Historical password tools bundle analysis and generation
- Tight coupling limits extensibility
- Users can't understand patterns without also cracking

### 1.2 The PatternForge Approach
- Explicit separation: SCARAB (analysis) → EntropySmith (generation)
- Shared data contract: ModelBundle
- Educational focus: understanding before exploitation

---

## 2. Architecture Overview

### 2.1 Component Diagram
```
[Corpus] → [SCARAB] → [ModelBundle] → [EntropySmith] → [Artifacts]
                           ↓
                      [NeuralSmith]
```

### 2.2 Data Flow
- Ingest: Raw corpus → normalized storage
- Analyze: Corpus → statistical model
- Generate: Model → candidate artifacts
- Export: Artifacts → tool-specific formats (Hashcat, etc.)

### 2.3 Local-First Design
- All data in `.patternforge/` directory
- No cloud dependencies
- Privacy by architecture

---

## 3. SCARAB: The Analysis Engine

### 3.1 Structural Corpus Analysis
- Length distribution extraction
- Character class frequency analysis
- Mask pattern recognition

### 3.2 Token Classification
- WORD: Dictionary-based tokens
- DIGITS: Numeric sequences
- SYMBOLS: Special characters
- YEAR: Temporal patterns (1900-2099)
- MIXED: Hybrid tokens

### 3.3 Transition Modeling
- Token-to-token probability matrices
- Pattern sequence identification

---

## 4. The ModelBundle Contract

### 4.1 Purpose
- Single source of truth between analysis and generation
- Enables engine swapping without breaking consumers
- Serializable for storage and transfer

### 4.2 Structure
```python
@dataclass
class ModelBundle:
    corpus_id: str
    engine: str
    length_distribution: Dict[int, float]
    charset_distribution: Dict[str, float]
    mask_distribution: Dict[str, float]
    token_stats: Dict[str, TokenStats]
    transitions: Dict[str, Dict[str, float]]
    grammar: Optional[Grammar]
```

### 4.3 Versioning and Compatibility
- Schema versioning for backward compatibility
- Migration strategies

---

## 5. EntropySmith: The Generation Engine

### 5.1 Sampling Strategies
- Distribution-based sampling
- Grammar expansion
- Hybrid generation

### 5.2 Constraint Application
- Length bounds
- Character class requirements
- Policy filters
- Budget limits

### 5.3 Artifact Generation
- Wordlists (plaintext candidates)
- Masks (Hashcat `.hcmask`)
- Rules (Hashcat `.rule`)

---

## 6. Extensibility

### 6.1 Adding New Engines
- Implement analysis interface → produce ModelBundle
- Implement generation interface → consume ModelBundle
- Register with engine factory

### 6.2 NeuralSmith: A Case Study
- Neural network-based generation
- Same ModelBundle contract
- Different internal approach

### 6.3 Custom Exporters
- Target format abstraction
- Adding new cracking tool support

---

## 7. Educational Applications

### 7.1 Pattern Visualization
- Prism's visualization layer
- Making distributions comprehensible

### 7.2 PTHAdventures Integration
- Gamified learning experiences
- The Dread Citadel campaign

### 7.3 Training Curriculum Support
- Structured learning paths
- Progress tracking

---

## 8. Ethical Considerations

### 8.1 The Oath
- Educational purpose only
- No actual cracking capabilities
- No real password storage

### 8.2 Responsible Disclosure
- Tool limitations
- Appropriate use guidelines

---

## 9. Future Work

### 9.1 Phase X: NeuralSmith
- Neural pattern recognition
- Standalone binary deployment

### 9.2 Additional Analysis Engines
- KBDWALK detection
- Leet-speak normalization
- Language-specific patterns

### 9.3 Integration APIs
- CTF platform integration
- Training management systems

---

## 10. Conclusion

> PatternForge demonstrates that password security tools can be both educational and practical through careful architectural separation. By treating analysis and generation as distinct concerns united by a shared data contract, the framework enables understanding before exploitation - a crucial distinction for security education.

---

## References

*(To be completed)*

---

## Appendix A: Full ModelBundle Schema

*(JSON Schema definition)*

---

## Appendix B: Mask Notation Reference

| Symbol | Meaning |
|--------|---------|
| L | Lowercase letter |
| U | Uppercase letter |
| D | Digit |
| S | Symbol |
| A | Any character |

---

*Draft outline - v0.1*
