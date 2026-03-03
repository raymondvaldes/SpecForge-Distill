# Release Notes: v1.2.2

This patch release introduces significant quality improvements to the requirement extraction engine, including stricter modal-only capture and improved context handling for notes.

## Release Snapshot

- Latest stable release: `v1.2.2`
- Status: Released

## Highlights

- **Strict Modal-Only Extraction:** The engine now strictly requires an explicit obligation verb (e.g., `shall`, `must`, `should`) from the taxonomy to trigger a requirement capture. This eliminates "neutral" noise and improves extraction precision.
- **Automatic Note Merging:** Trailing `Note:` and `Notes:` blocks are now automatically detected and merged into the preceding requirement statement, ensuring all relevant context is preserved in a single record.
- **Improved Deduplication:** Enhanced semantic deduplication pass in the normalization pipeline to prevent redundant output from repeating sections.

## Added

- New extraction logic to detect and append `Note:` and `Notes:` paragraphs to requirements.
- Taxonomy version `2026.03` which focuses strictly on high and medium obligation levels.

## Changed

- Narrative extraction now filters out short segments (less than 10 characters) and neutral "hints" that lack explicit obligation verbs.
- Removed `may` and `optional` from the default taxonomy to focus on actionable requirements.

## Fixed

- Resolved issues where Table of Contents entries were incorrectly captured as requirements.
- Fixed a bug where semantic duplicates were being linked but not removed from the final output.
- Corrected multiple documentation links and versioning inconsistencies.

## Upgrade Path

- Users upgrading to `v1.2.2` will see cleaner, more concise output. If you relied on "may/optional" extraction, please note these are now ignored by default.
