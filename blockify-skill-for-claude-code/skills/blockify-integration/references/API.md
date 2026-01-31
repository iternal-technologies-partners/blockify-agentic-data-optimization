# Blockify API Quick Reference

## Endpoint

```
POST https://api.blockify.ai/v1/chat/completions
```

## Authentication

```
Authorization: Bearer blk_your_api_key_here
Content-Type: application/json
```

## Models

| Model | Use Case |
|-------|----------|
| `ingest` | Raw text to IdeaBlocks |
| `distill` | Merge similar IdeaBlocks |
| `technical-ingest` | Ordered content (manuals) |

## Request Format

```json
{
  "model": "ingest",
  "messages": [{"role": "user", "content": "your text"}],
  "max_tokens": 8000,
  "temperature": 0.5
}
```

## Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| max_tokens | 8000+ | Minimum for full output |
| temperature | 0.5 | Don't change |
| chunk_size | 2000 chars | Recommended for ingest |

## Rate Limits

- Free: 10 req/min, 100/day
- Starter: 60 req/min, 1000/day
- Pro: 300 req/min, 10000/day
- Enterprise: Custom

## Full Documentation

See `./blockify-agentic-data-optimization/documentation`
