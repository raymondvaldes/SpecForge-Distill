# Phase 06 Research

Phase 6 covers cross-platform runtime ergonomics for:
- WSL
- Ubuntu
- macOS
- Windows PowerShell 7

Research for this phase should also absorb the pending IV&V follow-on work from the Phase 5 closeout:

- harden runtime-adjacent tests for robustness and performance rather than relying on machine-sensitive wall-clock thresholds
- revisit determinism and reliability coverage so wrapper, manifest, and platform behavior remain hermetic and repeatable
- include targeted refactors that simplify runtime logic, remove duplicated decision paths, and improve maintainability while preserving deterministic behavior
- align any new runtime work with the intent captured in `docs/TEST_IVV_VISION.md`
- update `docs/TEST_SPEC.md` when Phase 6 work changes the verification boundary or introduces new platform/runtime assertions

Add platform-specific research notes here as planning begins.
