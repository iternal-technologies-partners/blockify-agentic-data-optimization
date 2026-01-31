# IdeaBlock Structure Specification

**Document Purpose:** Complete technical specification of the IdeaBlock XML format for data engineers and developers.

---

## Table of Contents

1. [Overview](#overview)
2. [IdeaBlock Schema](#ideablock-schema)
3. [Field Specifications](#field-specifications)
4. [Tag Taxonomy](#tag-taxonomy)
5. [Entity Types](#entity-types)
6. [Ordered Content (Technical Manual) Format](#ordered-content-technical-manual-format)
7. [Best Practices](#best-practices)
8. [Parsing Examples](#parsing-examples)

---

## Overview

An IdeaBlock is a structured XML representation of a single, self-contained piece of knowledge. It answers ONE critical question with a trusted answer, enhanced with metadata for governance, retrieval, and reasoning.

### Design Principles

1. **Semantic Completeness**: Each block contains all context needed to understand the answer
2. **Question-Answer Alignment**: Mirrors how users query AI systems
3. **Metadata Rich**: Enables filtering, permissions, and analytics
4. **Deduplication Ready**: Structure allows semantic similarity detection
5. **LLM Optimized**: Compact format minimizes token usage

---

## IdeaBlock Schema

### Standard IdeaBlock (Unordered Content)

```xml
<ideablock>
  <name>Descriptive Title</name>
  <critical_question>What specific question does this answer?</critical_question>
  <trusted_answer>The validated, accurate response in 2-3 sentences.</trusted_answer>
  <tags>TAG1, TAG2, TAG3</tags>
  <entity>
    <entity_name>ENTITY NAME</entity_name>
    <entity_type>ENTITY_TYPE</entity_type>
  </entity>
  <!-- Additional entities as needed -->
  <keywords>keyword1, keyword2, keyword3</keywords>
</ideablock>
```

### Real Example (API Output)

```xml
<ideablock>
  <name>Claude Code Overview</name>
  <critical_question>What is Claude Code?</critical_question>
  <trusted_answer>Claude Code is an AI-powered development tool that helps
    programmers write, debug, and optimize code. It offers intelligent code
    suggestions, automated testing, and context-aware assistance.</trusted_answer>
  <tags>IMPORTANT, PRODUCT FOCUS, INFORM (WITHOUT EMOTION), SIMPLE (OVERVIEW),
    INNOVATION, TECHNOLOGY</tags>
  <entity>
    <entity_name>CLAUDE CODE</entity_name>
    <entity_type>PRODUCT</entity_type>
  </entity>
  <keywords>Claude Code, AI, Development Tool, Code, Intelligent Code
    Suggestions, Automated Testing, Context-Aware Assistance</keywords>
</ideablock>
```

---

## Field Specifications

### name

| Attribute | Value |
|-----------|-------|
| **Required** | Yes |
| **Type** | String |
| **Max Length** | 100 characters (recommended) |
| **Format** | Title Case, descriptive |
| **Purpose** | Human-readable identifier for the knowledge block |

**Guidelines:**
- Should be clear and searchable
- Avoid abbreviations unless universally understood
- Should indicate what the block is about

**Examples:**
- "Blockify's Performance Improvement"
- "Enterprise Data Duplication Factor"
- "Claude Code Integration with IDEs"

### critical_question

| Attribute | Value |
|-----------|-------|
| **Required** | Yes |
| **Type** | String |
| **Max Length** | 200 characters (recommended) |
| **Format** | Complete question ending with "?" |
| **Purpose** | The question this knowledge answers |

**Guidelines:**
- Must be a complete, grammatically correct question
- Should be specific and answerable
- Matches how users naturally query

**Examples:**
- "What is Claude Code?"
- "How does Blockify's distillation approach compare to traditional chunking methods?"
- "What is the projected aggregate Enterprise Performance improvement?"

### trusted_answer

| Attribute | Value |
|-----------|-------|
| **Required** | Yes |
| **Type** | String |
| **Max Length** | 500 characters (recommended) |
| **Format** | 2-3 complete sentences |
| **Purpose** | The validated, accurate response |

**Guidelines:**
- Should directly answer the critical_question
- Must be factually accurate (99% lossless)
- Concise but complete
- No speculation or marketing fluff

**Examples:**
- "Blockify's distillation approach is projected to achieve an aggregate Enterprise Performance improvement of 68.44X for Big Four Consulting Firm."
- "The average Enterprise Data Duplication Factor is 15:1, accounting for typical data redundancy across multiple documents and systems in an enterprise setting."

### tags

| Attribute | Value |
|-----------|-------|
| **Required** | Yes |
| **Type** | Comma-separated list |
| **Max Tags** | 10 (recommended) |
| **Format** | UPPERCASE |
| **Purpose** | Classification, filtering, governance |

**Guidelines:**
- Use standardized tag taxonomy (see below)
- Include both content and style tags
- Multiple tags are normal and expected

### entity

| Attribute | Value |
|-----------|-------|
| **Required** | No (but recommended) |
| **Type** | Nested XML elements |
| **Max Entities** | Unlimited |
| **Purpose** | Named entity recognition for knowledge graphs |

**Structure:**
```xml
<entity>
  <entity_name>ENTITY NAME</entity_name>
  <entity_type>ENTITY_TYPE</entity_type>
</entity>
```

**Guidelines:**
- entity_name should be UPPERCASE
- entity_type should match the taxonomy (see below)
- Multiple entities per IdeaBlock is common

### keywords

| Attribute | Value |
|-----------|-------|
| **Required** | Yes |
| **Type** | Comma-separated list |
| **Max Keywords** | 10-15 (recommended) |
| **Format** | Mixed case, searchable terms |
| **Purpose** | Enhanced retrieval, BM25 search |

**Guidelines:**
- Include the main subject
- Include related terms and synonyms
- Include specific numbers/values mentioned
- Include product/company names

---

## Tag Taxonomy

### Content Classification Tags

| Tag | Description |
|-----|-------------|
| `IMPORTANT` | Critical information, should be prioritized |
| `PRODUCT FOCUS` | About a specific product |
| `COMPANY FOCUS` | About a company/organization |
| `PROCESS` | Describes a procedure or workflow |
| `TECHNOLOGY` | Technical topic |
| `PERFORMANCE` | Performance metrics or improvements |
| `GROWTH` | Growth-related information |
| `INVESTMENT` | Financial or investment related |
| `COMPARISON` | Comparing two or more things |
| `ANALYSIS` | Analytical content |
| `STUDY` | Research or study findings |
| `RESEARCH` | Research-based information |
| `DATA MANAGEMENT` | Data handling topics |
| `INTEGRATION` | System integration topics |
| `AI` | Artificial intelligence related |
| `INNOVATION` | Innovative technologies/approaches |

### Style Tags

| Tag | Description |
|-----|-------------|
| `INFORM (WITHOUT EMOTION)` | Neutral, factual tone |
| `SIMPLE (OVERVIEW)` | High-level, accessible |
| `DETAILED` | In-depth technical content |
| `WARNING` | Contains cautions or warnings |
| `BEST PRACTICE` | Recommended approaches |

---

## Entity Types

### Standard Entity Types

| Type | Use For | Examples |
|------|---------|----------|
| `PRODUCT` | Products, tools, software | BLOCKIFY, CLAUDE CODE, AIRGAPAI |
| `ORGANIZATION` | Companies, agencies | ITERNAL TECHNOLOGIES, BIG FOUR CONSULTING FIRM |
| `PERSON` | Individuals | JOHN SMITH, CEO NAME |
| `METRIC` | Measurements, KPIs | 68.44X, 78X IMPROVEMENT |
| `TECHNOLOGY` | Technologies, frameworks | LLAMA 3.2, VECTOR DATABASE |
| `CONCEPT` | Abstract concepts | ENTERPRISE DISTILLATION, RAG |
| `LOCATION` | Geographic locations | UNITED STATES, CLOUD |
| `DATE` | Time references | FY24, 2026 |
| `OTHER` | Catch-all for unclassified | ENTERPRISE CONTENT LIFECYCLE |

### Entity Extraction Rules

1. Extract ALL named entities from the trusted_answer
2. Use UPPERCASE for entity_name
3. Choose the most specific entity_type
4. Include key metrics as entities
5. Include product and company names

---

## Ordered Content (Technical Manual) Format

For technical manuals and procedures, use the `technical-ingest` model with a special input format.

### Input Structure

```json
"### Primary ###
---
[The main content that you want to Blockify goes here.]
---
### Proceeding ###
---
[The section that comes before the Primary Section goes here.]
---
### Following ###
---
[The section that comes after the Primary Section goes here.]"
```

### Output Structure (Technical Manual IdeaBlock)

```xml
<Manual>
  <OneSentenceSummary>Brief summary of the entire section.</OneSentenceSummary>

  <OneParagraphSummary>Detailed summary explaining the full context.</OneParagraphSummary>

  <Sections>
    <Section>
      <Heading>Section Title</Heading>

      <OneSentenceSummary>Section-level summary.</OneSentenceSummary>

      <OneParagraphSummary>Detailed section summary.</OneParagraphSummary>

      <UserQuestions>
        <UserQuestion1>Common question 1?</UserQuestion1>
        <UserQuestion2>Common question 2?</UserQuestion2>
        <!-- Up to 5 questions -->
      </UserQuestions>

      <FullText>The original text content preserved.</FullText>

      <Procedures>
        <!-- If procedures exist -->
      </Procedures>

      <Sentences>
        <Sentence id="S1" role="INFO">First sentence.</Sentence>
        <Sentence id="S2" role="PREREQUISITE">Prerequisite info.</Sentence>
        <Sentence id="S3" role="COMMAND">Command or action.</Sentence>
        <Sentence id="S4" role="WARNING">Warning message.</Sentence>
        <!-- More sentences with roles -->
      </Sentences>
    </Section>
  </Sections>
</Manual>
```

### Sentence Roles

| Role | Description |
|------|-------------|
| `INFO` | General information |
| `PREREQUISITE` | Required before proceeding |
| `COMMAND` | Action to take |
| `WARNING` | Caution or warning |
| `REFERENCE` | Points to other documentation |
| `RESULT` | Expected outcome |

---

## Best Practices

### 1. Chunk Size Before Processing

```
RECOMMENDED CHUNK SIZES:
─────────────────────────

General Content:      1,000 - 4,000 characters
                      (2,000 recommended default)

Technical Docs:       4,000 characters
                      (more context needed)

Meeting Transcripts:  4,000 characters
                      (conversational flow)
```

### 2. Chunking Guidelines

- Split at paragraph, sentence, or section boundaries
- NEVER split mid-sentence
- Include 10% overlap on chunk boundaries
- Keep chunks similar in size

### 3. Processing Pipeline

```
[Raw Document]
     |
     v
[Parse to Text] --> Use quality parser (Unstructured.io, Textract)
     |
     v
[Chunk] --> 2,000 char chunks, split at sentences
     |
     v
[Blockify Ingest] --> One API call per chunk
     |
     v
[Collect IdeaBlocks]
     |
     v
[Semantic Clustering] --> Group similar blocks
     |
     v
[Blockify Distill] --> 2-15 blocks per call
     |
     v
[Final IdeaBlocks]
```

### 4. Quality Validation

- Human review is recommended
- Check numerical accuracy (99% lossless target)
- Verify entity extraction
- Validate tag appropriateness
- Test retrieval with sample queries

### 5. Token Optimization

| Configuration | Value |
|---------------|-------|
| max_tokens | 8000+ |
| temperature | 0.5 |
| Input chunk | 1000-4000 chars |
| Expected output | ~1300 tokens/IdeaBlock |

---

## Parsing Examples

### Python XML Parsing

```python
import xml.etree.ElementTree as ET

def parse_ideablock(xml_string):
    """Parse IdeaBlock XML into structured dict."""
    root = ET.fromstring(xml_string)

    ideablock = {
        'name': root.find('name').text,
        'critical_question': root.find('critical_question').text,
        'trusted_answer': root.find('trusted_answer').text,
        'tags': [t.strip() for t in root.find('tags').text.split(',')],
        'entities': [],
        'keywords': [k.strip() for k in root.find('keywords').text.split(',')]
    }

    for entity in root.findall('entity'):
        ideablock['entities'].append({
            'name': entity.find('entity_name').text,
            'type': entity.find('entity_type').text
        })

    return ideablock

# Usage
xml_response = """<ideablock>
  <name>Claude Code Overview</name>
  <critical_question>What is Claude Code?</critical_question>
  <trusted_answer>Claude Code is an AI-powered development tool.</trusted_answer>
  <tags>IMPORTANT, TECHNOLOGY</tags>
  <entity>
    <entity_name>CLAUDE CODE</entity_name>
    <entity_type>PRODUCT</entity_type>
  </entity>
  <keywords>Claude Code, AI, Development</keywords>
</ideablock>"""

block = parse_ideablock(xml_response)
print(block['name'])  # "Claude Code Overview"
```

### JavaScript XML Parsing

```javascript
function parseIdeaBlock(xmlString) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(xmlString, 'text/xml');

  const block = {
    name: doc.querySelector('name')?.textContent,
    critical_question: doc.querySelector('critical_question')?.textContent,
    trusted_answer: doc.querySelector('trusted_answer')?.textContent,
    tags: doc.querySelector('tags')?.textContent.split(',').map(t => t.trim()),
    entities: [],
    keywords: doc.querySelector('keywords')?.textContent.split(',').map(k => k.trim())
  };

  doc.querySelectorAll('entity').forEach(entity => {
    block.entities.push({
      name: entity.querySelector('entity_name')?.textContent,
      type: entity.querySelector('entity_type')?.textContent
    });
  });

  return block;
}
```

### Regex Extraction (Fallback)

```python
import re

def extract_ideablock_fields(xml_string):
    """Quick regex extraction when full parsing isn't needed."""
    patterns = {
        'name': r'<name>(.*?)</name>',
        'question': r'<critical_question>(.*?)</critical_question>',
        'answer': r'<trusted_answer>(.*?)</trusted_answer>',
        'tags': r'<tags>(.*?)</tags>',
        'keywords': r'<keywords>(.*?)</keywords>'
    }

    return {
        key: re.search(pattern, xml_string, re.DOTALL).group(1).strip()
        for key, pattern in patterns.items()
        if re.search(pattern, xml_string, re.DOTALL)
    }
```

---

## Vector Database Schema

When storing IdeaBlocks in a vector database:

```json
{
  "id": "ideablock_uuid",
  "vector": [0.123, 0.456, ...],  // Embedding of trusted_answer
  "metadata": {
    "name": "Claude Code Overview",
    "critical_question": "What is Claude Code?",
    "trusted_answer": "Claude Code is an AI-powered...",
    "tags": ["IMPORTANT", "TECHNOLOGY"],
    "entities": [
      {"name": "CLAUDE CODE", "type": "PRODUCT"}
    ],
    "keywords": ["Claude Code", "AI", "Development"],
    "source_document": "claude-code-docs.pdf",
    "created_at": "2026-01-25T00:00:00Z",
    "version": "1.0"
  }
}
```

---

*Document created: 2026-01-25*
*Based on: Blockify API Documentation, API response analysis*
