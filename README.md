# Blockify Insights Documentation

Sign up for Blockify Enterprise and receive $1,000 in free Blockify Token Credits: [console.blockify.ai/signup](https://console.blockify.ai/signup)

**Purpose:** Comprehensive technical documentation for engineers integrating Blockify with Claude Code, Clawdbot, and RAG systems.

**Created:** 2026-01-25
**Last Updated:** 2026-01-25

---

## Documentation Index

| Document | Description | Audience |
|----------|-------------|----------|
| [BLOCKIFY-DEEP-DIVE.md](./documentation/BLOCKIFY-DEEP-DIVE.md) | Complete technical understanding of Blockify | All Engineers |
| [IDEABLOCK-STRUCTURE.md](./documentation/IDEABLOCK-STRUCTURE.md) | IdeaBlock XML format specification | Data Engineers |
| [BLOCKIFY-API-REFERENCE.md](./documentation/BLOCKIFY-API-REFERENCE.md) | API documentation with examples | Backend Engineers |
| [LOCAL-VECTOR-DATABASE-SETUP.md](./documentation/LOCAL-VECTOR-DATABASE-SETUP.md) | ChromaDB setup for 100k+ blocks | DevOps/Data Engineers |
| [DISTILLATION-SERVICE.md](./documentation/DISTILLATION-SERVICE.md) | Auto-dedupe server for large-scale deduplication | Platform Engineers |
| [CLAUDE-CODE-BLOCKIFY-SKILL.md](./documentation/CLAUDE-CODE-BLOCKIFY-SKILL.md) | Claude Code skill for Blockify integration | Claude Code Users |
| [ARCHITECTURE-END-TO-END.md](./documentation/ARCHITECTURE-END-TO-END.md) | Complete integration architecture | Architects |
| [CLAWDBOT-RAG-INTEGRATION.md](./documentation/CLAWDBOT-RAG-INTEGRATION.md) | Clawdbot + Blockify RAG implementation | Full-Stack Engineers |
| [GETTING-STARTED-GUIDE.md](./documentation/GETTING-STARTED-GUIDE.md) | Step-by-step setup for any skill level | All Engineers |
| [RAG-AGENTIC-SEARCH-RESEARCH.md](./documentation/RAG-AGENTIC-SEARCH-RESEARCH.md) | RAG architecture patterns research | All Engineers |

---

## Quick Start

### What is Blockify?

Blockify is a **patented data ingestion, distillation, and governance platform** that transforms messy enterprise content into compact, validated "IdeaBlocks" - structured knowledge units optimized for AI/LLM applications.

### Key Performance Metrics

| Metric | Improvement |
|--------|-------------|
| **Aggregate Enterprise Performance** | Up to 78X |
| **Vector Search Accuracy** | 2.29X |
| **Information Distillation** | 29.93X |
| **Token Efficiency** | 3.09X |
| **Dataset Size Reduction** | 40X (down to ~2.5% of original) |

### API Quick Test

```bash
curl --location 'https://api.blockify.ai/v1/chat/completions' \
--header 'Authorization: Bearer YOUR_API_KEY' \
--header 'Content-Type: application/json' \
--data '{
    "model": "ingest",
    "messages": [{"role": "user", "content": "Your text to process here"}],
    "max_tokens": 8000,
    "temperature": 0.5
}'
```

### Available Models

| Model | API Name | Use Case |
|-------|----------|----------|
| Blockify Ingest | `ingest` | Convert raw text to IdeaBlocks |
| Blockify Distill | `distill` | Merge/deduplicate similar IdeaBlocks |
| Technical Manual Ingest | `technical-ingest` | Ordered content (manuals, procedures) |

---

## Integration Patterns

### For Claude Code

Use the Claude Code skill in [blockify-skill-for-claude-code](./blockify-skill-for-claude-code/) to:
- Process project documentation into IdeaBlocks
- Create optimized knowledge bases for RAG
- Improve codebase context retrieval

### For Clawdbot (Website Chatbot)

Integrate Blockify-processed knowledge for:
- 78X more accurate responses
- Reduced hallucination risk
- Better product knowledge retrieval

### For Enterprise RAG Systems

Blockify sits between document parsing and vector storage:

```
[Documents] --> [Parser] --> [Blockify] --> [Vector DB] --> [LLM]
```

---

## Related Documentation

- [RAG-AGENTIC-SEARCH-RESEARCH.md](./documentation/RAG-AGENTIC-SEARCH-RESEARCH.md) - RAG architecture research
- [blockify-distillation-service](./blockify-distillation-service/) - Distillation service implementation
- [blockify-skill-for-claude-code](./blockify-skill-for-claude-code/) - Claude Code skill package

---

## Support

- **Enterprise Sales:** sales@iternal.ai
- **Technical Support:** support@iternal.ai
- **Website:** https://iternal.ai/blockify
- **Console:** https://console.blockify.ai

---

*Blockify, IdeaBlock, and AirgapAI are trademarks of Iternal Technologies.*
