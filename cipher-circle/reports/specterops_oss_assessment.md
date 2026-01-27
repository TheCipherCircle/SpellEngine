# SpecterOps Open Source Projects Assessment
## PTHAdventures Campaign Development Candidates

**Prepared by:** Loreth, The Lorekeeper
**Date:** January 25, 2026
**Purpose:** Identify SpecterOps OSS tools suitable for educational adventure campaigns

---

## Executive Summary

SpecterOps maintains an impressive portfolio of 38+ open-source security tools, with several prime candidates for PTHAdventures educational campaigns. Their tools span Active Directory attack path analysis, Kerberos exploitation, credential extraction, and offensive data processing.

**Top Candidates for Adventure Campaigns:**
1. **BloodHound** - Ideal for "Attack Path Navigator" campaign (visual, graph-based learning)
2. **Rubeus** - Perfect for "Kerberos Quest" campaign (direct hashcat integration)
3. **Certify** - Excellent for "Certificate Chaos" campaign (AD CS misconfigurations)
4. **Seatbelt** - Great for "Enumeration Explorer" introductory campaign

**Key Integration Opportunity:** Rubeus outputs hashes in hashcat-compatible formats (mode 13100 for Kerberoasting, mode 18200 for AS-REP Roasting), creating a natural bridge to PatternForge password analysis workflows.

---

## Tool-by-Tool Assessment

### 1. BloodHound

**What It Does:**
BloodHound uses graph theory to reveal hidden and unintended relationships within Active Directory and Entra ID environments. It visualizes attack paths from any compromised user to high-value targets like Domain Admin.

**Latest Version:** BloodHound v8.0 (July 2025) introduced OpenGraph for cross-platform attack path analysis beyond AD/Entra ID.

| Criteria | Assessment |
|----------|------------|
| **Learning Value** | Graph theory, AD relationships, privilege escalation paths, trust exploitation |
| **Difficulty** | Intermediate - requires AD fundamentals knowledge |
| **Adventure Fit** | EXCELLENT - Visual nature perfect for gamification |
| **Integration** | Indirect - identifies targets for password attacks |
| **Legal/Ethical** | Safe with lab environments; endorsed by DHS |

**Skills Taught:**
- Understanding AD object relationships (users, groups, computers, GPOs)
- Identifying attack paths through ACL misconfigurations
- Analyzing trust relationships between domains
- Strategic thinking about lateral movement

**Adventure Potential:**
*"The Attack Path Navigator"* - Players use BloodHound to chart a course through a deliberately misconfigured AD environment, discovering the shortest path to domain dominance. Each discovered path reveals lore about historical AD compromise techniques.

**Sources:**
- [BloodHound Community Edition](https://specterops.io/bloodhound-community-edition/)
- [BloodHound Introduction](https://bloodhound.specterops.io/get-started/introduction)
- [HTB Academy BloodHound Course](https://academy.hackthebox.com/course/preview/active-directory-bloodhound)

---

### 2. SharpHound

**What It Does:**
C# data collector for BloodHound. Uses native Windows API calls and LDAP namespace functions to enumerate AD objects, relationships, ACLs, group memberships, sessions, and more.

**Relationship to BloodHound:**
SharpHound collects the raw data that BloodHound visualizes. Without SharpHound (or alternative collectors like BloodHound.py or RustHound), BloodHound has nothing to analyze.

| Criteria | Assessment |
|----------|------------|
| **Learning Value** | AD enumeration, LDAP queries, Windows API, OPSEC |
| **Difficulty** | Beginner-Intermediate |
| **Adventure Fit** | GOOD - Paired with BloodHound campaign |
| **Integration** | Indirect - data collection phase |
| **Legal/Ethical** | Safe in authorized environments |

**Skills Taught:**
- AD enumeration techniques
- Understanding what data reveals attack paths
- Operational security (stealth modes, query volumes)
- Detection evasion concepts

**Adventure Potential:**
*"The Silent Collector"* - A stealth-focused mini-campaign where players must gather AD intelligence without triggering detection thresholds. Teaches defensive awareness alongside offensive technique.

**Sources:**
- [SharpHound GitHub](https://github.com/SpecterOps/SharpHound)
- [SharpHound Data Collection Permissions](https://bloodhound.specterops.io/collect-data/permissions)
- [SharpHound Detection - Purple Team](https://ipurple.team/2024/07/15/sharphound-detection/)

---

### 3. GhostPack Suite

GhostPack is a collection of C# security tools. Below are the most relevant for PTHAdventures:

#### 3a. Rubeus (Kerberos Toolkit)

**What It Does:**
Rubeus is a comprehensive Kerberos attack tool that can perform Kerberoasting, AS-REP Roasting, ticket manipulation, and more. Derived from Mimikatz and generates raw Kerberos data over UDP port 88.

| Criteria | Assessment |
|----------|------------|
| **Learning Value** | Kerberos protocol, ticket attacks, encryption types, hash extraction |
| **Difficulty** | Intermediate-Advanced |
| **Adventure Fit** | EXCELLENT - Direct password cracking tie-in |
| **Integration** | DIRECT - Outputs hashcat-compatible formats |
| **Legal/Ethical** | Educational use in labs; real attacks require authorization |

**Hashcat Integration:**
- Kerberoasting (TGS): Mode 13100 (RC4), 19600 (AES128), 19700 (AES256)
- AS-REP Roasting: Mode 18200
- Output format flag: `/format:hashcat`

**Skills Taught:**
- Kerberos authentication fundamentals
- Service Principal Names (SPNs)
- Ticket encryption and cracking
- Password policy weaknesses

**Adventure Potential:**
*"Kerberos Quest: Taming the Three-Headed Dog"* - Multi-chapter campaign teaching Kerberos from fundamentals to exploitation. Players progress from understanding tickets to extracting and cracking them with PatternForge-generated wordlists.

**PatternForge Integration:**
```
Rubeus extracts Kerberos tickets (krb5tgs hashes)
    -> PatternForge analyzes cracked passwords
    -> EntropySmith generates targeted candidates
    -> Hashcat cracks remaining tickets faster
```

**Sources:**
- [Rubeus GitHub](https://github.com/GhostPack/Rubeus)
- [Rubeus Kerberoast Documentation](https://docs.specterops.io/ghostpack/rubeus/roasting)
- [Detailed Guide on Rubeus](https://www.hackingarticles.in/a-detailed-guide-on-rubeus/)

---

#### 3b. Seatbelt (Host Enumeration)

**What It Does:**
Performs security-oriented host-survey "safety checks" relevant from both offensive and defensive perspectives. Comprehensive enumeration of system, user, and security configurations.

| Criteria | Assessment |
|----------|------------|
| **Learning Value** | Windows internals, security configurations, enumeration methodology |
| **Difficulty** | Beginner |
| **Adventure Fit** | GOOD - Entry-level campaign material |
| **Integration** | Indirect - identifies credential storage locations |
| **Legal/Ethical** | Defensive value; safe for education |

**Skills Taught:**
- Windows security configuration review
- Identifying misconfigurations
- Systematic enumeration methodology
- Understanding what attackers look for

**Adventure Potential:**
*"The Safety Inspector"* - Introductory campaign where players learn host enumeration by running Seatbelt checks and understanding what each finding means for security. Dual offensive/defensive perspective.

**Sources:**
- [Seatbelt GitHub](https://github.com/GhostPack/Seatbelt)
- [Seatbelt Overview](https://docs.specterops.io/ghostpack-docs/Seatbelt-mdx/overview)

---

#### 3c. Certify (AD CS Attacks)

**What It Does:**
Enumerates and abuses misconfigurations in Active Directory Certificate Services (AD CS). Released at Black Hat 2021 with the "Certified Pre-Owned" research.

| Criteria | Assessment |
|----------|------------|
| **Learning Value** | PKI, certificate authentication, AD CS misconfigurations |
| **Difficulty** | Advanced |
| **Adventure Fit** | EXCELLENT - Unique topic, high engagement |
| **Integration** | Indirect - alternative authentication bypass |
| **Legal/Ethical** | Educational; requires lab environment |

**ESC Attack Coverage:**
- ESC1: Misconfigured certificate templates allowing SAN specification
- ESC7: ManageCA permission abuse
- Multiple other escalation techniques

**Skills Taught:**
- Public Key Infrastructure (PKI) fundamentals
- Certificate-based authentication
- AD CS template security
- Golden certificate attacks

**Adventure Potential:**
*"Certificate Chaos: The ESC Chronicles"* - Progressive campaign through ESC1-ESC8 vulnerabilities. Each chapter explores a different misconfiguration, building expertise in AD CS security.

**Sources:**
- [Certify GitHub](https://github.com/GhostPack/Certify)
- [Certify Wiki - Escalation Techniques](https://github.com/GhostPack/Certify/wiki/4-%E2%80%90-Escalation-Techniques)
- [Black Hills - Abusing AD CS](https://www.blackhillsinfosec.com/abusing-active-directory-certificate-services-part-one/)

---

#### 3d. SharpDPAPI (DPAPI Attacks)

**What It Does:**
C# port of Mimikatz DPAPI functionality for extracting DPAPI-protected credentials.

| Criteria | Assessment |
|----------|------------|
| **Learning Value** | Windows credential protection, DPAPI, master keys |
| **Difficulty** | Advanced |
| **Adventure Fit** | MODERATE - Niche but valuable |
| **Integration** | Potential - extracts encrypted credentials |
| **Legal/Ethical** | Credential extraction requires authorization |

---

### 4. Nemesis

**What It Does:**
Centralized data processing platform that ingests, enriches, and allows collaborative analysis of files collected during offensive security assessments. Functions as an "offensive VirusTotal."

**Latest Version:** Nemesis 2.0 (August 2025) - Complete rewrite with simplified Docker Compose architecture.

| Criteria | Assessment |
|----------|------------|
| **Learning Value** | File analysis, credential discovery, automation, data pipelines |
| **Difficulty** | Intermediate-Advanced (setup), Beginner (usage) |
| **Adventure Fit** | MODERATE - More infrastructure than technique |
| **Integration** | STRONG - Automated credential discovery |
| **Legal/Ethical** | Post-exploitation tool; educational value |

**Key Features:**
- 28+ file enrichment modules
- C2 platform integration (Cobalt Strike, Mythic, Sliver)
- Automated secret scanning
- DPAPI blob discovery
- Collaborative file triage

**Adventure Potential:**
*"The Data Forge"* - Infrastructure-focused campaign teaching offensive data processing. Players learn to set up and use Nemesis to process engagement data, discovering hidden credentials and secrets.

**Sources:**
- [Nemesis GitHub](https://github.com/SpecterOps/Nemesis)
- [Nemesis 2.0 Blog Post](https://specterops.io/blog/2025/08/05/nemesis-2-0/)
- [Nemesis Help Net Security](https://www.helpnetsecurity.com/2023/12/12/nemesis-specterops-data-enrichment-analytic-pipeline/)

---

### 5. Ghostwriter

**What It Does:**
Open-source platform for offensive security operations - report writing, asset tracking, and assessment management.

| Criteria | Assessment |
|----------|------------|
| **Learning Value** | Professional practice, reporting, operation management |
| **Difficulty** | Beginner (concept), Intermediate (setup) |
| **Adventure Fit** | LOW - Administrative rather than technical |
| **Integration** | Minimal |
| **Legal/Ethical** | Purely defensive/administrative |

**Assessment:** Not suitable for adventure campaigns but valuable for teaching professional practices in a separate training track.

**Sources:**
- [Ghostwriter GitHub](https://github.com/GhostManager/Ghostwriter)
- [Ghostwriter - SpecterOps](https://specterops.io/open-source-tools/ghostwriter/)

---

## Recommended Adventure Candidates

### Tier 1: Primary Campaign Material

| Tool | Campaign Name | Priority | PatternForge Synergy |
|------|--------------|----------|----------------------|
| **Rubeus** | Kerberos Quest | HIGH | Direct hashcat integration |
| **BloodHound** | Attack Path Navigator | HIGH | Target identification |
| **Certify** | Certificate Chaos | HIGH | Alternative auth vector |

### Tier 2: Supporting Campaigns

| Tool | Campaign Name | Priority | PatternForge Synergy |
|------|--------------|----------|----------------------|
| **Seatbelt** | The Safety Inspector | MEDIUM | Credential location discovery |
| **SharpHound** | The Silent Collector | MEDIUM | BloodHound prerequisite |
| **Nemesis** | The Data Forge | MEDIUM | Credential extraction pipeline |

### Tier 3: Reference Material

| Tool | Usage | Notes |
|------|-------|-------|
| SharpDPAPI | Supporting technique | DPAPI credential extraction |
| SafetyKatz | Supporting technique | Mimikatz functionality |
| ForgeCert | Advanced topic | Golden certificate attacks |

---

## Proposed Campaign Concepts

### Campaign 1: "Kerberos Quest: Taming the Three-Headed Dog"
**Tools:** Rubeus, hashcat, PatternForge
**Chapters:**
1. *The Realm of Kerberos* - Authentication fundamentals
2. *Service Principal Scrolls* - Understanding SPNs
3. *The Roasting Ritual* - Kerberoasting with Rubeus
4. *The Cracking Crucible* - Hash cracking with hashcat
5. *The Pattern Revelation* - Analyzing cracked passwords with PatternForge
6. *The Forge Strikes Back* - Generating targeted candidates with EntropySmith
7. *AS-REP's Revenge* - AS-REP Roasting techniques
8. *The Golden Ticket* - Pass-the-Ticket finale

**PatternForge Integration Points:**
- Chapter 5: Import cracked passwords into corpus
- Chapter 6: Generate attack-specific wordlists
- Bonus: Cross-campaign password pattern analysis

---

### Campaign 2: "The Attack Path Navigator"
**Tools:** BloodHound, SharpHound
**Chapters:**
1. *Mapping the Kingdom* - AD structure fundamentals
2. *The Collector's Art* - SharpHound data gathering
3. *Graph Theory Grimoire* - Understanding node relationships
4. *Path of Least Resistance* - Finding attack paths
5. *The Choke Point Chronicles* - Defensive remediation
6. *Trust No Domain* - Trust relationship exploitation
7. *OpenGraph Odyssey* - Beyond AD/Entra with v8.0

---

### Campaign 3: "Certificate Chaos: The ESC Chronicles"
**Tools:** Certify, Certipy
**Chapters:**
1. *PKI Foundations* - Certificate basics
2. *The Template Tome* - AD CS template security
3. *ESC1: The SAN Scandal* - Subject Alternative Name abuse
4. *ESC2-ESC4: Escalation Trilogy* - Template misconfigurations
5. *ESC7: The ManageCA Menace* - Permission abuse
6. *The Golden Certificate* - ForgeCert and persistence
7. *Defense of the Realm* - Securing AD CS

---

## Integration Opportunities with PatternForge

### Direct Integration

```
+-------------------+     +-----------------+     +------------------+
|     Rubeus        |     |   PatternForge  |     |     hashcat      |
|  (Kerberoasting)  | --> |  (SCARAB/Smith) | --> | (Targeted Attack)|
+-------------------+     +-----------------+     +------------------+
        |                         |                        |
        v                         v                        v
   krb5tgs hashes         Pattern analysis          Cracked passwords
   /format:hashcat        Candidate generation      (feed back to PF)
```

### Workflow Example

1. **Rubeus** extracts Kerberoastable service account hashes
2. **hashcat** cracks initial batch with standard wordlists
3. **PatternForge/SCARAB** analyzes cracked passwords for patterns
4. **EntropySmith** generates targeted candidates based on discovered patterns
5. **hashcat** runs second pass with EntropySmith output
6. Repeat cycle with new discoveries

### Proposed PatternForge Features for Integration

| Feature | Description | Adventure Value |
|---------|-------------|-----------------|
| `patternforge import --format krb5tgs` | Import Kerberos ticket format | Kerberos Quest Ch. 5 |
| `patternforge analyze --context ad-service` | AD service account patterns | Targeted generation |
| `patternforge forge --target kerberos` | Kerberos-optimized candidates | Higher crack rates |

---

## Legal and Ethical Considerations

### Safe Educational Use

All SpecterOps tools are designed for authorized security testing. For PTHAdventures:

1. **Lab Environments Required** - All hands-on exercises must use isolated lab environments
2. **No Production Data** - Never use real organizational data
3. **Authorization Emphasis** - Each campaign should reinforce the importance of proper authorization
4. **Defensive Perspective** - Include "blue team" chapters showing detection/prevention

### Recommended Lab Platforms

- **Hack The Box Academy** - Offers BloodHound-specific courses
- **TryHackMe** - AD attack path rooms
- **DVAD (Damn Vulnerable AD)** - Free vulnerable AD lab
- **Detection Lab** - Chris Long's defensive lab environment

### Licensing

| Tool | License | Commercial Use |
|------|---------|----------------|
| BloodHound CE | Apache 2.0 | Permitted |
| Rubeus | BSD 3-Clause | Permitted |
| Seatbelt | BSD 3-Clause | Permitted |
| Certify | BSD 3-Clause | Permitted |
| Nemesis | BSD 3-Clause | Permitted |

---

## Conclusion

SpecterOps maintains an exceptional portfolio of open-source security tools with significant educational potential. **Rubeus** stands out as the highest-priority candidate due to its direct hashcat integration and natural fit with PatternForge password analysis workflows.

The proposed "Kerberos Quest" campaign offers the strongest synergy with PatternForge's mission of password pattern analysis, creating a complete learning journey from Kerberos fundamentals through hash extraction to intelligent candidate generation.

**Recommended Next Steps:**
1. Prototype "Kerberos Quest" Chapter 1-2 with PatternForge integration points
2. Establish lab environment with Kerberoastable service accounts
3. Create sample hash corpus for PatternForge analysis demonstrations
4. Develop "BloodHound Navigator" as parallel campaign track

---

## References

### Primary Sources
- [SpecterOps Open Source Tools](https://specterops.io/our-commitment-to-open-source/)
- [SpecterOps GitHub Organization](https://github.com/specterops)
- [GhostPack GitHub Organization](https://github.com/GhostPack)
- [SpecterOps Documentation Library](https://docs.specterops.io/)

### BloodHound Resources
- [BloodHound Community Edition](https://specterops.io/bloodhound-community-edition/)
- [BloodHound v8.0 Release](https://specterops.io/blog/2025/07/29/bloodhound-community-edition-v8-launches-with-opengraph-identity-attack-paths-beyond-active-directory-entra-id/)
- [SANS BloodHound Cheat Sheet](https://www.sans.org/posters/bloodhound-cheat-sheet/)

### GhostPack Documentation
- [Rubeus Introduction](https://docs.specterops.io/ghostpack/rubeus/introduction)
- [Rubeus Roasting Commands](https://docs.specterops.io/ghostpack/rubeus/roasting)
- [Seatbelt Overview](https://docs.specterops.io/ghostpack-docs/Seatbelt-mdx/overview)
- [Certify Wiki](https://github.com/GhostPack/Certify/wiki)

### Training Resources
- [HTB Academy - Active Directory BloodHound](https://academy.hackthebox.com/course/preview/active-directory-bloodhound)
- [Pluralsight - Discovery with BloodHound](https://www.pluralsight.com/courses/discovery-bloodhound)
- [Red Team Notes - BloodHound with Kali](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/abusing-active-directory-with-bloodhound-on-kali-linux)

### Hash Cracking References
- [The Hacker Recipes - Kerberoast](https://www.thehacker.recipes/ad/movement/kerberos/kerberoast)
- [Hashcat Cheatsheet](https://github.com/frizb/Hashcat-Cheatsheet/blob/master/README.md)
- [AS-REP Roasting with Rubeus and Hashcat](https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/as-rep-roasting-using-rubeus-and-hashcat)
