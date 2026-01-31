# Supporting a Top 10 City’s Police Department Operations through Improving LLM Accuracy by 78x with Blockify and AirgapAI

AI is rapidly becoming a strategic asset for U.S. Police Departments. To enhance citizen support, ensure policy compliance, and improve the general accuracy of operations, officers must access the right information, at the right time, in a safe, secure, and trusted manner \- while being absolutely certain every insight is factually correct and within the rules, regulations, and legal frameworks provided.

Intel and Iternal Technologies have partnered to provide a unique solution that addresses the most common challenges police departments face when adopting AI technologies: hallucinations, data curation, governance, and ultra-granular access-control of sensitive and restricted data.

Pairing highly performant data-center solutions like Gaudi 2 & Blockify® for data preparation and optimization with edge-based Intel NPU chips & AirgapAI™ software for 100 percent local inference delivers an end-to-end platform that allows police department personnel to craft compliant reports, answer citizen inquiries, and surface operational documentation \- with 78X greater accuracy.

## **Benchmark Results**

The Police Department’s 865 page policy and procedure handbook contains 326,145 words of essential conduct materials that were processed in about 617 seconds. The ability to process 5 million pages of text per month on a single Gaudi 2 core demonstrates the scalability and efficiency of this approach.

* Total Time: ≈ 617 seconds  
* Total Responses: ≈ 1276 chunks

Beyond speed, Blockify’s approach increased the precision of vector searches and RAG models, virtually eliminating hallucinations and improving LLM accuracy by approximately 78× (7,800 percent) compared with a traditional RAG pipeline.

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




