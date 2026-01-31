# Supporting a Major Federal Systems Integrator's Classified Proposal Operations through Improving LLM Accuracy by 78x with Blockify and AirgapAI

AI is rapidly becoming a strategic asset for U.S. federal systems integrators. To win highly competitive, classified government contracts, proposal, capture, and engineering teams must access the right information, at the right time, in a safe, secure, and trusted manner \- while being absolutely certain every insight is factually correct and never leaks outside a Sensitive Compartmented Information Facility (SCIF).

Intel and Iternal Technologies have partnered to provide a unique solution that addresses the most common challenges Major Federal Systems Integrator faces when adopting AI technologies: hallucinations, data curation, governance, and ultra-granular access-control of classified and ITAR–restricted data.

Pairing highly performant data-center solutions like Gaudi 2 & Blockify® for data preparation and optimization with edge-based Intel NPU chips & AirgapAI™ software for 100 percent local inference delivers an end-to-end platform that allows Major Federal Systems Integrator personnel to craft compliant proposals, answer customer RFIs, and surface engineering documentation \- without ever letting sensitive data leave the SCIF.

## **Benchmark Results**

A corpus of approx. 8,599 words of sensitive sales materials were processed in about 17 seconds. The ability to process 5 million pages of text per month on a single Gaudi 2 core demonstrates the scalability and efficiency of this approach.

* Total Time: ≈ 16.74 seconds  
* Total Responses: ≈ 31

Beyond speed, Blockify’s approach increased the precision of vector searches and RAG models, virtually eliminating hallucinations and improving LLM accuracy by approximately 78× (7,800 percent) compared with a traditional RAG pipeline.

## **Why AI Inference Matters and Why You Should Care**

AI inference is more than running a trained model; it goes beyond simple document search. It empowers proposal, capture, and engineering teams to extract real-time, accurate, and contextually relevant insights from decades of classified program data at scale.

Traditional proposal efforts require manual content mining across countless repositories. Without an AI-driven content-lifecycle approach, Federal Systems Integrators risk delays, non-compliant language, or inadvertent disclosure of controlled information. Garbage in, garbage out \- and if you can’t trust your AI every time, you can’t trust it at all.

![][image1]

Intel and Iternal used AI to bring structure to unstructured documents: historical proposals, CDRLs, CONOPS, cyber-security annexes, hardware drawings, software bill-of-materials, and test reports, through an advanced data-ingestion and optimization approach powered by Blockify.

![][image2]

The result is a single source of truth distilled to only 2.5 percent of its original size \- easier to govern, quicker to query, and fully aligned to export-control rules.

## **A Summary of the AI Inference Solution**

### Blockify Data Ingestion with Gaudi

Leveraging Intel Gaudi 2 AI accelerators and Iternal’s patented Blockify solution, Major Defense Contractor teams can ingest and optimize thousands of documents for an improved large-language-model inferencing pipeline paired with RAG.

* Processing Speed: ≈ 900 words / sec  
* Accuracy: RAG-based LLM accuracy ↑ 40×; vector search precision ↑ 51 %  
* Inference Throughput: 0.68 inferences / sec (≈ 5,404 bytes / sec)

Blockify’s three-pronged ingestion, distillation, and taxonomy workflow:

* Ingestion & De-duplication \- eliminate redundant clauses, legacy specs, and obsolete standards.  
* Distillation \- segment content into modular “blocks” tagged with classification, ITAR, and export-control attributes.  
* Taxonomy Creation \- index every block for dynamic contextual retrieval inside the SCIF.

### AirgapAI – Inferencing at the Edge with Intel NPU

Optimizing data is only useful when applied in the field. AirgapAI is a powerful, network-independent AI solution designed to run locally on Intel-equipped AI PCs inside a SCIF \- no external connectivity required.

* Vector Search & Inference: ≈ 2.2× faster on Intel NPU  
* Accuracy: RAG-based LLM accuracy ↑ 40×; vector search precision ↑ 51 %  
* Retrieval: Scan ≈ 10 million records in \< 1.5 sec

After Blockify outputs the distilled dataset, engineers load it onto an AirgapAI-enabled workstation. The system retrieves relevant content and launches an LLM inference to draft compliance-checked sections, technical descriptions, or responses to Contracting Officer questions \- all fully offline, ensuring NISPOM, CMMC, and ITAR compliance.

By operating completely offline, AirgapAI upholds stringent data-protection standards, no external connection is required, minimizing potential vulnerabilities and ensuring confidential information remains strictly private. 

## **Eliminating Legacy RAG Pitfalls**

One of the primary issues with legacy RAG is the semantic drift between how unique donor questions are represented in vector space, compounded by vector dilution when extraneous details pollute a chunk of text. Blockify eliminates these issues by delivering a 51 percent improvement in vector accuracy and by embedding a dedicated query element that guides retrieval toward the most appropriate content.

![][image3]

## **What We Did: Breaking Down the Framework**

Intel Gaudi 2 accelerates LLM inference with high-throughput deep-learning cores, ideal for parallel processing of complex, multi-tiered defense documentation. Major Federal Systems Integrator's documents often contain nested specifications and acronym-heavy language. To enable real-time Q\&A, content was modularized with Blockify, then embedded as high-density vectors for instantaneous retrieval.

LLAMA 3, fine-tuned via Low-Rank Adaptation (LoRA) on a single Gaudi 2 core, achieved optimal quality by processing 8,000-character segments and generating 1,000 tokens per response with 100 parallel jobs.

### The Blockify workflow steps included:

1. Chunking the Text: The source documents were divided into smaller content chunks based on a proprietary algorithm. Those chunks were passed into the specially configured LLM, which output modular blocks of content. These blocks offer a robust taxonomy that can be reused or reassembled based on user needs.

![][image4]

2. Embeddings: These content blocks were converted into embeddings (vector representations) to capture unique context and structure, enabling content-aware retrieval within AirgapAI.  
3. Retrieval and Response Generation: Based on user queries, the system retrieves relevant content from the Context-Aware Retrieval Database for accurate, contextually relevant responses.

This enhanced workflow allows the system to instantly recall specific insights, marketing strategies, service offerings, and proposals, with the ability to dynamically assemble content into diverse structured outputs using large language models.

The result? Real-time expertise, engagement, and personalized content in minutes \- something that would otherwise require hours of manual research and compilation.

## **Business Use Cases: Real-Time AI Inference in Action**

* Classified Proposal Generation \- assemble RFP volumes, SOW mappings, and BOE narratives in minutes while ensuring DD-254 classification rules are met.  
* Engineering Change Requests \- auto-populate ECP templates with lineage-tracked subsystem specs and cost impacts.  
* Capability Statements & Data Sheets \- produce ITAR-sanitized marketing collateral for FMS programs without exposing source data.   
* SCIF FAQ Assistant \- field real-time questions from program managers on power budgets, SWaP-C metrics, or MIL-STD compliance entirely offline.  
* Test Procedure Authoring \- draft qualification test plans referencing historical vibration or EMI results in seconds.  
* Disconnected Operations \- deploy on-premise for secure, air-gapped environments, ensuring compliance with strict data sovereignty and access controls for classified programs.

### What This Means for You: Scalable AI Inference for Future Growth

By uniting Intel Gaudi 2 and Iternal Technologies’ Blockify with the secure, offline capabilities of AirgapAI, Federal Systems Integrators can harness AI inference at scale, turning decades of unstructured advancement data into actionable insights without ever exposing sensitive information to third-party clouds. With Intel Gaudi 2, Blockify, and AirgapAI, Major Federal Systems Integrator can:

* Automate Data Ingestion & Curation \- process terabytes of legacy documentation while slashing hallucinations.  
* Drive Hyper-Compliant Content \- ensure every generated paragraph respects classification, ITAR, and customer-flow-down clauses.  
* Accelerate Decision-Making \- surface trusted answers in seconds, compressing proposal cycles and boosting Pwin (Proposal Win Probability).  
* Protect National Security \- keep all sensitive data inside the SCIF, eliminating cloud-based exposure risks.

AI has moved from conceptual to operational in defense contracting. Whether generating a rapid-response proposal, answering contracting-officer inquiries, or drafting engineering artifacts, Intel and Iternal deliver the secure, accurate, and scalable framework Major Federal Systems Integrator needs to maintain mission advantage.




