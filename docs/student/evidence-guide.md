# Task 1.5 supplied evidence

Audit each C01-C10 claim in [the draft](ai-capacity-report-draft.md) against [evidence-pack.json](evidence-pack.json). Every claim requires its own classification, a correction from the pack's correction_choices, and the required evidence ID set; select the exact number specified for that claim. `measurement-definition-error` is a metric being relabeled as a different quantity. `calculation-error` concerns units, arithmetic or the supplied formula. `unsupported-assumption` lacks evidence.

Select the correction method that fixes the claim, or retain the claim when the pack establishes it as a planning assumption. The numeric correction values belong in the named calculation fields in Step 2.

The historical retuned 2-user results remain for auditing provenance and measurement meaning. They are not Task 1.4's current 20-user experiment and are not pure service-time measurements. The capacity input uses newly captured Task 1.4 worker spans, with explicit counts, sums and provenance. Use the supplied pooled duration rounded to six decimals as the worker formula input.

The sensor workload, growth, exception fraction, retention and operating thresholds are authored hypothetical planning inputs, not measured production traffic or SLOs. Derive projected ingestion, exception rate and raw retained storage with explicit unit fields. Decimal MB and GB use 10^6 and 10^9 bytes. Retention covers raw payload only, excluding indexes, replicas and overhead.

For workers record input service duration, arrival rate, their product, the margin fraction, the result after applying that margin exactly once, and the integer count after a single ceiling at the end. Service input tolerance is 0.000001 seconds/job; intermediate workers 0.0001; other numeric tolerances are 0.001 of the named unit. Integer counts must match exactly.

Choose one of the two bounded pilot options allowed by the operating policy. The structured ADR must consistently connect context, decision, both alternatives, that pilot's consequence, trigger, rollback and next measurement. Either coherent option is accepted; mixing one pilot's decision with another's operational conditions is not. Pilot recommendations do not implement a production scaling change.

Your required runtime investigations and final Markdown decision-evidence record support instructor discussion. The fixed assessment pack makes the automatic calculations and bounded decisions reproducible; it does not grade an open-ended prose defense.

Each selection count is explicit in the sheet and schema. For scaling_recommendation.evidence_ids, select four records covering measured service demand, the projected workload, the approved pilot policy, and limits of transferring local results to production. Include both named alternatives and exactly one consequence of the selected pilot. These are complete case answers, not optional supporting citations.
