# IdeaBlock Schema Reference

## Standard IdeaBlock (XML)

```xml
<ideablock>
  <name>Descriptive Title</name>
  <critical_question>What question does this answer?</critical_question>
  <trusted_answer>The validated answer (2-3 sentences).</trusted_answer>
  <tags>TAG1, TAG2, TAG3</tags>
  <entity>
    <entity_name>ENTITY NAME</entity_name>
    <entity_type>ENTITY_TYPE</entity_type>
  </entity>
  <keywords>keyword1, keyword2, keyword3</keywords>
</ideablock>
```

## Field Specifications

| Field | Required | Max Length | Description |
|-------|----------|------------|-------------|
| name | Yes | 100 chars | Title Case, searchable |
| critical_question | Yes | 200 chars | Complete question with ? |
| trusted_answer | Yes | 500 chars | 2-3 sentences, factual |
| tags | Yes | 10 tags | UPPERCASE, comma-separated |
| entity | No | Unlimited | Name + Type pairs |
| keywords | Yes | 15 words | Searchable terms |

## Entity Types

- PRODUCT
- ORGANIZATION
- PERSON
- METRIC
- TECHNOLOGY
- CONCEPT
- LOCATION
- DATE
- OTHER

## Common Tags

### Content Classification
IMPORTANT, PRODUCT FOCUS, COMPANY FOCUS, PROCESS, TECHNOLOGY, PERFORMANCE, COMPARISON, ANALYSIS

### Style Tags
INFORM (WITHOUT EMOTION), SIMPLE (OVERVIEW), DETAILED, WARNING, BEST PRACTICE

## Full Documentation

See `./blockify-agentic-data-optimization/documentation/IDEABLOCK-STRUCTURE.md`
