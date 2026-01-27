# Distributed Cracking Research Report

*Research into remote agent deployment for parallel/distributed workloads*

**Date:** 2026-01-25
**Author:** Forge + Vex
**Status:** Research Complete

---

## Executive Summary

Distributed password cracking enables multiple computing nodes to work together on hash recovery tasks, dramatically increasing throughput and reducing time-to-crack. This report explores existing solutions, evaluates benefits and challenges, and proposes a development roadmap for PatternForge distributed capabilities.

**Key Findings:**
- Distributed cracking is a "pleasantly parallel" problem - chunks can be processed independently
- Existing solutions (Hashtopolis, Fitcrack, HashKitty) prove the architecture is mature
- Cloud GPU costs have dropped significantly ($1.49-$2.99/hr for H100s)
- Primary challenges: agent security, chunk coordination, network overhead
- Recommendation: Phase approach starting with Hashtopolis integration, moving to native agents

---

## 1. Existing Solutions Analysis

### 1.1 Hashtopolis

**Architecture:** Client-server with Python agents
**Maturity:** Production-ready, active development (updated Jan 2026)
**License:** Open source

| Strength | Details |
|----------|---------|
| Multi-platform | Linux, Windows, macOS agents |
| Multi-user | Teams, groups, resource sharing |
| Auto-updates | Agents self-update binaries and kernels |
| Chunk management | Automatic keyspace division and assignment |
| Web UI | Full management interface |

**How it works:**
1. Server calculates keyspace for task
2. Agents benchmark their hardware
3. Server assigns chunks based on agent speed
4. Agents report results, request more work
5. Server aggregates results

**Hashtopolis 2.0** (in development) adds:
- Enhanced authorization system
- AgentGroups for resource prioritization
- Cross-team sharing capabilities

> Source: [Hashtopolis Documentation](https://docs.hashtopolis.org/), [GitHub](https://github.com/hashtopolis/server)

### 1.2 Fitcrack

**Architecture:** BOINC-based distributed computing
**Maturity:** Production, research-backed
**License:** Open source

| Strength | Details |
|----------|---------|
| BOINC integration | Leverages proven distributed computing framework |
| 350+ algorithms | Full hashcat algorithm support |
| REST API | Programmatic control |
| Adaptive scheduling | Chunks sized to client performance |

**Chunk distribution formula:**
- Client A (100 passwords/unit) → receives 10 passwords (10×100=1000 work)
- Client B (500 passwords/unit) → receives 50 passwords (50×500=2500 work)

> Source: [Fitcrack GitHub](https://github.com/nesfit/fitcrack), [Research Paper](https://www.sciencedirect.com/science/article/abs/pii/S1742287619301446)

### 1.3 HashKitty

**Architecture:** Custom distributed platform
**Maturity:** Research/emerging
**License:** Open source

| Strength | Details |
|----------|---------|
| SBC support | Works on Single Board Computers (Raspberry Pi, etc.) |
| Heterogeneous | Mixed hardware/OS configurations |
| Scalable | Add/remove nodes dynamically |

> Source: [HashKitty Paper](https://arxiv.org/html/2505.06084v1)

### 1.4 Comparison Matrix

| Feature | Hashtopolis | Fitcrack | HashKitty |
|---------|-------------|----------|-----------|
| Agent deployment | Python client | BOINC client | Custom |
| Auto-updates | Yes | Yes | Partial |
| Multi-user | Yes | Yes | Basic |
| Web UI | Yes | Yes | Yes |
| REST API | Limited | Yes | Yes |
| SBC support | No | No | Yes |
| Cloud integration | Manual | Manual | Manual |
| Active development | High | Medium | Low |

---

## 2. Benefits of Distributed Cracking

### 2.1 Performance Scaling

**Linear Speedup:**
Password cracking is "pleasantly parallel" - work can be divided without inter-node communication.

| Nodes | Theoretical Speedup | Real-world (with overhead) |
|-------|---------------------|---------------------------|
| 1 | 1x | 1x |
| 4 | 4x | 3.5-3.8x |
| 10 | 10x | 8-9x |
| 100 | 100x | 70-85x |

**Example:** A 10-hour single-GPU job becomes ~1 hour with 10 agents.

### 2.2 Cost Efficiency

**Cloud GPU Pricing (2025-2026):**

| Provider | GPU | Price/hr | Notes |
|----------|-----|----------|-------|
| Vast.ai | H100 | $1.49-$1.87 | Marketplace, variable |
| Lambda Labs | H100 | $2.99 | Reserved, reliable |
| RunPod | H100 | $2.39 | Community cloud |
| AWS | H100 | $3-4 | On-demand |

**Cost comparison for 1 trillion hash attempts:**
- Single local RTX 4090: 24+ hours, electricity only
- 10x Vast.ai H100s: ~2 hours @ $20-30 total
- 100x Vast.ai H100s: ~15 minutes @ $25-40 total

> Sources: [Vast.ai Pricing](https://vast.ai/pricing), [Lambda Pricing](https://lambda.ai/pricing), [GPU Cloud Pricing Guide](https://www.hyperbolic.ai/blog/gpu-cloud-pricing)

### 2.3 Hardware Flexibility

- **Heterogeneous nodes:** Mix GPUs, CPUs, old and new hardware
- **Burst capacity:** Spin up cloud nodes for large jobs
- **Idle utilization:** Use lab machines overnight/weekends
- **Geographic distribution:** Agents in multiple locations

### 2.4 Fault Tolerance

- **Chunk reassignment:** If agent dies, work returns to pool
- **Progress persistence:** Completed chunks saved regardless of failures
- **No single point of failure:** Multiple agents provide redundancy

---

## 3. Challenges and Risks

### 3.1 Security Concerns

| Risk | Severity | Mitigation |
|------|----------|------------|
| Hash leakage | HIGH | Agent authentication, encrypted transport |
| Rogue agents | HIGH | One-time registration tokens, audit logs |
| Result tampering | MEDIUM | Result verification, trusted nodes |
| Credential theft | MEDIUM | Minimal agent permissions, no local storage |

**Agent Authentication Pattern:**
```
1. Admin generates one-time token on server
2. Agent presents token on first connection
3. Server validates and registers agent
4. Agent receives persistent credentials
5. All subsequent communication authenticated
```

### 3.2 Network Overhead

| Phase | Data Transfer | Frequency |
|-------|---------------|-----------|
| Task assignment | ~KB | Per chunk |
| Wordlist sync | MB-GB | Per task |
| Rule sync | ~KB | Per task |
| Result reporting | ~KB | Per crack |
| Heartbeat | ~100 bytes | Every 30-60s |

**Optimization strategies:**
- Pre-stage wordlists on agents
- Delta sync for incremental updates
- Compress large transfers
- Batch result reporting

### 3.3 Chunk Distribution Complexity

**Challenges:**
- Keyspace calculation varies by attack type
- Mask attacks harder to divide than dictionary
- Hybrid attacks require careful segmentation
- Prince/combinator modes need special handling

**Solutions:**
- Pre-calculate keyspace before distribution
- Standardize chunk size by time, not keyspace
- Benchmark agents to determine optimal chunk sizes

### 3.4 Operational Complexity

| Challenge | Impact |
|-----------|--------|
| Agent deployment | Need scripts/automation for multiple platforms |
| Version management | Keep all agents on compatible versions |
| Monitoring | Track agent health, progress, errors |
| Debugging | Distributed systems are harder to troubleshoot |

---

## 4. Architecture Options for PatternForge

### Option A: Hashtopolis Integration

**Approach:** PatternForge generates tasks → exports to Hashtopolis → imports results

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  PatternForge   │────▶│   Hashtopolis   │────▶│    Agents       │
│  (Analysis +    │     │   (Server)      │     │  (Distributed)  │
│   Generation)   │◀────│                 │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Pros:**
- Leverage existing, proven infrastructure
- No agent development needed
- Active community and support
- Production-ready today

**Cons:**
- External dependency
- Two systems to manage
- Limited customization
- Separate UIs

**Effort:** Low (weeks)

### Option B: Native PatternForge Agents

**Approach:** Build PatternForge-native distributed system

```
┌─────────────────────────────────────────────────────────────────┐
│                     PatternForge Server                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ SCARAB   │  │ Entropy  │  │  Task    │  │  Agent   │        │
│  │ Analysis │  │  Smith   │  │ Scheduler│  │ Manager  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
            │                           │
            ▼                           ▼
    ┌───────────────┐           ┌───────────────┐
    │ PF Agent      │           │ PF Agent      │
    │ (Linux GPU)   │           │ (Cloud H100)  │
    └───────────────┘           └───────────────┘
```

**Pros:**
- Full control over architecture
- Unified UI/UX
- Custom optimizations for PatternForge workflows
- Educational focus can be built-in

**Cons:**
- Significant development effort
- Need to solve solved problems (chunk distribution, etc.)
- Maintenance burden
- Security responsibility

**Effort:** High (months)

### Option C: Hybrid Approach (Recommended)

**Approach:** Start with Hashtopolis integration, build native features incrementally

```
Phase 1: Hashtopolis export/import
Phase 2: API integration (programmatic control)
Phase 3: Native task distribution (optional agents)
Phase 4: Full native distributed mode
```

**Pros:**
- Immediate value with low effort
- Learn from integration before building
- Gradual migration path
- Fallback always available

**Cons:**
- Longer total timeline
- Temporary duplicate functionality

**Effort:** Medium (phased)

---

## 5. Proposed Development Roadmap

### Phase 1: Hashtopolis Export (v1.2.0)

**Goal:** Export PatternForge artifacts for Hashtopolis consumption

**Deliverables:**
- [ ] `patternforge export --target hashtopolis` command
- [ ] Generate Hashtopolis-compatible task files
- [ ] Wordlist + mask + rules packaging
- [ ] Documentation for Hashtopolis setup

**Effort:** 1-2 weeks

### Phase 2: Hashtopolis API Integration (v1.3.0)

**Goal:** Programmatic control of Hashtopolis from PatternForge

**Deliverables:**
- [ ] Hashtopolis API client library
- [ ] `patternforge attack --distributed` flag
- [ ] Task submission and monitoring
- [ ] Result import and reporting
- [ ] Configuration for Hashtopolis server connection

**Effort:** 2-3 weeks

### Phase 3: Cloud Agent Launcher (v1.4.0)

**Goal:** One-click cloud GPU deployment

**Deliverables:**
- [ ] Vast.ai integration (spawn instances with agent)
- [ ] Lambda Labs integration
- [ ] `patternforge cloud spawn --provider vast --gpus 4`
- [ ] Auto-configure Hashtopolis connection
- [ ] Cost estimation and monitoring
- [ ] Auto-shutdown on task completion

**Effort:** 3-4 weeks

### Phase 4: Native Task Distribution (v2.0.0)

**Goal:** PatternForge-native distributed mode

**Deliverables:**
- [ ] Task scheduler with chunk management
- [ ] Native PatternForge agent (standalone binary)
- [ ] Agent registration and authentication
- [ ] Real-time progress aggregation
- [ ] Fault tolerance and chunk reassignment
- [ ] Web dashboard for monitoring

**Effort:** 2-3 months

### Phase 5: Advanced Features (v2.x)

**Goal:** Enterprise-grade distributed cracking

**Deliverables:**
- [ ] Multi-tenant support
- [ ] Priority queues
- [ ] Resource quotas
- [ ] Audit logging
- [ ] SBC/edge device support
- [ ] Hybrid cloud/on-prem orchestration

**Effort:** Ongoing

---

## 6. Release Candidate Strategy

| Version | Codename | Distributed Feature | Target Date |
|---------|----------|---------------------|-------------|
| v1.1.0 | "The Forge" | None (current release) | Q1 2026 |
| v1.2.0 | "The Anvil" | Hashtopolis export | Q1 2026 |
| v1.3.0 | "The Chain" | Hashtopolis API | Q2 2026 |
| v1.4.0 | "The Cloud" | Cloud agent launcher | Q2 2026 |
| v2.0.0 | "The Legion" | Native distributed | Q3 2026 |
| v2.1.0 | "The Swarm" | Advanced features | Q4 2026 |

### Integration with Existing Roadmap

```
Current:
  v1.1.0 - Binary distribution, play command ✓

Proposed additions:
  v1.2.0 - Hashtopolis export + NeuralSmith foundation
  v1.3.0 - Hashtopolis API + NeuralSmith beta
  v1.4.0 - Cloud launcher + NeuralSmith v1
  v2.0.0 - Native distributed + Major milestone
```

---

## 7. Security Requirements

### Agent Security Checklist

- [ ] TLS/HTTPS for all communication
- [ ] One-time registration tokens
- [ ] Certificate pinning (optional)
- [ ] Audit logging of all agent actions
- [ ] Hash data encrypted at rest on agents
- [ ] Automatic credential rotation
- [ ] Agent permission scoping
- [ ] Network segmentation recommendations

### Threat Model

| Threat | Likelihood | Impact | Mitigation |
|--------|------------|--------|------------|
| Hash exfiltration | Medium | High | Encryption, access controls |
| Malicious agent | Low | High | Authentication, audit |
| Man-in-the-middle | Low | High | TLS, cert pinning |
| Denial of service | Medium | Medium | Rate limiting, quotas |
| Result manipulation | Low | Medium | Result verification |

---

## 8. Cost-Benefit Analysis

### Scenario: Large Hash Recovery Operation

**Target:** 50,000 NTLM hashes
**Dictionary:** 10GB wordlist + rules
**Estimated keyspace:** 100 trillion candidates

| Approach | Hardware | Time | Cost |
|----------|----------|------|------|
| Single RTX 4090 | Local | ~48 hours | Electricity (~$5) |
| Hashtopolis (4 local) | Lab GPUs | ~12 hours | Electricity (~$10) |
| Hashtopolis + Cloud | 4 local + 10 H100 | ~2 hours | ~$30-50 |
| Full cloud (20 H100) | Vast.ai | ~1 hour | ~$40-60 |

**Break-even analysis:**
- If time savings > $20-50/hour value, cloud is justified
- For CTF/training: local is usually sufficient
- For professional engagements: cloud ROI is clear

---

## 9. Educational Considerations

PatternForge is an **educational tool**. Distributed features must maintain this focus:

### Design Principles

1. **Transparency:** Show users what's happening across nodes
2. **Learning:** Explain chunk distribution, not just execute it
3. **Safety:** No features that only make sense for malicious use
4. **Limits:** Encourage reasonable scope, not massive scale

### Suggested UI Elements

```
┌─────────────────────────────────────────────────────────────────┐
│  DISTRIBUTED CRACKING - EDUCATIONAL MODE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Understanding Distributed Cracking:                            │
│  • Your task has been divided into 10 chunks                    │
│  • Each agent works on a different portion of the keyspace      │
│  • This is "pleasantly parallel" - no agent waits for others    │
│                                                                 │
│  Agent Status:                                                  │
│  ├─ Agent-01 (RTX 4090): Chunk 3/10 - 45% complete             │
│  ├─ Agent-02 (H100):     Chunk 7/10 - 72% complete             │
│  └─ Agent-03 (RTX 3080): Chunk 1/10 - 31% complete             │
│                                                                 │
│  Why different speeds? Agents have different GPU capabilities.  │
│  Faster agents will request more chunks after finishing.        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Recommendations

### Immediate (v1.2.0)
1. **Implement Hashtopolis export** - low effort, immediate value
2. **Document Hashtopolis setup** - help users who want distributed now
3. **Add distributed cracking educational content** - teach concepts

### Short-term (v1.3.0-v1.4.0)
1. **API integration** - programmatic control of Hashtopolis
2. **Cloud launcher** - reduce barrier to distributed cracking
3. **Cost calculator** - help users estimate cloud costs

### Long-term (v2.0.0+)
1. **Native agents** - when PatternForge-specific features justify it
2. **Web dashboard** - unified monitoring and control
3. **Enterprise features** - multi-tenant, quotas, audit

### Not Recommended
- Building native agents before proving value with Hashtopolis integration
- Skipping the security requirements
- Ignoring the educational mission

---

## Sources

- [Hashtopolis Documentation](https://docs.hashtopolis.org/)
- [Hashtopolis GitHub](https://github.com/hashtopolis/server)
- [Fitcrack GitHub](https://github.com/nesfit/fitcrack)
- [HashKitty Paper](https://arxiv.org/html/2505.06084v1)
- [Distributed Cracking with BOINC](https://www.sciencedirect.com/science/article/abs/pii/S1742287619301446)
- [Vast.ai Pricing](https://vast.ai/pricing)
- [Lambda Labs Pricing](https://lambda.ai/pricing)
- [GPU Cloud Pricing Guide 2025](https://www.hyperbolic.ai/blog/gpu-cloud-pricing)
- [Cloud Hash Cracking Blog](https://brunoteixeira1996.github.io/posts/2025-06-12-hash-cracking-in-the-cloud/)

---

*Report prepared by the Cipher Circle Research Division*
