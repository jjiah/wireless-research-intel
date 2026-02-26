---
report_id: {{report_id}}
week_start: {{week_start}}
week_end: {{week_end}}
generated_on: {{generated_on}}
data_window_days: {{data_window_days}}
new_items_count: {{new_items}}
total_items_count: {{total_items}}
active_venues_count: {{active_venues}}
inputs:
  new_json_files: {{new_json_files}}
  prior_reports_used: {{prior_reports_used}}
  index_db: {{index_db}}
quality:
  missing_abstract_count: {{missing_abstract_count}}
  missing_doi_count: {{missing_doi_count}}
  deduped_count: {{deduped_count}}
parameters:
  clustering:
    method: {{cluster_method}}              # tfidf_kmeans | embedding_hdbscan
    k_or_min_cluster_size: {{cluster_param}}
  novelty:
    ngram_range: {{novelty_ngram_range}}    # e.g., "2-3"
    min_doc_freq_current: {{novelty_min_df_current}}
    max_doc_freq_baseline: {{novelty_max_df_baseline}}
  trend:
    baseline_window_days: {{baseline_window_days}} # e.g., 56
    smoothing_alpha: {{smoothing_alpha}}           # e.g., 1.0 (Laplace)
---

# Wireless Research Intelligence Report (WRIS v1.2)
**Week:** {{week_start}} - {{week_end}}  
**Generated:** {{generated_on}}  
**Scope:** Venue-wide, no topic filtering.  

## 0. Sources & Coverage
### Sources
{{#sources}}
- {{.}}
{{/sources}}
{{^sources}}
- (none)
{{/sources}}

### Coverage snapshot
- New works ingested (this week): **{{new_items}}**
- Total works in local index (cumulative): **{{total_items}}**
- Active venues this week: **{{active_venues}}**
- Missing abstracts: **{{missing_abstract_count}}**
- Missing DOIs: **{{missing_doi_count}}**
- Deduplicated items: **{{deduped_count}}**
- Median pub-to-ingest lag (days): **{{median_pub_to_ingest_days}}**

---

## 1. Executive Intelligence (read this first)
### Top signals this week
- **Top accelerating clusters (momentum):** {{top_clusters_by_momentum}}
- **Top emerging micro-topics (emergence):** {{top_microtopics_by_emergence}}
- **New terminology / phrases (novelty):** {{top_novel_phrases}}
- **Methodological drift (rising methods):** {{top_methods_rising}}
- **Early impact leaders (citation velocity):** {{top_early_impact}}

### 1-paragraph field interpretation (LLM)
{{executive_interpretation}}

### Actionable research breadcrumbs (explicit search strings)
> Use these directly for follow-up searching (OpenAlex / Semantic Scholar / Google Scholar).
- **Topic queries:**  
{{#topic_queries}}
  - {{.}}
{{/topic_queries}}
{{^topic_queries}}
  - (none)
{{/topic_queries}}

- **Keyword / phrase queries:**  
{{#keyword_queries}}
  - {{.}}
{{/keyword_queries}}
{{^keyword_queries}}
  - (none)
{{/keyword_queries}}

---

## 2. Quant Snapshot (high-signal stats)
- Items per venue (top 10): {{items_per_venue_top10}}
- Items per cluster (top 10): {{items_per_cluster_top10}}
- Items per method tag (top 10): {{items_per_method_top10}}
- Items per concept/keyword (top 10): {{items_per_keyword_top10}}

---

## 3. Topic Landscape (clusters)
> Clusters are computed from titles+abstracts when available; titles-only otherwise.

{{#clusters}}
### Cluster {{cluster_id}} - {{cluster_label}}
- Size (this week): {{n_current}}
- Size (baseline): {{n_baseline}}
- Share (this week): {{share_current}}
- Share (baseline): {{share_baseline}}
- **Momentum score:** {{momentum_score}}
- **Emergence score:** {{emergence_score}}
- **Novelty score:** {{novelty_score}}
- Representative terms: {{top_terms}}
- Representative phrases (2-grams): {{top_phrases}}

**What this cluster is about (LLM):**  
{{cluster_summary}}

**Methods commonly used (LLM + rules):**  
{{cluster_methods}}

**Representative papers (top 5):**
{{#representative_papers}}
- {{title}} ({{published}}) - {{venue}} - {{url}} {{#doi}}- DOI: {{doi}}{{/doi}}
{{/representative_papers}}

{{/clusters}}
{{^clusters}}
- (no clusters)
{{/clusters}}

---

## 4. Emerging Micro-Topics & New Terminology
### 4.1 Emerging micro-topics (low volume, high growth)
{{#emerging_microtopics}}
- {{name}} - emergence={{emergence_score}}, current={{count_current}}, baseline={{count_baseline}}
  - Evidence phrases: {{evidence_phrases}}
  - Example papers: {{example_papers}}
{{/emerging_microtopics}}
{{^emerging_microtopics}}
- (none)
{{/emerging_microtopics}}

### 4.2 New phrases (novelty detector)
{{#novel_phrases}}
- "{{phrase}}" - novelty={{novelty_score}}, current_df={{df_current}}, baseline_df={{df_baseline}}
  - Appears in: {{example_papers}}
{{/novel_phrases}}
{{^novel_phrases}}
- (none)
{{/novel_phrases}}

---

## 5. Methodological Drift (what methods are taking over)
### 5.1 Rising methods (trend delta)
{{#methods_rising}}
- {{method}} - current={{count_current}}, baseline={{count_baseline}}, momentum={{momentum_score}}
{{/methods_rising}}
{{^methods_rising}}
- (none)
{{/methods_rising}}

### 5.2 Declining methods (trend delta)
{{#methods_declining}}
- {{method}} - current={{count_current}}, baseline={{count_baseline}}, momentum={{momentum_score}}
{{/methods_declining}}
{{^methods_declining}}
- (none)
{{/methods_declining}}

### 5.3 Method notes (LLM)
{{method_notes}}

---

## 6. Early Impact Signals
> Not total citations; focuses on early velocity.

### 6.1 Citation velocity leaders (top 10)
{{#citation_velocity_leaders}}
- {{title}} - {{venue}} (pub {{published}}) - v={{citation_velocity}}/day - cited_by={{cited_by_count}} - {{url}}
{{/citation_velocity_leaders}}
{{^citation_velocity_leaders}}
- (none)
{{/citation_velocity_leaders}}

### 6.2 Cross-venue consensus topics
{{cross_venue_consensus}}

---

## 7. Structural Shifts & Convergence (LLM + evidence)
- **Shift 1:** {{shift_1}}  
  - Evidence: {{shift_1_evidence}}
- **Shift 2:** {{shift_2}}  
  - Evidence: {{shift_2_evidence}}
- **Shift 3:** {{shift_3}}  
  - Evidence: {{shift_3_evidence}}

---

## 8. Open Problems (LLM, evidence-based)
- {{open_problem_1}}  
  - Evidence: {{open_problem_1_evidence}}
- {{open_problem_2}}  
  - Evidence: {{open_problem_2_evidence}}
- {{open_problem_3}}  
  - Evidence: {{open_problem_3_evidence}}

---

## 9. My Research Alignment (LLM, decision-oriented)
- My current focus: {{my_focus}}

### 9.1 Directly aligned clusters (do now)
{{aligned_clusters}}

### 9.2 Adjacent opportunities (explore)
{{adjacent_opportunities}}

### 9.3 Saturation / risk warnings (avoid or differentiate)
{{saturation_warnings}}

### 9.4 Concrete next steps (1-2 weeks)
{{my_next_steps}}

---

## 10. Venue Highlights (raw list)
{{#venues}}
### {{name}}
{{#items}}
- {{title}} ({{published}}) - {{url}} {{#doi}}- DOI: {{doi}}{{/doi}}
{{/items}}
{{^items}}
- (no items)
{{/items}}

{{/venues}}

---

## 11. Notable Papers (curated)
{{#notable}}
- {{title}} - {{venue}} - {{url}} {{#doi}}- DOI: {{doi}}{{/doi}}
{{/notable}}
{{^notable}}
- (none)
{{/notable}}

---

## 12. Provenance & Reproducibility
- Ingestion run: {{ingest_run_id}}
- Sources snapshot: {{sources_snapshot}}
- Normalization notes: {{normalization_notes}}
- Trend baseline window: {{baseline_window_days}} days
- Clustering method: {{cluster_method}} ({{cluster_param}})
- Notes: {{provenance_notes}}

---

## 13. Actions / Follow-ups
- {{action_1}}
- {{action_2}}
