# Blockify + Kibana: Governance Dashboards for Your RAG Knowledge Base

> **TL;DR:** Kibana is the standard visualization tier for Elastic-backed systems. Once your corpus is indexed as IdeaBlocks (via [Blockify + Elastic](./BLOCKIFY-ELASTIC.md)), every block carries structured metadata — tags, entities, source documents, validation status. Kibana turns that metadata into the RAG governance dashboard most teams never had: coverage, drift, duplication rate, and retrieval hit-rate, all in one place.

---

## The Problem: RAG Systems Are Black Boxes

Most enterprise RAG stacks run blind:

- **No coverage visibility** — Which products, regions, policies are under-represented in the knowledge base?
- **No drift detection** — When does content become stale? Who's updated what?
- **No validation state** — Which blocks have been reviewed by a subject-matter expert and which are AI-generated only?
- **No retrieval auditing** — Which IdeaBlocks are being retrieved? Which are never returned?

Without this, the first signal that your RAG is rotting is usually a customer-facing hallucination.

---

## How Blockify Fits

Blockify produces richly-tagged IdeaBlocks. Elastic indexes them with structured metadata. Kibana reads the index and gives you five dashboards out of the box.

```
IdeaBlocks in Elastic  →  Kibana Data View  →  Five dashboards
   (blockify-ideablocks)    (ideablocks*)       1. Knowledge Coverage
                                                 2. Content Drift
                                                 3. Validation State
                                                 4. Retrieval Hit-Rate
                                                 5. Entity Graph
```

---

## Quick Start

### 1. Create the Kibana Data View

Settings → Data Views → Create. Index pattern: `blockify-ideablocks`. Time field: `ingested_at`.

### 2. Import the five dashboards

Save the following five saved-search definitions (JSON bodies abbreviated here; full NDJSON import file lives in `/assets/kibana/blockify-dashboards.ndjson`):

#### Dashboard 1 — Knowledge Coverage

- **Visualization:** Treemap of `entity_type` × `entity_name`, sized by block count
- **Purpose:** See which product lines, personas, or topics dominate the knowledge base — and where gaps live
- **Query:** `*`

#### Dashboard 2 — Content Drift

- **Visualization:** Line chart of `count()` by `ingested_at`, split by `tags`
- **Purpose:** Spot tags (e.g., `pricing`, `policy-v2`) with no recent updates
- **Tip:** Filter for `tags: "current"` and alert on zero-change over 90 days

#### Dashboard 3 — Validation State

- **Visualization:** Pie chart of `validation_status` (`draft` / `sme_approved` / `ai_only`)
- **Purpose:** Show the percentage of the knowledge base that has SME sign-off
- **Secondary:** Data table of IdeaBlocks still in `draft` state, sorted by retrieval frequency

#### Dashboard 4 — Retrieval Hit-Rate

- **Visualization:** Horizontal bar chart of `retrievals_30d` by `name`, top 50
- **Purpose:** Identify "zombie" blocks (high count, never retrieved) and "hero" blocks (retrieved on most queries — candidates for SME review priority)
- **Data source:** A side index `blockify-retrieval-log` populated by your app layer

#### Dashboard 5 — Entity Graph

- **Visualization:** Vega-Lite graph of `entity_name` nodes linked by shared `tags`
- **Purpose:** See how concepts cluster; spot orphan entities; guide taxonomy refinement

---

## Advanced Patterns

### Pattern 1: Alert on retrieval failures

Use Kibana's Alerting rules to fire when a user query returns zero results. Feed the alert into a "gap" backlog that SMEs triage weekly.

```json
{
  "rule_type_id": ".es-query",
  "params": {
    "esQuery": "{\"query\":{\"match\":{\"retrieval_hit_count\":0}}}",
    "threshold": [10],
    "thresholdComparator": ">"
  }
}
```

### Pattern 2: Watcher for drift

Every night, compute `now() - max(ingested_at)` grouped by `tags`. Alert Slack when any priority tag has been static for 60+ days.

### Pattern 3: Lens dashboards per business unit

Filter each dashboard by `tags: "sales"` / `tags: "engineering"` / `tags: "legal"` and share a unit-scoped view with each team lead.

---

## Why Blockify + Kibana

| Vanilla RAG observability | Blockify + Kibana |
|---|---|
| Retrieval is opaque — no way to audit what's being returned | Full retrieval log joined to IdeaBlock metadata |
| No coverage map of the knowledge base | Treemap shows entity / topic distribution |
| Drift only surfaces when a customer complains | Time-series views fire alerts before complaints |
| SME review cadence is ad hoc | Validation-state pie makes review queue obvious |

---

## Related Integrations

- [Blockify + Elastic](./BLOCKIFY-ELASTIC.md) — Required backing store for Kibana dashboards
- [Blockify + LangChain](./BLOCKIFY-LANGCHAIN.md) — Instrument retrieval calls to populate the retrieval log
- [Blockify + n8n](./BLOCKIFY-N8N.md) — Trigger re-ingestion workflows from Kibana alerts
- [Blockify + Starburst](./BLOCKIFY-STARBURST.md) — Federate Kibana dashboards across multiple IdeaBlock sources

---

*Kibana is a trademark of Elasticsearch N.V. Blockify is an independent open-source project and is not affiliated with Elastic.*
