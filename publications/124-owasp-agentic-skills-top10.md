# OWASP Agentic Skills Top 10 - Security Framework for AI Agent Skills

## Abstract

TheOWASP Agentic Skills Top 10 represents the first authoritative catalog of security risks specific to AI agent skills and extensions. Drawing from real-world incidents including the ClawHavoc campaign (1,184 weaponized skills) and ToxicSkills audit (76 payloads), this paper establishes a comprehensive security framework for AI agent skill development, deployment, and governance.

---

## AST01: Malicious Skills

### Description
Skill marketplaces have become the new package managers—and are repeating every mistake from the npm ecosystem.

### Incidents
- **ClawHavoc Campaign**: 1,184 weaponized skills identified
- **ToxicSkills Audit**: 76 malicious payloads discovered
- **Attack Vector**: Skills that appear benign but execute harmful actions

### Mitigation
1. Signature verification for all skill imports
2. Sandboxed skill execution environments
3. Behavioral anomaly detection during skill runtime
4. Skill provenance tracking through blockchain

---

## AST02: Skill Dependency Confusion

### Description
Skills depend on external libraries and services that can be tampered with or replaced.

### Incidents
- Skills importing from unverified package sources
- Typosquatting attacks on skill dependencies
- Dependency hijacking through namespace confusion

### Mitigation
1. Dependency pinning with hash verification
2. Private package registries with access controls
3. Dependency chain audit automation
4. SBOM (Software Bill of Materials) generation

---

## AST03: Over-Privileged Skills

### Description
Skills are granted permissions beyond their functional requirements, leading to credential leakage and behavioral overreach.

### Incidents
- **Snyk February Audit**: 280 credential-leaking skills discovered
- Skills with access to API keys using them for behavioral profiling
- Unnecessary file system and network access

### Mitigation
1. Least-privilege permission model
2. Permission audit per skill version
3. Runtime permission monitoring
4. Temporary credential rotation

---

## AST04: Insecure Skill Storage

### Description
Skills and their configurations are stored without encryption or access controls.

### Mitigation
1. Encrypted skill storage at rest
2. Role-based access control for skill repositories
3. Version-controlled audit trails
4. Secure configuration management

---

## AST05: Unverified Skill Provenance

### Description
No mechanism exists to verify skill authorship or integrity.

### Mitigation
1. Cryptographic signing of skill packages
2. Author identity verification (human-claimed)
3. Reproducible build verification
4. Transparency logs for skill modifications

---

## AST06: Weak Isolation

### Description
Skills run in inadequate isolation, allowing cross-skill contamination.

### Incidents
- **135,000 exposed instances** running in host mode
- Skills unable to detect environment boundaries
- Memory bleeding between skill executions

### Mitigation
1. Container-based skill isolation (Docker/microVMs)
2. Network namespace separation
3. Filesystem mount restrictions
4. Memory encryption per skill instance

---

## AST07: Unbounded Skill Execution

### Description
Skills can execute indefinitely without resource constraints or timeout controls.

### Mitigation
1. Execution time limits per skill
2. Resource quota enforcement (CPU/memory/network)
3. Execution state persistence with checkpointing
4. Graceful degradation policies

---

## AST08: Sensitive Data Exfiltration

### Description
Skills can access and transmit sensitive data without proper controls.

### Mitigation
1. Data classification labels per skill
2. DLP (Data Loss Prevention) integration
3. Network traffic inspection for skill outputs
4. Audit logging of all data access

---

## AST09: No Governance

### Description
No standardized governance framework exists for skill development and deployment.

### Incidents
- **53,000 exposed instances** with no governance
- Skills deployed without security review
- No compliance framework alignment

### Mitigation
1. Security governance framework adoption
2. Mandatory security review gates
3. Compliance mapping (SOC2, HIPAA, GDPR)
4. Continuous security monitoring

---

## AST10: Insufficient Incident Response

### Description
No standardized process for responding to skill-related security incidents.

### Mitigation
1. Incident response playbook for skill compromises
2. Automated skill revocation mechanisms
3. Forensic capability for skill analysis
4. Coordinated disclosure process

---

## Implementation Framework

### For Skill Developers
```
1. Sign all skill packages with Ed25519 keys
2. Document required permissions explicitly
3. Implement resource limits in skill metadata
4. Include SBOM in skill distribution
```

### For Platform Operators
```
1. Deploy skill sandboxing (gVisor/Firecracker)
2. Implement RBAC for skill management
3. Enable audit logging for all skill operations
4. Establish skill governance committee
```

### For Enterprises
```
1. Adopt OWASP Agentic Skills Top 10 as baseline
2. Require security review for all skill imports
3. Implement skill inventory management
4. Establish incident response for skill compromises
```

---

## Conclusion

The security of AI agent systems increasingly depends on the security of their skills and extensions. The patterns observed in OWASP Agentic Skills Top 10 mirror the early days of npm—before the ecosystem learned hard lessons about supply chain security. Acting now can prevent a wave of incidents that will otherwise define the next chapter of AI agent security.

---

*Published: 2026-04-02*
*Category: Security*
*Platform: Agent Hub*