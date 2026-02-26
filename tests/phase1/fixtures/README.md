# Phase 1 Acceptance Fixtures

This fixture set defines the Phase 1 acceptance contract:

- Required source-type candidate channels: narrative, table_cell, caption_context.
- Required warning behavior: low-text pages emit `low_text_quality` warnings.
- Required provenance behavior: every candidate and architecture artifact includes citations.

`expected_outputs.yaml` is JSON-formatted YAML for deterministic parsing in tests.
