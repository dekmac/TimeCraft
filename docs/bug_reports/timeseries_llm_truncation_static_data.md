# Bug Report: LLM TimeSeries Generation Produces Static / Rejected Data and Misclassified Lengths

## Summary
Recent logs show the time series generation workflow repeatedly rejecting LLM outputs due to length mismatches (e.g., 315, 296, 365 vs expected 288) and ultimately returning empty lists for several sensors. After a parsing policy change that should accept variable lengths (truncate or allow short), older rejection log messages still appear, indicating parts of the code path still enforce strict equality. Additionally, accepted sequences after truncation are completely static (all 18.5, all 23.0, monotonically incremental by 0.1), giving the impression of "mocked" or non-physically-driven data.

## Impact
- Multiple sensors fail to return any timeseries (empty arrays) after 3 attempts, reducing system utility.
- When data is returned it is often unrealistically static, failing physics validation.
- Validation correctly flags non-realistic patterns (e.g., OVERALL_VALID: NO) but workflow does not attempt semantic improvement/regeneration for physics failures (only for reflection stage, not for initial physics validation).
- Logging misleads operators: shows rejection due to length mismatch even though new truncation logic should handle over-length responses.
- User perceives results as fabricated/mocked because: (a) static plateaus; (b) repeated identical values across large spans; (c) absence of variability consistent with scenario instructions.

## Evidence (Extracted From Logs)
| Sensor | Parsed Lengths | Outcome | Notes |
|--------|----------------|---------|-------|
| SF_BLDG_HUMIDITY_SENSOR_01 | 315, 296, 365 | Empty | All rejected for length mismatch |
| SF_BLDG_CRACK_WIDTH_SENSOR_01 | 3, 330, 500 | Empty | Very low then very high count; final large static-ish sequence |
| SF_BLDG_OCCUPANCY_SENSOR_01 | 3, 500, 500 | Empty | Fails length each attempt |
| SF_BLDG_CO2_SENSOR_01 | 641, 267, 3 | Empty | Mixed lengths; last only 3 values |
| SF_MAINHALL_TEMP_C_01 | 400 (truncated) | Accepted static | All 18.5 values (flat) |
| SF_MAINHALL_HUMIDITY_PCT_01 | 400 (truncated) | Accepted semi-linear | Slight incremental pattern, still unrealistic |
| SF_NAVE_CRACKWIDTH_MM_01 | 324 (truncated) | Accepted | Passes validation |

## Root Cause Analysis
1. **Parser Policy Inconsistency**
   - We updated `parse_timeseries_response` to truncate or accept short sequences, but rejection logs (`Rejecting result`) still appear. This indicates either:
     - a) Running code is from an earlier version (deployment not restarted / hot reload mismatch), or
     - b) Another parsing pathway duplicates older strict logic (possibly `parse_llm_timeseries_response` from `.helpers` or an inline legacy block) used in certain handlers before new function invocation.

2. **Static / Formulaic Outputs**
   - Prompts enforce EXACT value count; when model drifts and emits descriptive preamble (DEVICE TYPE lines), numeric extraction yields large blocks of uniform values (model falls back to simple constant series under constraint pressure).
   - No post-generation variability enforcement beyond optional validator; validator does not currently trigger regeneration—only reports metrics.
   - Physics validation marks data invalid (OVERALL_VALID: NO) but code path chooses to "keep original values" rather than prompting for improved re-generation with guidance (improvement loop only exists in separate reflection function not invoked on initial physics failure).

3. **Length-Based Retry Logic Still Too Narrow**
   - Generation loop currently retries only when zero numeric values are parsed (post-fix). In logs we still see retries triggered by length mismatch, implying old logic: `if len(values) != sequence_length: return []` which forces empty parse → triggers retry; static or uniform patterns that match length on first attempt skip any improvement attempt.

4. **Lack of Distinction Between Metadata and Data**
   - The LLM includes sensor specification prose. Our current regex splitting lumps all numbers, potentially capturing enumerated bullet numbers or spec ranges not belonging to the timeseries (e.g., 0.52 repeating, or range endpoints). This inflates counts (641, 500) and dilutes signal.

5. **No Sanitization of Repeated Constant Series**
   - A constant sequence of length 288 passes parsing and proceeds to validation; physics failure does not trigger regeneration.

6. **Insufficient Prompt Guardrails**
   - The enhanced prompt instructs EXACT numeric list, but situational instructions still allow model to output metadata. Lack of a hard pattern enforcement (e.g., regex constraints or formatting example repeated) reduces compliance.

7. **Validation Result Handling**
   - `validate_scenario_alignment` returns `is_valid=False` but we do not branch into an improvement loop (unlike tagging & reflection). This misses an opportunity to salvage poor physics adherence without mock data.

## Contributing Factors
- Legacy rejection logging leftover after new parser patch.
- Potential alternative parser or stale process instance.
- Over-reliance on a single prompt without iterative constraint tightening.
- Missing semantic improvement loop after physics validation failure.
- No heuristic filters to strip spec blocks before numeric extraction.

## Proposed Fixes (Actionable)
| # | Area | Change | Rationale | Effort |
|---|------|--------|-----------|--------|
| 1 | Parsing | Add pre-extraction block removal: truncate at first line containing only or starting with `DEVICE TYPE:` / `SPECIFICATIONS:` unless numeric sequence follows on same line | Avoid capturing spec prose numbers inflating length | Low |
| 2 | Parsing | Implement numeric block isolation: use regex to find the longest contiguous comma-separated numeric region; discard others | Reduces noise from headers | Medium |
| 3 | Logging | Remove stale "Rejecting result" path; ensure only new truncation messages appear; add field `parse_mode` (full, truncated, short, longest_block) | Operator clarity | Low |
| 4 | Generation Loop | If physics validation fails with static or near-constant series (std dev < threshold), trigger one improvement regeneration prompt referencing validation feedback | Replace unrealistic plateaus | Medium |
| 5 | Validation | Add quick stats (mean, std, max_delta) into validation dict to support regeneration heuristics | Data-driven improvement gating | Low |
| 6 | Prompting | Prepend explicit guard clause: `OUTPUT FORMAT STRICT: provide ONLY a single line of comma-separated numeric values. DO NOT include headers, units, bullet points, or explanatory text.` Provide negative examples | Reduce metadata bleed | Low |
| 7 | Reflection Integration | Invoke `reflect_on_timeseries_generation` automatically when `is_valid=False` OR variability heuristic fails (once, not full loop) | Unified improvement pathway | Medium |
| 8 | Anti-Constant Heuristic | If after truncation: unique_values <= 5 for 288 points and sensor not expected to be stable (e.g., temperature, occupancy), force improvement pass | Avoid mocked feel | Low |
| 9 | Metadata | Return `length_status` plus `raw_parsed_length` and `extracted_block_length` before truncation | Preserve provenance | Low |
|10 | Config Flag | Introduce `strict_length_mode` (default False) enabling teams to opt back to prior strict behavior | Operational flexibility | Low |
|11 | Tests | Add unit tests for: (a) over-length with metadata; (b) under-length acceptance; (c) constant series regeneration; (d) spec prose filtering; (e) variability heuristic triggers | Prevent regression | Medium |

## Detailed Remediation Plan
1. Update prompt template injection with STRICT output format and negative examples.
2. Enhance `parse_timeseries_response`:
   - Pre-clean: remove lines starting with known metadata tokens (DEVICE TYPE, SENSOR TYPE, CATEGORY, SPECIFICATIONS, MEASUREMENT, TYPICAL, **, bullet '-') unless line contains a comma-separated predominantly numeric pattern.
   - Extract candidate numeric blocks via regex: `(?:\d+(?:\.\d+)?\s*,\s*){10,}\d+(?:\.\d+)?` choose longest.
   - Fallback to existing token split if no block found.
3. Record raw token count, block length, truncated length.
4. Modify generation loop to always attempt improvement if `is_valid=False` and improvement not yet tried; pass validation feedback into improvement prompt.
5. Implement variability heuristic: compute std dev & unique count; if below thresholds trigger improvement.
6. Extend validation result object with metrics; ensure they propagate to API response.
7. Add config/env flags: `TIMESERIES_STRICT_LENGTH`, `TIMESERIES_ENABLE_AUTO_IMPROVE`.
8. Write tests in `tests/unit/` (create if absent) for new parsing and improvement triggers.
9. Add documentation (this file) & link from DEVELOPMENT_GUIDELINES or README troubleshooting section.

## Risks & Mitigations
- Risk: Over-aggressive filtering removes valid numbers. Mitigation: fallback path preserves old behavior if no dense block detected.
- Risk: Extra API calls increase latency. Mitigation: single improvement attempt; configurable.
- Risk: Prompt still ignored. Mitigation: add negative examples + improvement pass focusing solely on format.

## Test Plan
| Test | Input | Expected Outcome |
|------|-------|------------------|
| Over-length with metadata | Response starting with DEVICE TYPE plus 400 numbers | Parser extracts first dense numeric block; truncated to 288; metadata recorded | 
| Constant series | 288 identical numbers | Validation fails due to low variability; improvement trigger generates varied series | 
| Under-length | 180 values | Accepted (length_status=short); no improvement if variability ok | 
| Mixed prose numbers | Ranges and bullet stats plus 50 numeric values | Longest block chosen; counts correct | 
| Strict mode on | 180 values with strict flag True | Rejected, triggers regeneration | 
| Improvement disabled | Invalid physics sequence but flag off | Returned as-is with note | 

## Rollout Steps
1. Implement parsing & prompt updates behind flags (defaults safe).
2. Add tests & run locally.
3. Deploy to staging, collect log samples for variety.
4. Enable auto-improve flag gradually.
5. Monitor latency & success rate; adjust thresholds.

## Next Actions
- Await approval to implement code changes.
- On approval: execute remediation plan items 1–8.

---
*Generated automatically; edit as needed before PR.*
