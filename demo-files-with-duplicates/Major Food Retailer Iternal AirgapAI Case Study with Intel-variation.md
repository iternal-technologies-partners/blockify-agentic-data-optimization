# Supporting Major Food Retailer Employee Operations through Improving LLM Accuracy by 78x with Blockify and AirgapAI

Artificial intelligence is rapidly becoming a strategic asset for major food retailers. To streamline operations and empower employees, a major food retailer must quickly enable thousands of employees with HR onboarding policies and procedures that feel individually tailored yet remain fully compliant with company policies and state labor laws across 9 states and 443 stores in the USA. 

Accelerating access to employee HR resources at scale requires instant access to the right information, at the right time, in a safe, secure, and trusted manner—while being certain each insight is factually correct and never exposes sensitive employee data. 

Intel and Iternal Technologies have partnered to provide a unique solution that addresses the most common challenges food retailers face when adopting AI technologies: hallucinations, data curation, governance, and ultra-granular access-control of confidential employee information. 

Pairing highly-performant data-center solutions like Gaudi 2 & Blockify® for data preparation and optimization, with edge-based Intel NPU chips & AirgapAI™ software for 100 percent local inference, delivers a major food retailer an end-to-end platform for hyper-personalized employee enablement; without ever letting sensitive data leave the corporate network.

# Blockify
## Enterprise Data Optimization for AI That Actually Works

---

## The Problem: Your AI Is Only as Good as Your Data

Enterprises are discovering a painful truth: **AI projects fail at the data layer, not the model layer.**

Gartner predicts that through 2026, organizations will abandon 60% of AI projects unsupported by AI-ready data. The reason is simple: when you dump millions of documents into a vector database and hope for the best, you get hallucinations, version conflicts, outdated information, and answers that can't be trusted.

The "dump-and-chunk" approach to RAG doesn't work:
- **Version conflicts**: Old pricing from FY21 mixed with current discounts from FY24
- **Stale content masquerading as fresh**: Someone opens a 3-year-old proposal, accidentally saves it, and now it has yesterday's date
- **Semantic fragmentation**: Fixed-length chunking splits critical information in half
- **Retrieval noise**: Near-duplicate passages crowd out relevant answers
- **Impossible maintenance**: Updating "paragraph 47 of document 59" across a million files takes tens of thousands of labor hours

**The result: AI that hallucinates, answers that can't be trusted, and projects that never reach production.**

---

## The Solution: Blockify Enterprise Data Optimization

Blockify is a **patented data ingestion, distillation, and governance platform** that transforms messy enterprise content into a compact, governed "golden dataset" of IdeaBlocks.

Instead of millions of unmanageable paragraphs, you get thousands of curated, validated, and permissioned knowledge blocks that power accurate AI responses.

**The numbers speak for themselves:**

| Metric | Improvement |
|--------|-------------|
| **Aggregate Enterprise Performance** | Up To 78X |
| **Vector Search Accuracy** | 2.29X |
| **Information Distillation** | 29.93X |
| **Token Efficiency** | 3.09X |
| **Dataset Size Reduction** | 40X (down to as low as ~2.5% of original) |

---

## How Blockify Works

### The IdeaBlock: Your New Unit of Knowledge

An IdeaBlock is the smallest unit of curated knowledge in your data taxonomy. Each block contains:

| Component | Description |
|-----------|-------------|
| **Descriptive Name** | Clear, searchable title for the concept |
| **Critical Question** | The question this knowledge answers |
| **Trusted Answer** | Validated, accurate response (2-3 sentences) |
| **Metadata Tags** | Clearance level, version, product line, NDA status |
| **Source Citation** | Link to original document for audit |

### The Processing Pipeline

| Step | What Happens |
|------|--------------|
| **1. Scoping** | Define index hierarchy (Org > Business Unit > Product > Persona) |
| **2. Ingestion** | Accept DOCX, PDF, PPT, PNG/JPG, Markdown, HTML |
| **3. Chunking & Extraction** | Context-aware splitting + fine-tuned LLM converts chunks to draft IdeaBlocks |
| **4. Semantic Deduplication** | Cluster near-duplicates, merge into canonical blocks, reduce by 40X |
| **5. Auto-Tagging** | Apply clearance, version, product, and permission labels |
| **6. Human Validation** | SMEs review thousands of blocks instead of millions of paragraphs |
| **7. Export** | Push to any vector DB or export as JSON-L for offline use |

---

## The Business Case: Why Legacy RAG Fails

### Financial Repercussions of Bad Data

| Scenario | Impact |
|----------|--------|
| **Mega-Bid Meltdown** | LLM mixes legacy pricing with current discounts; buyer disqualifies on compliance grounds. 18 months of pursuit costs written off. |
| **Warranty Cascade** | Chatbot generates BOM with obsolete component. Field failures trigger $47M recall. |
| **Regulatory Fine** | Hallucinated clinical-trial statistic leads to €5M EMA fine and forced product-labeling change. |

### Operational & Safety Risks

| Scenario | Impact |
|----------|--------|
| **Grounded Fleet** | Outdated torque value for helicopter rotor bolts propagates through RAG system. Emergency inspection of every aircraft required. |
| **Intelligence Failure** | Conflicting code names in separate PDFs confuse analyst's threat-brief. Security response delayed by hours. |

### The Root Causes

| Problem | Description |
|---------|-------------|
| **Accelerating Data Drift** | 5% change every 6 months means 1/3 of knowledge base is outdated within 3 years |
| **Content Proliferation** | Same paragraph lives in SharePoint, Jira, email chains, and vendor portals |
| **No Single Source of Truth** | No taxonomy linking key information to a master record |
| **Naïve Chunking** | Fixed-length windows destroy semantic coherence |
| **Vector Noise** | Near-duplicate paragraphs occupy adjacent positions, returning redundant passages |

---

## Performance Analysis: Real Customer Data

### Vector Search Accuracy Improvement

| Approach | Average Distance to Best Match | Improvement |
|----------|-------------------------------|-------------|
| **Legacy Chunking** | 0.3624 | Baseline |
| **Blockify (Undistilled)** | 0.1833 | 1.98X |
| **Blockify (Distilled)** | 0.1585 | 2.29X |

*Lower distance = higher accuracy. Blockify delivers 56% improvement in vector search precision.*

### Token Efficiency Impact

| Approach | Avg Tokens per Query | Annual Cost (1B queries) |
|----------|---------------------|--------------------------|
| **Legacy Chunking** | ~303 tokens/chunk | $1.09M |
| **Blockify Distilled** | ~98 tokens/block | $353K |
| **Savings** | 3.09X fewer tokens | **$738,000/year** |

### Data Reduction Analysis

| Metric | Original | Blockified | Reduction |
|--------|----------|------------|-----------|
| **Words** | 88,877 | 44,537 | 2.00X |
| **Characters** | 607,711 | 327,700 | 1.85X |
| **With Enterprise Duplication Factor (15X)** | - | - | **29.93X** |

---

## Platform Flexibility

Blockify integrates with your existing AI infrastructure:

### Supported Components

| Component | Options |
|-----------|---------|
| **Document Parsing** | Unstructured.io, AWS Textract, Google Gemini |
| **Embeddings** | OpenAI, AWS Bedrock, Mistral, Jina, open-source |
| **Vector Databases** | Azure AI Search, Pinecone, Milvus, Vertex Matching Engine |
| **LLM Runtime** | NVIDIA NIM, VLLM, Intel OpenVino |
| **Compute** | Intel Xeon (CPU), Intel Gaudi 2/3, NVIDIA GPU, AMD GPU |

### Architecture Patterns

| Workflow | Integration |
|----------|-------------|
| **Unstructured.io + Azure AI Search** | Parse with Unstructured > Blockify optimization > Azure vector store |
| **Gemini + Pinecone** | Gemini extraction > Blockify transformation > Pinecone similarity search |
| **Amazon Textract + Bedrock** | Textract parsing > Blockify preprocessing > Bedrock AI services |

Blockify sits between document parsing and vectorization—regardless of platform.

---

## The Governance Advantage

### Role-Based Data Permissioning

| Role | Data Access |
|------|-------------|
| **Sales** | Product specs, pricing, competitive intel |
| **Legal** | Contract templates, compliance requirements, NDA terms |
| **Engineering** | Technical specifications, API documentation, integration guides |
| **HR** | Policy documents, benefits information, hiring procedures |

*Different employees get different IdeaBlock datasets based on job role, responsibilities, and clearance.*

### Compliance-Ready Tags

| Tag Type | Examples |
|----------|----------|
| **Security Classification** | PUBLIC, INTERNAL, CONFIDENTIAL, SECRET |
| **Export Control** | ITAR, EAR, NATO-restricted, Five-Eyes-only |
| **Data Privacy** | PII-redacted, GDPR-compliant, HIPAA-safe |
| **Version Control** | Current, Deprecated, Draft, Approved |

---

## The Blockify Difference: Manageable at Scale

### Before: Impossible Human Maintenance

- 1 million documents across multiple repositories
- 5% change rate every 6 months = 50,000 documents to review
- Finding "paragraph 47 of document 59" across the enterprise: impossible
- Errors persist, compound, and poison AI outputs

### After: Quarterly Review in Hours

- 2,000-3,000 IdeaBlocks cover everything about a product/service
- Split blocks across 5-10 subject matter experts
- Each SME reviews their blocks in 1-2 hours per quarter
- Update one block > update every AI system that uses it

**Blockify makes human governance of enterprise AI data actually possible.**

---

## The Strategic Vision: From Documents to Data

### Today: Documents Are Source of Truth
- Files scattered across SharePoint, email, CRM, ERP
- Version conflicts everywhere
- No way to ensure AI gets the right information

### Tomorrow: IdeaBlocks Are Source of Truth
- Blocks become the "golden master record"
- Documents generated dynamically when needed
- AI always pulls from validated, current data
- "Fix once, publish everywhere" becomes reality

---

## Technical Specifications

| Specification | Detail |
|---------------|--------|
| **LLM Models Available** | LLAMA 3.2 (1B, 3B), LLAMA 3.1 (8B, 70B) |
| **Processing Modes** | Blockify Ingest (raw > IdeaBlocks), Blockify Distill (merge/dedupe) |
| **Input Size** | 1,000-4,000 characters (2,000 recommended) |
| **Data Fidelity** | ~99% lossless for numerical data, facts, key information |
| **Deployment Time** | 1.5 hours from zero to production (verified) |
| **API Format** | OpenAPI standard |
| **Output Options** | API push to vector DB, JSON-L export for offline |
| **Offline Capability** | Full offline operation with AirgapAI |

---

## Deployment Options

| Option | Description | Best For |
|--------|-------------|----------|
| **Cloud SaaS** | Hosted Blockify processing | Fast deployment, minimal IT overhead |
| **Private Cloud** | Blockify in customer's cloud environment | Data residency requirements |
| **On-Premises** | Full installation behind firewall | Classified/air-gapped environments |
| **Hybrid** | Cloud processing with on-prem storage | Balanced security and convenience |

---

## Implementation Journey

| Phase | Activities | Outcome |
|-------|------------|---------|
| **Discovery** | Identify priority document sources, define index hierarchy | Scoping document |
| **Ingestion** | Connect document sources, run initial processing | Draft IdeaBlocks |
| **Distillation** | Deduplicate, merge, optimize dataset | Reduced dataset |
| **Governance Setup** | Define roles, permissions, review workflows | Governed access model |
| **SME Validation** | Subject matter experts review and approve blocks | Production-ready dataset |
| **Integration** | Connect to vector DB and AI applications | Live RAG system |
| **Ongoing Cadence** | Quarterly review, continuous improvement | Maintained accuracy |

---

## Services Opportunities

| Service | Description |
|---------|-------------|
| **Data Strategy Consulting** | Design optimal taxonomy and index hierarchy |
| **Initial Blockification** | Process and optimize existing document corpus |
| **SME Training** | Train internal teams on block review and governance |
| **Custom Integration** | Connect Blockify to existing RAG infrastructure |
| **Ongoing Optimization** | Quarterly reviews, accuracy monitoring, updates |
| **AI Agent Development** | Build agentic applications powered by Blockified data |

---

## The Bottom Line

Blockify solves the fundamental problem killing enterprise AI projects: **data quality**.

| Challenge | Blockify Solution |
|-----------|------------------|
| **AI hallucinations** | Up to 78X accuracy improvement |
| **Unmanageable data** | 40X dataset reduction |
| **Impossible governance** | Human review in hours, not years |
| **Token costs** | 3.09X efficiency = $738K annual savings |
| **Version conflicts** | Single source of truth |
| **Compliance risks** | Role-based permissioning with audit trail |

**Blockify converts unreliable RAG prototypes into production-grade, trusted AI systems.**

---

*Blockify is developed by Iternal Technologies, powering enterprise AI for Fortune 500 companies, defense contractors, and government agencies worldwide.*

**Enterprise Sales**: sales@iternal.ai
**Website**: iternal.ai
**Technical Support**: support@iternal.ai

---

*Patents pending. Blockify, IdeaBlock, and AirgapAI are trademarks of Iternal Technologies.*


## **Why AI Inference Matters and Why You Should Care**

AI inference is more than processing a trained model; it goes beyond simple data entry and policy lookups. It empowers the Major Food Retailer's HR and Training teams to extract real-time, accurate, and contextually relevant insights from training manuals, onboarding policies, and performance reviews at scale.

Traditional HR systems require manual searches and generic responses. Without an effective AI-driven content lifecycle, the Major Food Retailer risks providing information that feels irrelevant or, worse, inadvertently revealing private employee details. Garbage in, garbage out \- and if you can’t trust your AI to be correct every time, you can’t trust it at all because the mistakes are unpredictable.

![][image1]

Intel and Iternal used AI to bring structure to unstructured HR artifacts, employee handbooks, benefits summaries, health and safety guidelines, store opening procedures, and vacation policies; through an advanced data-ingestion and optimization approach powered by Blockify.

![][image2]

The result is a highly accurate and optimized dataset that includes greater governance, control, management, and quality of data while simplifying human oversight. These improvements virtually eliminate AI hallucinations in Retrieval-Augmented Generation (RAG) workflows and improve LLM accuracy by approximately 78x (7,800 percent) compared to a traditional RAG pipeline.

![][image3]

Blockify’s patented approach creates a single source of truth. Distilling The Retailer's accumulated institutional knowledge down to 2.5 percent of the original size allows for easy content-lifecycle management.

## **A Summary of the AI Inference Solution**

### Blockify Data Ingestion with Gaudi

Leveraging Intel Gaudi 2 AI accelerators and Iternal’s patented Blockify solution, The Retailer's HR team ingests and optimizes thousands of documents for an improved LLM inferencing pipeline paired with RAG.

* Processing Time: Vector search and inference is approximately 2.2x faster using Intel NPU.  
* Accuracy: Retrieval-augmented generation (RAG)-based LLM accuracy increased by 40 times, and vector search precision improved by 51%.  
* Retrieval Speed: Achieved vector search of ≈6.6 million records in 1 second.

![][image4]

These results stem from an efficient pipeline combining Iternal’s Blockify distillation and data-cleansing with the powerful Intel Gaudi 2 AI Accelerators. Blockify outputs an optimized taxonomy of modular content indexed for dynamic contextual responses:

* Ingestion and de-duplication of employee and HR onboarding manuals, policy and procedure documents, and region specific store guidance.  
* Distillation into concise, reusable blocks tagged with employee focused training language.  
* Creation of a secure, portable dataset ready for air-gapped deployment.

### AirgapAI – Inferencing at the Edge with Intel NPU

Optimizing a dataset is only as useful as its “in-field” applicability. AirgapAI is a powerful, network-independent AI solution designed to run locally on any Intel-equipped AI PC inside The Retailer's firewalled environment.

Stored securely on the local device, the Blockified dataset never leaves The Retailer’s property. Employees can run any open-source LLM, including custom fine-tunes that understand employee-specific vernacular, directly on their laptops, even without internet connectivity.

After loading the dataset onto an AirgapAI-enabled AI PC, the system can scan 10 million vector records in under 1.5 seconds, retrieve the most relevant employee training scenario stories, and generate a bespoke guidance on how to handle a situation on the spot—all without touching the public cloud.

By operating completely offline, AirgapAI upholds stringent data-protection standards, no external connection is required, minimizing potential vulnerabilities and ensuring confidential employee matters remain strictly private. HR reps can quickly respond to employee inquiries, craft policy follow-ups, translate guidance into multiple languages, and more.

One of the primary issues with legacy RAG is the semantic drift between how unique employee questions are represented in vector space, compounded by vector dilution when extraneous details pollute a chunk of text. Blockify eliminates these issues by delivering a 51 percent improvement in vector accuracy and by embedding a dedicated query element that guides retrieval toward the most appropriate content.  
![][image5]

## **What We Did: Breaking Down the Framework**

For AI inference to perform at scale, robust infrastructure is essential. Intel Gaudi 2 accelerated the inference of large language models (LLMs). Gaudi 2 is purpose-built for deep-learning workloads; its architecture allows for high throughput—ideal for parallel processing of complex, layered data such as employee handbooks.

The Retailer's HR materials often contain high degrees of dense context that would confuse traditional RAG systems. To enable real-time retrieval and deliver detailed responses, these documents were pre-processed and indexed using Iternal’s Blockify to modularize content into manageable blocks. Blocks are deduplicated, distilled, indexed, tagged, and merged into a final output dataset packaged for edge deployment.

The LLAMA 3 LLM was fine-tuned via Low-Rank Adaptation (LoRA) and run on a single Intel Gaudi 2 core. 

After extensive testing, Iternal and Intel determined optimal output quality and compute performance when processing 8,000-character segments, generating 1,000 tokens per query with 100 parallel jobs.

### The Blockify workflow steps included:

1. Chunking the Text: The source documents were divided into smaller content chunks based on a proprietary algorithm. Those chunks were passed into the specially configured LLM, which output modular blocks of content. These blocks offer a robust taxonomy that can be reused or reassembled based on user needs.

![][image6]

2. Embeddings: These content blocks were converted into embeddings (vector representations) to capture unique context and structure, enabling content-aware retrieval within AirgapAI.  
3. Retrieval and Response Generation: Based on user queries, the system retrieves relevant content from the Context-Aware Retrieval Database for accurate, contextually relevant responses.

This enhanced workflow allows the HR system to instantly recall specific employee insights, training materials, benefits information, and policy documents, with the ability to dynamically assemble content into diverse structured outputs using large language models.

The result? Real-time expertise, engagement, and personalized content in minutes \- something that would otherwise require hours of manual research and compilation.

## **Business Use Cases: Real-Time AI Inference in Action**

The implications for broader expansion of this technology across The Retailer are extensive.

* **Personalized Employee Communications:** Combine Blockify and AirgapAI to craft unique emails that highlight department-specific news, training opportunities, and benefit updates, all vetted for employee preferences.  
* **Tailored Onboarding Materials:** Instantly assemble new hire packets featuring personalized role descriptions, team introductions, and policy overviews, ensuring compliance with The Retailer's HR policies.  
* **Performance Review Summaries:** Generate individualized summaries of employee performance, referencing specific achievements and growth areas, complete with actionable feedback and development goals.  
* **Shift Briefings:** Before a shift, managers can pull personalized briefing packets that summarize each employee's recent performance, preferred tasks, and any relevant accommodations—completely offline.  
* **Staffing Optimization:** Match available employees to open shifts in real time, using AI-driven analysis of employee skills and store needs while ensuring labor law compliance.

### What This Means for You: Scalable AI Inference for Future Growth

By uniting Intel Gaudi 2 and Iternal Technologies’ Blockify with the secure, offline capabilities of AirgapAI, retailers can harness AI inference at scale, turning decades of unstructured advancement data into actionable insights without ever exposing sensitive information to third-party clouds.

### Together, Intel and Iternal help Retailers:

* **Automate HR Data Ingestion & Curation:** Rapidly process and distill mountains of employee records and HR documents, ensuring you get accurate answers without hallucinations.  
* **Drive Hyper-Personalized Employee Experiences:** Tailor every employee interaction \- from onboarding to training and benefits communication \- based on individual roles, preferences, and career development needs.  
* **Enable Faster HR Decision-Making:** Confidently retrieve and synthesize trusted employee and operational information to craft HR policies, analyze workforce trends, and manage compliance in seconds rather than hours.  
* **Protect Employee Trust:** Keep all sensitive employee data, performance histories, contact details, and personal preferences inside your firewall at all times.

With refined data pipelines and robust inference infrastructure now available, AI has moved from conceptual to operational in food retail HR. Whether you’re optimizing talent acquisition, enhancing employee engagement, or ensuring compliance, the tools and frameworks are in place to meet your needs. Securely, accurately, and at scale.  







