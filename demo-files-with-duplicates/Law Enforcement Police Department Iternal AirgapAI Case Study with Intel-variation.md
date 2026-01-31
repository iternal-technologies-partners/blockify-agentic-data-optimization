# Supporting a Top 10 City’s Police Department Operations through Improving LLM Accuracy by 78x with Blockify and AirgapAI

AI is rapidly becoming a strategic asset for U.S. Police Departments. To enhance citizen support, ensure policy compliance, and improve the general accuracy of operations, officers must access the right information, at the right time, in a safe, secure, and trusted manner \- while being absolutely certain every insight is factually correct and within the rules, regulations, and legal frameworks provided.

Intel and Iternal Technologies have partnered to provide a unique solution that addresses the most common challenges police departments face when adopting AI technologies: hallucinations, data curation, governance, and ultra-granular access-control of sensitive and restricted data.

Pairing highly performant data-center solutions like Gaudi 2 & Blockify® for data preparation and optimization with edge-based Intel NPU chips & AirgapAI™ software for 100 percent local inference delivers an end-to-end platform that allows police department personnel to craft compliant reports, answer citizen inquiries, and surface operational documentation \- with 78X greater accuracy.

# Iternal AI Academy: Enterprise AI Fluency Training

**Transform Your Workforce into AI-Proficient Professionals**


## The Challenge

Organizations investing in AI tools face a critical gap: employees don't know how to communicate effectively with AI. Reading documentation isn't the same as doing. Your teams need practical, hands-on training to unlock the full potential of AI investments—whether they use Claude, ChatGPT, AirGap AI, or any other platform.


## The Solution

The **Iternal AI Academy** (edu.iternal.ai) delivers comprehensive AI fluency training built from thousands of real-world enterprise training sessions. Unlike theoretical courses, our platform combines foundational education with interactive practice scenarios where employees learn by doing.


## Platform Highlights

| Feature | Description |
|---------|-------------|
| **610+ Courses** | Spanning every major industry, job role, and skill level |
| **Three Proficiency Tiers** | Beginner, Advanced, and Expert tracks for progressive learning |
| **Real-Time AI Feedback** | Prompts are scored and critiqued by AI for immediate improvement |
| **Verified Certificates** | Independently verifiable credentials with unique certificate IDs |
| **Universal Application** | Skills transfer to any AI platform—not vendor-locked |

## How It Works

1. **Learn**: Clear instruction on prompt structure, comparing weak vs. strong examples
2. **Practice**: Real scenarios where employees craft prompts and interact with live AI
3. **Score**: AI evaluates prompt quality and provides specific improvement guidance
4. **Certify**: Earn verifiable credentials demonstrating AI competency


## Course Categories

- **Industry-Specific**: Pharmaceutical, Finance, Logistics, Manufacturing, Healthcare, etc.
- **Role-Based**: Sales, Marketing, Customer Service, Operations, HR, IT, etc.
- **Skill-Focused**: Email follow-ups, CRM management, discovery calls, account planning, etc.
- **Advanced Techniques**: XML prompting, structured context building, complex workflows

## Flexible Enterprise Licensing

| Option | Investment |
|--------|------------|
| Individual License | 1 Year Subscription |
| Enterprise (30+ seats) | Volume discounts available |
| Pilot Program | Single license to evaluate before rollout |


## Ideal Deployment Model

**Weekly 45-Minute Team Sessions**: Organizations see the greatest adoption when teams learn together—practicing prompts, sharing discoveries, and building momentum as a community rather than isolated individuals via the self-service course.

## Why Iternal AI Academy

- **Battle-Tested Curriculum**: Developed from thousands of enterprise training engagements
- **Platform Agnostic**: Skills apply to any AI tool your organization uses
- **Measurable Progress**: Track completion, scores, and certification across your workforce
- **Continuous Expansion**: Dozens of new courses added monthly to address emerging use cases

**Ready to accelerate your workforce's AI capabilities?**

Visit **edu.iternal.ai** or contact your Iternal representative for a live demonstration.

*Iternal AI Academy—Because talking to AI is a skill, and skills are built through practice.*


## **Why AI Inference Matters and Why You Should Care**

AI inference is more than running a trained model; it goes beyond simple document search. It empowers law enforcement teams to process real-time, accurate, and contextually relevant insights from critical policies and procedures at scale.

Traditional operation efforts require manual research across countless repositories. Without an AI-driven content-lifecycle approach, Law Enforcement Organizations risk delays, non-compliant actions, or accidents in enforcement efforts. Garbage in, garbage out \- and if you can’t trust your AI every time, you can’t trust it at all.

![][image1]

Intel and Iternal used AI to bring structure to unstructured documents: citizen complaints, police reports, body camera footage transcripts, policy manuals, and operational guidelines, through an advanced data-ingestion and optimization approach powered by Blockify.

![][image2]

The result is a single source of truth distilled to only 2.5 percent of its original size \- easier to govern, quicker to query, and fully aligned to export-control rules.

## **A Summary of the AI Inference Solution**

### Blockify Data Ingestion with Gaudi

Leveraging Intel Gaudi 2 AI accelerators and Iternal’s patented Blockify solution, Major Law Enforcement Organization teams can ingest and optimize thousands of documents for an improved large-language-model inferencing pipeline paired with RAG.

* Processing Speed: ≈ 900 words / sec  
* Accuracy: RAG-based LLM accuracy ↑ 40×; vector search precision ↑ 51 %  
* Inference Throughput: 0.68 inferences / sec (≈ 5,404 bytes / sec)

Blockify’s three-pronged ingestion, distillation, and taxonomy workflow:

* Ingestion \- Extract essential information from source.  
* Distillation \- eliminate redundant clauses, legacy specs, and obsolete standards.  
* Taxonomy Creation \- index every block for dynamic contextual retrieval

### AirgapAI – Inferencing at the Edge with Intel NPU

Optimizing data is only useful when applied in the field. AirgapAI is a powerful, network-independent AI solution designed to run locally on Intel-equipped AI PCs within a police department's secure environment – no external connectivity required.

* **Vector Search & Inference:** ≈ 2.2× faster on Intel NPU, enabling quicker analysis of large datasets.  
* **Accuracy:** RAG-based LLM accuracy ↑ 40×; vector search precision ↑ 51%, leading to more reliable information for officers and improved policy compliance.  
* **Retrieval:** Scan ≈ 10 million records in \< 1.5 sec, allowing rapid access to critical information for citizen support and operational efficiency.

After Blockify outputs the distilled dataset, officers load it onto an AirgapAI-enabled workstation. The system retrieves relevant content and launches an LLM inference to draft accurate responses to citizen inquiries, ensure policy-checked incident reports, or generate compliant internal communications – all fully offline, ensuring CJIS, HIPAA, and other relevant data security standards are met.

By operating completely offline, AirgapAI upholds stringent data-protection standards, as no external connection is required, minimizing potential vulnerabilities and ensuring confidential citizen information and operational data remains strictly private.

## **Eliminating Legacy RAG Pitfalls**

A core challenge for police departments is how officers phrase questions and the overwhelming volume of information within policy documents. Our AI solution addresses these issues by delivering a 51 percent improvement in the accuracy of retrieved information. It achieves this by focusing on the core intent of a query and guiding the system toward the most relevant content, thereby enhancing citizen support, policy compliance, and the general accuracy of police operations.

![][image3]

## **What We Did: Breaking Down the Framework**

Intel Gaudi 2 accelerates LLM inference with high-throughput deep-learning cores, ideal for parallel processing of complex, multi-tiered defense documentation. The Major Law Enforcement Organization's documents often contain nested specifications and acronym-heavy language. To enable real-time Q\&A, content was modularized with Blockify, then embedded as high-density vectors for instantaneous retrieval.

LLAMA 3, fine-tuned via Low-Rank Adaptation (LoRA) on a single Gaudi 2 core, achieved optimal quality by processing 8,000-character segments and generating 1,000 tokens per response with 100 parallel jobs.

### The Blockify workflow steps included:

1. Chunking the Text: The source documents were divided into smaller content chunks based on a proprietary algorithm. Those chunks were passed into the specially configured LLM, which output modular blocks of content. These blocks offer a robust taxonomy that can be reused or reassembled based on user needs.

![][image4]

2. Embeddings: These content blocks were converted into embeddings (vector representations) to capture unique context and structure, enabling content-aware retrieval within AirgapAI.  
3. Retrieval and Response Generation: Based on user queries, the system retrieves relevant content from the Context-Aware Retrieval Database for accurate, contextually relevant responses.

This enhanced workflow allows instant recall of insights, strategies, policies, dynamically assembling content into diverse outputs using large language models. The result is real-time expertise, engagement, and personalized content in minutes, saving hours of manual work.

### Business Use Cases: Real-Time AI Inference in Action

* Citizen Inquiry Response \- assemble detailed responses to common citizen questions about local ordinances, crime statistics, or department procedures in minutes while ensuring data privacy rules are met.  
* Policy Compliance Audits \- auto-populate incident reports with lineage-tracked policy references and legal precedents.  
* Public Information Releases & Briefings \- produce sanitized (replace with legally compliant, publicly releasable) marketing collateral for community programs without exposing sensitive source data.  
* Dispatch FAQ Assistant \- field real-time questions from officers on protocol deviations, jurisdiction boundaries, or emergency response metrics entirely offline.  
* Training Procedure Authoring \- draft qualification training plans referencing historical incident outcomes or community feedback in seconds.

### What This Means for You: Scalable AI Inference for Future Growth

By uniting Intel Gaudi 2 and Iternal Technologies’ Blockify with the secure, offline capabilities of AirgapAI, Police Departments can harness AI inference at scale, turning decades of unstructured operational data into actionable insights without ever exposing sensitive information to third-party clouds. With Intel Gaudi 2, Blockify, and AirgapAI, a Major Police Department can:

* Automate Data Ingestion & Curation \- process terabytes of legacy documentation while slashing inaccuracies.  
* Drive Hyper-Compliant Content \- ensure every generated paragraph respects privacy, legal, and departmental guidelines.  
* Accelerate Decision-Making \- surface trusted answers in seconds, compressing response times and boosting public trust.  
* Protect Citizen Data \- keep all sensitive data within the department's secure network, eliminating cloud-based exposure risks.

AI has moved from conceptual to operational in law enforcement. Whether generating a rapid-response citizen communication, answering internal policy inquiries, or drafting operational procedures, Intel and Iternal deliver the secure, accurate, and scalable framework a Major Police Department needs to maintain mission advantage.




