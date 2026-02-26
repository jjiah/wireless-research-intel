---
report_id: {{report_id}}
week_start: {{week_start}}
week_end: {{week_end}}
generated_on: {{generated_on}}
data_window: {{data_window}}
new_items_count: {{new_items}}
total_items_count: {{total_items}}
active_venues_count: {{active_venues}}
skipped_no_doi: {{skipped_no_doi}}
inputs:
  new_json_files: {{new_json_files}}
  prior_reports_used: {{prior_reports_used}}
  index_db: {{index_db}}
---

# Weekly Wireless Report (Week of {{week_start}})
Generated: {{generated_on}}

## Sources
{{#sources}}
- {{.}}
{{/sources}}
{{^sources}}
- (none)
{{/sources}}

## Summary
- Date range: {{week_start}} to {{week_end}}
- New items added: {{new_items}}
- Total items (cumulative): {{total_items}}
- Items skipped (no DOI): {{skipped_no_doi}}
- Venues active this week: {{active_venues}}
- New venues this week: {{new_venues}}
- Top emerging topics: {{top_topics}}

## Snapshot Stats
- Items per venue (top 5): {{items_per_venue_top5}}
- Items per topic (top 5): {{items_per_topic_top5}}
- Median time from publication to ingestion (days): {{median_pub_to_ingest_days}}

## Long-Term Trends (from prior reports)
- Report window compared: {{trend_window}}
- Topic momentum (top rising): {{topic_momentum_up}}
- Topic momentum (top declining): {{topic_momentum_down}}
- Stable core topics: {{topic_core}}
- Venue momentum (top rising): {{venue_momentum_up}}
- Venue momentum (top declining): {{venue_momentum_down}}
- Notable shifts vs last period: {{notable_shifts}}

## Venue Highlights
{{#venues}}
### {{name}}
{{#items}}
- {{title}} ({{published}}) — {{url}}
{{/items}}
{{^items}}
- (no items)
{{/items}}

{{/venues}}

## Key Topics (LLM)
{{#topics}}
### {{name}}
- Summary: {{summary}}
- Methods: {{methods}}
- Key challenges: {{challenges}}
- Representative papers: {{papers}}
- Evidence (DOIs): {{evidence_dois}}
{{/topics}}
{{^topics}}
- (no topics)
{{/topics}}

## Topic Relationships (LLM)
- {{topic_relationships}}

## Open Problems (LLM)
- {{open_problem_1}}
- {{open_problem_2}}
- {{open_problem_3}}

## Relevance to My Research (LLM)
- My current focus: {{my_focus}}
- Directly aligned topics: {{aligned_topics}}
- Adjacent opportunities: {{adjacent_opportunities}}
- Potential pivots / risks: {{pivots_risks}}
- Suggested next steps for me: {{my_next_steps}}

## Provenance
- Ingestion run: {{ingest_run_id}}
- Sources snapshot: {{sources_snapshot}}
- Notes: {{provenance_notes}}

## Notable Papers
{{#notable}}
- {{title}} — {{venue}} — {{url}}
{{/notable}}
{{^notable}}
- (none)
{{/notable}}

## Actions / Follow-ups
- {{action_1}}
- {{action_2}}
