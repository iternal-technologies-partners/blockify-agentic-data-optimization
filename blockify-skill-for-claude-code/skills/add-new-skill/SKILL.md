# Best Practices for Writing and Using SKILL.md Files

> Compiled from [Official Anthropic Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills), [anthropics/skills repository](https://github.com/anthropics/skills), and community analysis (2025-2026).

---

## 1. What Skills Are (Mental Model)

Skills are **onboarding guides for specialized tasks**—modular instruction packages Claude loads dynamically when relevant. They transform Claude from general-purpose to domain-expert with procedural knowledge no model inherently possesses.

| Aspect | CLAUDE.md | Skills |
|--------|-----------|--------|
| Loading | Always (startup) | On-demand (triggered) |
| Scope | Project-wide rules | Task-specific workflows |
| Context cost | Every conversation | Only when needed |
| Structure | Single file | Directory with resources |

**Use CLAUDE.md for**: Unchanging conventions, coding standards, always-on project rules.
**Use Skills for**: Complex workflows, scripts, templates, domain expertise activated contextually.

---

## 2. Architecture (How Skills Work Internally)

### Token Loading Hierarchy

```
Level 1: Metadata only (always loaded)     ~100 tokens
         name + description in system prompt
                    ↓
Level 2: SKILL.md body (on trigger)        ~1,500-5,000 tokens
         Full instructions load after skill selected
                    ↓
Level 3: Bundled resources (as-needed)     Unlimited
         scripts/ references/ assets/
         Only read when Claude determines necessary
```

### Selection Mechanism

**Pure LLM reasoning—no algorithmic matching.** Claude evaluates all skill descriptions via natural language understanding, not embeddings/classifiers/keyword-matching. This means:

- Description quality is **critical** for triggering
- Vague descriptions → skill never triggers
- Specific trigger phrases → reliable activation

### Execution Model

Skills use a **dual-message injection pattern**:
1. Metadata message (`isMeta: false`) — visible to user as status
2. Skill prompt message (`isMeta: true`) — hidden from UI, sent to API

This provides transparency without dumping instruction walls into chat.

---

## 3. Required Structure

```
skill-name/
├── SKILL.md                    # Required - instructions + frontmatter
├── scripts/                    # Optional - executable code
│   └── validate.py
├── references/                 # Optional - docs loaded into context
│   ├── api.md
│   └── schema.md
└── assets/                     # Optional - files used in output (not loaded)
    └── template.docx
```

### Frontmatter (YAML)

```yaml
---
name: processing-pdfs                    # Required: lowercase, hyphens only
description: >-                          # Required: what + when to use
  Extract text and tables from PDF files, fill forms, merge documents.
  Use when working with PDF files or when user mentions PDFs, forms,
  or document extraction.
---
```

**Validation rules:**
- `name`: ≤64 chars, `[a-z0-9-]` only, no "anthropic"/"claude"
- `description`: ≤1024 chars, non-empty, no XML tags

### Body (Markdown)

Instructions Claude follows after skill triggers. Target **<500 lines**. Split into reference files when exceeding.

---

## 4. Core Design Principles

### 4.1 Conciseness Is Survival

Context window = public good. Every token competes with conversation history, other skills, user requests.

**Default assumption: Claude is already intelligent.** Only add what Claude doesn't know.

```markdown
# BAD (~150 tokens) - explains obvious things
PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available...

# GOOD (~50 tokens) - assumes competence
## Extract PDF text
Use pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

**Challenge each line:** "Does Claude need this? Does this justify its token cost?"

### 4.2 Progressive Disclosure

Never front-load everything. Structure for on-demand loading.

```markdown
# In SKILL.md - overview + pointers
## Quick start
[Essential code example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```

Claude loads `FORMS.md` only when user needs forms.

**Critical rules:**
- Keep references **one level deep** from SKILL.md
- No chains: SKILL.md → advanced.md → details.md (Claude may partial-read)
- Long files (>100 lines): include TOC at top

### 4.3 Degrees of Freedom

Match specificity to task fragility:

| Freedom | When | Example |
|---------|------|---------|
| **High** | Multiple valid approaches, context-dependent | Code review guidelines |
| **Medium** | Preferred pattern exists, some variation OK | Report templates with customizable sections |
| **Low** | Fragile/error-prone, consistency critical | DB migration scripts—exact command, no flags |

**Analogy:** Narrow bridge with cliffs = low freedom (exact guardrails). Open field = high freedom (general direction).

---

## 5. Writing Effective Descriptions

The description is **the** triggering mechanism. Claude uses it to select from 100+ skills.

### Rules

1. **Third person always** — "Processes Excel files" not "I can help you" or "You can use this"
2. **Specific + trigger phrases** — Include what it does AND when to invoke
3. **Key terms for discovery** — Use synonyms user might say

### Examples

```yaml
# GOOD - specific, includes triggers
description: >-
  Analyze Excel spreadsheets, create pivot tables, generate charts.
  Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.

# GOOD - action + context
description: >-
  Generate descriptive commit messages by analyzing git diffs.
  Use when user asks for help writing commit messages or reviewing staged changes.

# BAD - vague
description: Helps with documents
description: Processes data
description: Does stuff with files
```

---

## 6. Naming Conventions

**Prefer gerund form** (verb + -ing): clearly describes activity.

```
✓ processing-pdfs
✓ analyzing-spreadsheets
✓ testing-code
✓ managing-databases

✗ helper, utils, tools (vague)
✗ documents, data, files (generic)
✗ anthropic-helper, claude-tools (reserved)
```

Acceptable alternatives: noun phrases (`pdf-processing`), action-oriented (`process-pdfs`).

---

## 7. Bundled Resources

### scripts/ — Executable Code

**When:** Same code rewritten repeatedly, deterministic reliability needed.

```
scripts/
├── rotate_pdf.py
├── validate_form.py
└── extract_text.py
```

**Benefits:**
- Token efficient (executed without loading)
- Deterministic (no generation variance)
- Consistent across uses

**In SKILL.md, distinguish intent:**
```markdown
# Execute (most common)
Run `python scripts/validate.py input.pdf`

# Read as reference (rare, for complex logic)
See `scripts/validate.py` for the validation algorithm
```

### references/ — Context-Loaded Documentation

**When:** Documentation Claude should reference while working.

```
references/
├── schema.md       # Database schemas
├── api.md          # API specifications
├── policies.md     # Company rules
└── patterns.md     # Domain patterns
```

**Design pattern for multi-domain:**
```markdown
# In SKILL.md
## Available datasets
- **Finance**: Revenue, ARR → See [references/finance.md](references/finance.md)
- **Sales**: Pipeline, accounts → See [references/sales.md](references/sales.md)

## Quick search
```bash
grep -i "revenue" references/finance.md
```
```

**Large files (>10k words):** Include grep patterns in SKILL.md for targeted access.

### assets/ — Output Files (Not Loaded)

**When:** Files used in output, not instruction context.

```
assets/
├── logo.png
├── template.pptx
├── font.ttf
└── boilerplate/
```

Claude references by path, copies/modifies—never loads into context.

---

## 8. Workflow Patterns

### Checklist Pattern (Complex Multi-Step)

```markdown
## Form filling workflow

Copy and track progress:
```
- [ ] Step 1: Analyze form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

**Step 1: Analyze the form**
Run: `python scripts/analyze_form.py input.pdf`
```

### Feedback Loop Pattern (Quality-Critical)

```markdown
## Validation loop

1. Make edits to document
2. **Validate immediately**: `python scripts/validate.py output/`
3. If validation fails:
   - Review error message
   - Fix issues
   - Run validation again
4. **Only proceed when validation passes**
```

### Conditional Workflow Pattern

```markdown
## Document modification

1. Determine type:
   - **Creating new?** → Follow "Creation workflow"
   - **Editing existing?** → Follow "Editing workflow"

2. Creation workflow:
   - Use docx-js library
   - Build from scratch

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
```

### Template Pattern

```markdown
## Report structure

ALWAYS use this template:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview]

## Key findings
- Finding 1 with data
- Finding 2 with data

## Recommendations
1. Actionable recommendation
```
```

---

## 9. Anti-Patterns (Avoid)

### Don't Include
- README.md, CHANGELOG.md, INSTALLATION_GUIDE.md
- User-facing documentation
- Setup/testing procedures
- Auxiliary context about creation process

Skills are **for AI agents**, not humans.

### Don't Do

| Anti-Pattern | Why Bad | Fix |
|-------------|---------|-----|
| Windows paths (`scripts\helper.py`) | Breaks on Unix | Use forward slashes |
| Deeply nested references | Claude partial-reads | One level deep only |
| Time-sensitive info | Becomes wrong | Use "old patterns" section |
| Too many options | Confusing | Provide default + escape hatch |
| Vague descriptions | Never triggers | Specific + trigger phrases |
| Inconsistent terminology | Confuses Claude | Pick one term, use throughout |
| Magic numbers | Unverifiable | Document why each value |
| Error punt to Claude | Unreliable | Handle explicitly in scripts |

### Bad: Multiple Options Without Default
```markdown
# BAD
"You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image..."

# GOOD
"Use pdfplumber for text extraction:
[code]
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
```

---

## 10. Security & Permissions

### Tool Scoping

```yaml
allowed-tools: Read,Write,Bash(git:*)
```

**Principle of least privilege:** Only include tools the skill actually needs. `Bash(pdftotext:*)` not `Bash(*)`.

### Path Portability

```markdown
# GOOD - portable
{baseDir}/scripts/validate.py

# BAD - hardcoded
/Users/alice/skills/pdf/scripts/validate.py
```

`{baseDir}` auto-resolves to skill installation directory.

---

## 11. Testing & Iteration

### Development Process

1. **Complete task without skill** — Note what context you repeatedly provide
2. **Identify reusable pattern** — What would help future similar tasks?
3. **Create minimal skill** — Just enough to address gaps
4. **Test with fresh Claude instance** — Does it find right info? Apply rules correctly?
5. **Iterate based on observation** — What did it miss? What confused it?

### Testing Checklist

```
□ Description triggers on expected phrases
□ Description doesn't trigger on unrelated requests
□ Works with Haiku (needs more guidance?)
□ Works with Opus (over-explained?)
□ Scripts execute without error
□ Reference files load when expected
□ Validation loops catch errors
□ Real-world usage scenarios pass
```

### Evaluation Structure

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF and save to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Reads PDF using appropriate library",
    "Extracts text from all pages",
    "Saves to output.txt in readable format"
  ]
}
```

---

## 12. Organization Patterns by Complexity

### Simple Skill (Single Task)

```
image-rotate/
├── SKILL.md
└── scripts/
    └── rotate.py
```

### Medium Skill (Multiple Features)

```
pdf-processing/
├── SKILL.md
├── scripts/
│   ├── extract_text.py
│   ├── fill_form.py
│   └── validate.py
└── references/
    ├── FORMS.md
    └── API.md
```

### Complex Skill (Multi-Domain)

```
bigquery-analysis/
├── SKILL.md                    # Overview + domain selection
├── scripts/
│   └── query_runner.py
└── references/
    ├── finance.md              # Revenue, ARR, billing
    ├── sales.md                # Pipeline, opportunities
    ├── product.md              # Usage, features
    └── marketing.md            # Campaigns, attribution
```

---

## 13. Frontmatter Optional Fields

Beyond required `name`/`description`:

| Field | Effect |
|-------|--------|
| `allowed-tools` | Scoped permissions (e.g., `Read,Write,Bash(git:*)`) |
| `model` | Override session model (`inherit` = use current) |
| `user-invocable: false` | Hide from slash menu, allow programmatic only |
| `mode: true` | Categorize as "Mode Command" |

---

## 14. MCP Tool References

When using MCP tools, **always use fully qualified names**:

```markdown
# GOOD
Use the BigQuery:bigquery_schema tool to retrieve schemas.

# BAD - may fail
Use the bigquery_schema tool...
```

Format: `ServerName:tool_name`

---

## 15. Content Guidelines

### Consistent Terminology

Pick one term, use it everywhere:

```
✓ Always "API endpoint" (not "URL", "route", "path")
✓ Always "field" (not "box", "element", "control")
✓ Always "extract" (not "pull", "get", "retrieve")
```

### Time-Sensitive Information

```markdown
# BAD
If before August 2025, use old API. After August 2025, use new API.

# GOOD
## Current method
Use v2 API: `api.example.com/v2/messages`

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>
The v1 API used: `api.example.com/v1/messages`
No longer supported.
</details>
```

### Examples Over Explanations

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed date display bug in reports
Output:
```
fix(reports): correct date formatting in timezone conversion
```

Follow this style: type(scope): brief description, then details.
```

---

## 16. Quick Reference Card

```
SKILL CHECKLIST
═══════════════════════════════════════════════════════════════

□ name: lowercase, hyphens, ≤64 chars
□ description: third person, specific triggers, ≤1024 chars
□ SKILL.md body: <500 lines
□ References: one level deep from SKILL.md
□ Long refs: include TOC
□ Scripts: tested, explicit error handling
□ No magic numbers (all values justified)
□ Forward slashes only (no Windows paths)
□ No extraneous docs (README, CHANGELOG, etc.)
□ Consistent terminology throughout
□ Examples concrete, not abstract
□ Tested with real usage scenarios

DESCRIPTION TEMPLATE
═══════════════════════════════════════════════════════════════
description: >-
  [What it does - actions, capabilities].
  Use when [trigger phrases, contexts, file types, user intents].

PROGRESSIVE DISCLOSURE TEMPLATE
═══════════════════════════════════════════════════════════════
## Quick start
[Essential example - <50 lines]

## Features
- **Feature A**: See [A.md](references/A.md)
- **Feature B**: See [B.md](references/B.md)

## Quick search
```bash
grep -i "keyword" references/
```
```

---

---

## 17. Advanced Patterns from Production Skills

Learnings from real-world skill collections (Dicklesworthstone's Agent Flywheel stack):

### 17.1 "THE EXACT PROMPT" Pattern

Encode reproducible prompts in all-caps sections for agent-to-agent handoff:

```markdown
## THE EXACT PROMPT — Plan Review

```
Carefully review this entire plan for me and come up with your best
revisions in terms of better architecture, new features...
```
```

**Why it works:**
- Prompts are copy-paste ready
- Stream Deck / automation friendly
- No ambiguity about phrasing
- Enables cross-model workflows (GPT Pro → Claude Code)

### 17.2 "Why This Exists" Section

Front-load motivation before instructions:

```markdown
## Why This Exists

Managing multiple AI coding agents is painful:
- **Window chaos**: Each agent needs its own terminal
- **Context switching**: Jumping between windows breaks flow
- **No orchestration**: Same prompt to multiple agents = manual copy-paste

NTM solves all of this...
```

Helps Claude understand when to apply the skill contextually.

### 17.3 Integration Sections

Complex tools should document ecosystem connections:

```markdown
## Integration with Flywheel

| Tool | Integration |
|------|-------------|
| **Agent Mail** | Message routing, file reservations |
| **BV** | Work distribution, triage |
| **CASS** | Search past sessions |
| **DCG** | Safety system integration |
```

### 17.4 Risk Tiering Tables

For safety/security skills, use explicit tier classifications:

```markdown
| Tier | Approvals | Auto-approve | Examples |
|------|-----------|--------------|----------|
| **CRITICAL** | 2+ | Never | `rm -rf /`, `DROP DATABASE` |
| **DANGEROUS** | 1 | Never | `git reset --hard` |
| **CAUTION** | 0 | After 30s | `rm file.txt` |
| **SAFE** | 0 | Immediately | `rm *.log` |
```

### 17.5 Robot Mode / Machine-Readable Output

For orchestration tools, document JSON/NDJSON APIs:

```markdown
## Robot Mode (AI Automation)

```bash
ntm --robot-status              # Sessions, panes, agent states
ntm --robot-snapshot            # Unified state: sessions + beads + mail
```

Output format:
```json
{"type":"request_pending","request_id":"abc123","tier":"dangerous"}
```
```

### 17.6 Exit Code Standardization

```markdown
## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error |
| `2` | Invalid arguments / Unavailable |
| `3` | Not found |
| `4` | Permission denied |
| `5` | Timeout |
```

### 17.7 ASCII State Diagrams

Visualize complex flows:

```markdown
### Processing Pipeline

```
┌─────────────────┐
│   Claude Code   │  Agent executes command
└────────┬────────┘
         │
         ▼ PreToolUse hook (stdin: JSON)
┌─────────────────┐
│      dcg        │
│  ┌──────────┐   │
│  │  Parse   │──▶│ Normalize ──▶ Quick Reject
│  └──────────┘   │
└────────┬────────┘
         │
         ▼ stdout: JSON (deny) or empty (allow)
```
```

### 17.8 Hierarchical Configuration Documentation

```markdown
## Configuration

Configuration precedence (lowest to highest):
1. Built-in defaults
2. User config (`~/.config/tool/config.toml`)
3. Project config (`.tool/config.toml`)
4. Environment variables (`TOOL_*`)
5. Command-line flags
```

### 17.9 "Use ultrathink" Convention

For complex prompts, append thinking mode instructions:

```markdown
...hyper-optimize for both separately to play to the specifics of
each modality. Use ultrathink.
```

Signals to Claude to use extended thinking for thorough analysis.

### 17.10 Iteration Protocols

For refinement workflows, specify iteration counts:

```markdown
### Repeat Until Steady-State

- Start fresh conversations for each round
- After 4-5 rounds, suggestions become very incremental
- This phase can take 2-3 hours for complex features — this is normal
```

---

## 18. Common Skill Archetypes

### 18.1 CLI Reference Skill (github, gcloud, vercel)

**Structure:**
```markdown
# Tool Name Skill

## Authentication
[auth commands]

## Core Operations
[main commands grouped by function]

## Common Workflows
[multi-step recipes]
```

**Token efficiency:** Pure reference, minimal prose. Claude already knows CLI semantics.

### 18.2 Methodology Skill (planning-workflow, de-slopify)

**Structure:**
```markdown
# Methodology Name

> **Core Philosophy:** [one-liner insight]

## Why This Matters
[brief motivation]

## THE EXACT PROMPT
[copy-paste ready prompt]

## Why This Prompt Works
[technical breakdown]

## Before/After Examples
[concrete demonstrations]
```

### 18.3 Safety Tool Skill (dcg, slb)

**Structure:**
```markdown
# Tool Name

## Why This Exists
[threat model]

## Critical Design Principles
[architecture decisions]

## What It Blocks / Allows
[tables of patterns]

## Modular System
[extensibility]

## Security Considerations
[limitations, threat model assumptions]
```

### 18.4 Orchestration Tool Skill (ntm, agent-mail)

**Structure:**
```markdown
# Tool Name

## Why This Exists
[pain points solved]

## Quick Start
[minimal viable usage]

## Core Commands
[organized by function]

## Robot Mode
[machine-readable APIs]

## Integration with Ecosystem
[connections to other tools]
```

---

## Sources

- [Skill Authoring Best Practices - Anthropic Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Agent Skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [anthropics/skills Repository](https://github.com/anthropics/skills)
- [Claude Skills Deep Dive - Lee Han Chung](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Claude Code Customization Guide - alexop.dev](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/)
- [Claude Skills & CLAUDE.md Guide - gend.co](https://www.gend.co/blog/claude-skills-claude-md-guide)
- Dicklesworthstone Agent Flywheel Skills Collection (real-world patterns)
