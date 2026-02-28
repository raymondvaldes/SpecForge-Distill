# Requirements: SpecForge Distill

**Defined:** 2026-02-28
**Milestone:** `v1.1.0`
**Core Value:** Transform legacy spec PDFs into structured, provenance-linked markdown without missing critical requirement obligations.

## v1.1 Requirements

### Trusted Distribution

- [x] **REL-01**: Official releases provide platform-specific binaries with checksum-backed verification guidance for Ubuntu/WSL, macOS Intel, macOS Apple Silicon, and Windows PowerShell 7.
- [x] **REL-02**: User can run an install verification or self-test workflow that confirms the binary starts correctly and can process a known-good fixture.
- [x] **REL-03**: Release automation validates signed/notarized artifacts when signing secrets are configured and fails clearly when trust checks do not pass.

### Cross-Platform UX

- [x] **PLAT-02**: PowerShell 7 users can complete first-run and local-helper workflows without Bash-only assumptions.
- [x] **PLAT-03**: WSL and native Linux users receive clear guidance for common permission/path pitfalls.
- [x] **CLI-04**: CLI errors distinguish malformed PDFs, scanned/OCR-only PDFs, and genuinely empty extraction results.

### Batch Processing And Reporting

- [ ] **CLI-05**: User can process a directory or explicit list of PDFs in one command.
- [ ] **OUT-06**: Batch runs emit a machine-readable summary of successes, failures, warnings, and output locations.
- [ ] **RUN-02**: Batch mode uses deterministic output naming and returns a non-zero exit code when any input fails.

### Ingestion Breadth And Validation

- [ ] **ING-03**: Tool detects scanned/OCR-only PDFs explicitly and reports next actions instead of generic processing failures.
- [ ] **VAL-01**: User can run requirement-quality checks or export-ready validation as a separate command or artifact.
- [ ] **INT-02**: User can emit richer downstream interop/export metadata for SysML-oriented follow-on tooling.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Cloud-hosted or team-shared orchestration in `v1.1.0` | Keep the milestone focused on local CLI workflows |
| Automatic OCR correction for arbitrary low-quality scans | Detection and boundary-setting come first |
| Automatic diagram-to-Mermaid conversion | Still secondary to requirements and architecture extraction quality |
| Full repository or API synchronization workflows | Better fit for later interop milestones |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REL-01 | Phase 5 | Complete |
| REL-02 | Phase 5 | Complete |
| REL-03 | Phase 5 | Complete |
| PLAT-02 | Phase 6 | Complete |
| PLAT-03 | Phase 6 | Complete |
| CLI-04 | Phase 6 | Complete |
| CLI-05 | Phase 7 | Planned |
| OUT-06 | Phase 7 | Planned |
| RUN-02 | Phase 7 | Planned |
| ING-03 | Phase 8 | Planned |
| VAL-01 | Phase 8 | Planned |
| INT-02 | Phase 8 | Planned |

**Coverage:**
- v1.1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-28*
*Last updated: 2026-02-28 after Phase 6 execution*
