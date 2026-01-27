# Hashtopia Tag Audit Report

**Auditor:** Loreth, The Lorekeeper
**Date:** 2026-01-25
**Vault Location:** `/Users/petermckernan/Documents/Hashtopia-PatternForge`

---

## Executive Summary

The Hashtopia Obsidian vault contains **108 markdown files** across 17 directories. The tagging system shows signs of organic growth without a unified taxonomy. Key findings:

- **No #home tag exists** in the vault (contrary to the audit request)
- **44 unique inline tags** are in use
- **9 YAML frontmatter tags** exist in a single file (The Dread Citadel)
- High tag inconsistency with case variations and synonyms
- Many orphan tags used only once
- Core tags (#sudad, #research, #education, #tools) are overused without clear semantic meaning

---

## 1. Current State Summary

### 1.1 Total File Count by Directory

| Directory | File Count |
|-----------|------------|
| 3. Concepts | 21 |
| 3. Processing | 10 |
| 15. Misc | 14 |
| 9. Advanced Methods | 10 |
| 5. Resources | 7 |
| 4. Analysis | 7 |
| 10. Cryptographic Hash Algorithms | 7 |
| 6. Rules | 5 |
| 11. Writeups | 5 |
| 7. Wordlists | 4 |
| 8. Masks | 5 |
| 2. Methodology | 4 |
| Root level | 4 |
| 1. Start Here | 1 |
| 99. Sprints | 1 |
| 100. Tales and Quests | 1 |
| 101. Loreth Notes | 2 |

### 1.2 Tag Frequency (Inline Tags)

| Tag | Count | Assessment |
|-----|-------|------------|
| #research | 27 | Overused - too generic |
| #education | 26 | Overused - too generic |
| #type | 25 | Meaning unclear |
| #tools | 25 | Overused - too generic |
| #sudad | 23 | Internal/author tag - not useful for navigation |
| #wordlists | 21 | Good - topic-specific |
| #hashcat_attacks | 16 | Good - tool-specific |
| #advanced | 14 | Useful - skill level |
| #john_attacks | 10 | Good - tool-specific |
| #howto | 9 | Good - content type |
| #rules | 8 | Good - topic-specific |
| #reference | 8 | Good - content type |
| #awk | 7 | Too specific - CLI tool |
| #sed | 6 | Too specific - CLI tool |
| #training | 5 | Duplicate of #education? |
| #fun | 5 | Good - content type |
| #combinator | 4 | Good - attack type |
| #writeups | 3 | Good - content type |
| #Resources | 3 | Case inconsistent with possible tag intent |
| #methodology | 3 | Good - content type |
| #masks | 3 | Good - topic-specific |
| #hybrid | 3 | Good - attack type |
| #fundamentals | 3 | Useful - skill level |
| #dictionary | 3 | Synonym of #wordlists? |
| #concepts | 3 | Redundant - already in folder name |
| #bruteforce | 3 | Good - attack type |
| #ntlm | 2 | Good - hash type |
| #notes | 2 | Too generic |
| #how_do_i_extract_the_hashes_from_truecrypt_volumes | 2 | Too long/specific |
| #beginner | 2 | Useful - skill level |

### 1.3 Orphan Tags (Used Only Once)

| Tag | File |
|-----|------|
| #x89Lp2 | Password Structure and Composition.md |
| #triage | Utilities.md |
| #testing | Utilities.md |
| #terminal | Utilities.md |
| #Rockyou | Concept Application - HashCat.md |
| #Research | Password Entropy.md (case variant) |
| #performance | Utilities.md |
| #password-research | Utilities.md |
| #password | Rules Analysis.md |
| #hash-id | Utilities.md |
| #graph | Password Pattern Analysis.md |
| #compression | Utilities.md |
| #character-frequency | Utilities.md |
| #analysis | Utilities.md |

### 1.4 YAML Frontmatter Tags

Only **one file** uses YAML frontmatter tags:

**File:** `100.Tales and Quests/The Dread Citadel.md`

Tags:
- quest/campaign
- quest/validated
- difficulty/beginner
- hash/md5
- hash/sha1
- technique/wordlist
- technique/mask
- status/approved
- pthadventures

This file demonstrates excellent hierarchical tag structure that should be adopted vault-wide.

---

## 2. Problems Identified

### 2.1 No Consistent Taxonomy

Tags were added organically without a defined structure. This leads to:
- Overlapping meanings (#education vs #training)
- Unclear semantic intent (#type means what?)
- Case inconsistencies (#Research vs #research, #Resources vs #reference)

### 2.2 #sudad Tag - Personal/Internal

The tag `#sudad` appears 23 times and appears to be a personal identifier or internal marker. It provides no navigational value in the Obsidian graph and adds visual noise.

### 2.3 Overly Generic Tags

The most common tags are too broad to be useful:
- `#research` (27) - Almost everything is research
- `#education` (26) - The entire vault is educational
- `#tools` (25) - Most pages reference tools
- `#type` (25) - Semantically meaningless

### 2.4 Case Inconsistencies

| Variants | Should Be |
|----------|-----------|
| #Research, #research | #research |
| #Resources, #reference | #reference |

### 2.5 Semantic Duplicates

| Duplicates | Recommendation |
|------------|----------------|
| #education, #training | Consolidate to #education |
| #wordlists, #dictionary | Consolidate to #wordlists |
| #methodology, #howto | Keep both - different meaning |

### 2.6 Orphan Tags Creating Graph Noise

14 tags are used only once, creating isolated nodes in the graph view that add clutter without aiding navigation.

### 2.7 No #home Tag Exists

The original audit request mentioned #home overuse, but **no files in the vault contain #home**. This may indicate:
- Previous cleanup already removed it
- Confusion with another vault
- #home was never implemented

---

## 3. Recommended #home Placement

Since #home does not currently exist, here is a recommendation for implementing it correctly:

### 3.1 Pages That SHOULD Have #home (Main Entry Points)

These are index/hub pages that serve as navigation landmarks:

| File | Reason |
|------|--------|
| Home.md | Primary entry point |
| 3. Concepts/1. Concepts.md | Section index |
| 3. Processing/Processing.md | Section index |
| 5. Resources/Resources.md | Section index |
| 6. Rules/Rules.md | Section index |
| 7. Wordlists/Wordlists and Dictionaries.md | Section index |
| 8. Masks/Masks.md | Section index |
| 2. Methodology/1. Foundational Approach to Password & Hash Analysis.md | Key methodology page |
| 1. Start Here/Getting Started with Hashtopia.md | Onboarding page |
| About Hashtopia.md | Background info |

**Total recommended: 10 files**

### 3.2 Pages That Should NOT Have #home

All other 98 files are detail/reference pages and should not have #home, including:
- Individual concept explanations
- Tool-specific guides
- Writeups and case studies
- Reference tables
- Processing target guides

---

## 4. Recommended Tag Taxonomy

### 4.1 Proposed Tag Categories

#### Content Type Tags
| Tag | Purpose | Replaces |
|-----|---------|----------|
| #concept | Theoretical/foundational content | #concepts, #fundamentals, #education |
| #howto | Step-by-step guides | #howto (keep) |
| #reference | Lookup tables, quick reference | #reference (keep) |
| #writeup | Case studies, competition reports | #writeups (keep) |
| #research | Academic/deep analysis | #research (narrow scope) |

#### Topic Tags
| Tag | Purpose |
|-----|---------|
| #wordlists | Wordlist-related content |
| #rules | Rule-based attacks |
| #masks | Mask attacks |
| #hashes | Hash algorithm content |

#### Tool Tags
| Tag | Purpose |
|-----|---------|
| #hashcat | Hashcat-specific content |
| #john | John the Ripper content |
| #pack | PACK tool content |

#### Attack Type Tags
| Tag | Purpose |
|-----|---------|
| #dictionary-attack | Dictionary/wordlist attacks |
| #mask-attack | Mask-based attacks |
| #hybrid-attack | Combined attacks |
| #bruteforce | Brute force attacks |
| #combinator | Combinator attacks |

#### Skill Level Tags
| Tag | Purpose |
|-----|---------|
| #beginner | Entry-level content |
| #intermediate | Mid-level content |
| #advanced | Advanced content |

#### Navigation Tags
| Tag | Purpose |
|-----|---------|
| #home | Main navigation hub pages (limit to ~10) |
| #index | Section index pages |

### 4.2 Tags to Remove Entirely

| Tag | Reason |
|-----|--------|
| #sudad | Personal/internal marker |
| #type | Meaningless |
| #tools | Too generic |
| #education | Too generic (use #concept instead) |
| #training | Duplicate of #education |
| #notes | Too generic |
| #awk | Too CLI-specific |
| #sed | Too CLI-specific |
| #x89Lp2 | Appears to be accidental/test |
| #how_do_i_extract_the_hashes_from_truecrypt_volumes | Use shorter tag |
| All orphan tags in Utilities.md | Consolidate to #reference |

### 4.3 Case Normalization

All tags should be lowercase with hyphens for multi-word tags:
- #Research -> #research
- #Resources -> #reference
- #password-research -> remove (orphan)

---

## 5. Action Items

### Priority 1: Critical Cleanup

1. **Remove #sudad from all files** (23 files affected)
2. **Remove #type from all files** (25 files affected)
3. **Fix case inconsistencies** (#Research -> #research, #Resources -> #reference)

### Priority 2: Tag Consolidation

4. **Merge #education + #training -> #concept** (31 files affected)
5. **Merge #dictionary -> #wordlists** (3 files affected)
6. **Remove overly generic #tools tag** (25 files affected)

### Priority 3: Orphan Cleanup

7. **Remove all orphan tags from Utilities.md** and replace with #reference
8. **Remove #x89Lp2** from Password Structure and Composition.md

### Priority 4: Implement Navigation Tags

9. **Add #home to 10 key navigation pages** (listed in Section 3.1)
10. **Add #index to section index pages**

### Priority 5: Adopt YAML Frontmatter

11. Consider migrating to YAML frontmatter tags vault-wide (as demonstrated in The Dread Citadel.md) for better organization and metadata support

---

## 6. Files Without Any Tags

The following files have **no tags** and may benefit from tagging:

| File |
|------|
| Home.md |
| Welcome.md |
| Task Dashboard.md |
| 1. Start Here/Getting Started with Hashtopia.md |
| 2. Methodology/1. Foundational Approach to Password & Hash Analysis.md |
| 2. Methodology/2. Cracking Methodology.md |
| 3. Concepts/1. Concepts.md |
| 3. Concepts/DRAFT - Concept Application - HashSuite.md |
| 5. Resources/Resources.md |
| 5. Resources/Tools.md |
| 5. Resources/Applications.md |
| 5. Resources/Models.md |
| 5. Resources/Password & Hash Analysis Tool Comparison Matrix.md |
| 7. Wordlists/Custom Dictionary Generation.md |
| 8. Masks/Masks.md |
| 10. Cryptographic Hash Algorithms/Cryptographic Hashing Types.md |
| 10. Cryptographic Hash Algorithms/Whirlpool.md |
| 99. Sprints/Sprint 2.1 - Adventure State Machine.md |
| 101.Loreth Notes/Fun Eggs.md |
| 101.Loreth Notes/Two Covers UI Design.md |

---

## Appendix: Complete Tag-to-File Mapping

### Files by Tag (Most Common Tags)

#### #sudad (23 files)
- About Hashtopia.md
- 3. Concepts/Concept Application - HashCat.md
- 3. Concepts/Concept Application - John the Ripper.md
- 3. Processing/Cloud Services.md
- 3. Processing/DevOps Credentials.md
- 3. Processing/Full Disk Encryption Targets.md
- 3. Processing/NetNTLM v1 v2 Hash Leaks.md
- 3. Processing/Network Hashes.md
- 3. Processing/PCAP - Wireless Passwords.md
- 3. Processing/Windows Domain Password Hashes.md
- 3. Processing/Windows Local Password Hashes.md
- 4. Analysis/PACK - Extended User Guide Addendum.md
- 4. Analysis/PACK - Password Analysis and Cracking Kit.md
- 6. Rules/Rule Selection & Attack Strategy Guide.md
- 7. Wordlists/Wordlist Engineering & Manipulation.md
- 8. Masks/Top Masks.md
- 9. Advanced Methods/Advanced Compositional Attacks.md
- 9. Advanced Methods/Distributed and Parallel Attack Architecture.md
- 9. Advanced Methods/Keyboard Walk Processor.md
- 11. Writeups/Collection_1 - Anti-Public Dump - Stats and Analysys.md
- 11. Writeups/Password Cracking Machine Recipe.md

#### #research (27 files)
- 3. Concepts/Cryptographic Hashing.md
- 3. Concepts/Entropy and Guessability.md
- 3. Concepts/Markov-Chains.md
- 3. Concepts/Memorability vs Security.md
- 3. Concepts/Password Aging and Drift.md
- 3. Concepts/Password Complexity vs. Password Entropy.md
- 3. Concepts/Password Cracking System Architecture.md
- 3. Concepts/Password Lifecycles & Transformation Patterns.md
- 3. Concepts/Password Reuse.md
- 3. Concepts/Password Structure and Composition.md
- 3. Concepts/Probabalistic Context Free Grammer (PCFG).md
- 3. Concepts/Salts and Key Stretching.md
- 3. Concepts/Scale and Risk Amplification.md
- 3. Concepts/Why Complexity Rules Fail.md
- 3. Processing/Windows Domain Password Hashes.md
- 4. Analysis/Password Analysis Findings.md
- 4. Analysis/Password Population Findings - Interpretation & Impact Assessment.md
- 4. Analysis/Structural Analysis of Password Composition and Human Pattern Formation.md
- 9. Advanced Methods/Extreme Hashes.md
- 10. Cryptographic Hash Algorithms/Bcrypt.md
- 10. Cryptographic Hash Algorithms/Blowfish cipher.md
- 10. Cryptographic Hash Algorithms/Cryptographic Hash Algorithms.md
- 10. Cryptographic Hash Algorithms/MD5.md
- 10. Cryptographic Hash Algorithms/SHA-1.md
- 2. Methodology/3. General Methodology.md
- 2. Methodology/4. General Checklist.md
- 15. Misc/Example Hashes.md

---

*Report generated by Loreth, The Lorekeeper*
*This audit is read-only - no vault files were modified*
