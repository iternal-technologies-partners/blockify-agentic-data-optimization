# Supporting a Top 5 Auto Insurance Company's Operations: Improving LLM Accuracy by 78x with Blockify and AirgapAI

Trust is the foundation of insurance. AI is rapidly becoming a strategic asset for insurance carriers, and for a Top 5 Auto Insurance Company, the imperative is clear: enhance customer support, ensure policy compliance, and improve the general accuracy of operations. Claims adjusters and agents must access the right information, at the right time, in a safe, secure, and trusted manner; while being absolutely certain every insight is factually correct and within the rules, regulations, and legal frameworks provided.

![][image1]

Intel and Iternal Technologies have partnered to deliver a solution that confronts the most common challenges insurance carriers face when adopting AI technologies: hallucinations, data curation, governance, and ultra-granular access-control of sensitive and restricted data.

Pairing highly performant data-center solutions like Xeon/Gaudi and Blockify for data preparation and optimization with edge-based Intel NPU chips and AirgapAI software for 100 percent local inference delivers an end-to-end platform that allows insurance personnel to craft compliant claims assessments, answer customer inquiries, and surface underwriting documentation; with 78x greater accuracy.

## **Benchmark Results**

The Top 5 Auto Insurance Company's 351-page Insurance Policy and Code of Conduct Guidelines contains 141,836 words of essential conduct materials that must be processed. Depending on business and technology objectives, there are multiple methods to process the information, using Intel AI PCs, Intel Xeon, or Intel Gaudi 2.

### Intel Core Ultra 7 265V

Leveraging Intel Core Ultra 7 265V AI PC CPU, processing is completed in approximately 70,918 seconds. The ability to process 4,860 pages of text per month (2 words per second, 1.5 tokens per second) on an Intel Core Ultra 7 265V AI PC CPU demonstrates the ability to start small and scale.

* **Total Time**: Approximately 70,918 seconds  
* **Total Responses**: Approximately 993 chunks

### Intel Xeon 6767P

Leveraging Intel Xeon 6767P Series 6 CPUs, processing is completed in approximately 1,689 seconds. The ability to process 622 thousand pages of text per month (84 words per second, 112 tokens per second) on a single Xeon 6767P CPU demonstrates the scalability and efficiency of this approach on non-GPU hardware.

* **Total Time**: Approximately 1,689 seconds  
* **Total Responses**: Approximately 993 chunks

### Intel Gaudi 2

Leveraging Gaudi 2, processing is completed in approximately 141 seconds. The ability to process 5 million pages of text per month (1,008 words per second, 1,768 tokens per second) on a single 8xGPU Gaudi 2 demonstrates the scalability and efficiency of this approach.

* **Total Time**: Approximately 141 seconds  
* **Total Responses**: Approximately 993 chunks

### Intel Gaudi 3

Leveraging Gaudi 3, processing is completed in approximately 35 seconds. The ability to process 17.8 million pages of text per month (4,065 words per second, 5,420 tokens per second) on a single Gaudi 3 core demonstrates the scalability and efficiency of this approach.

* **Total Time**: Approximately 35 seconds  
* **Total Responses**: Approximately 993 chunks

Beyond speed, Blockify's approach increased the precision of vector searches and RAG models, virtually eliminating hallucinations and improving LLM accuracy by approximately 78x (7,800 percent) compared with a traditional RAG pipeline.

## **Why AI Inference Matters**

AI inference extends beyond running a trained model; it goes beyond simple document search. This capability empowers insurance teams to process real-time, accurate, and contextually relevant insights from complex policy documents and underwriting guidelines at scale.

Traditional operation efforts require manual research across countless policy documents, claims histories, and regulatory filings. Without an AI-driven content-lifecycle approach, insurance carriers risk processing delays, non-compliant decisions, or costly errors in claims adjudication. Garbage in, garbage out; if you cannot trust your AI every time, you cannot trust it at all.

![][image2]

Intel and Iternal used AI to bring structure to unstructured documents: customer claims, policy documents, adjuster notes, underwriting manuals, and compliance guidelines, through an advanced data-ingestion and optimization approach powered by Blockify.

![][image3]

The result is a single source of truth distilled to only 2.5 percent of its original size; easier to govern, quicker to query, and fully aligned to export-control rules.

## **A Summary of the AI Inference Solution**

### Blockify Data Ingestion with Gaudi

Leveraging Intel Xeon/Gaudi AI accelerators and Iternal's patented Blockify solution, The Top 5 Auto Insurance Company teams can ingest and optimize thousands of documents for an improved large-language-model inferencing pipeline paired with Agentic search and Retrieval Augmented Generation (RAG).

#### Processing Speed

| Hardware | Words per Second | Pages per Month |
| :---- | :---- | :---- |
| Intel Core Ultra 7 265V | 2 | 4,860 |
| Intel Xeon 6767P | 84 | 622,000 |
| Intel Gaudi 2 | 1,008 | 5,000,000 |
| Intel Gaudi 3 | 4,065 | 17,800,000 |

* **Accuracy**: RAG-based LLM accuracy increased 40x; vector search precision increased 51%  
* **Inference Throughput**: 0.68 inferences per second (approximately 5,404 bytes per second)

Blockify's three-pronged ingestion, distillation, and taxonomy workflow:

* **Ingestion**: Extract essential information from source
* **Distillation**: Eliminate redundant clauses, legacy specs, and obsolete standards
* **Taxonomy Creation**: Index every block for dynamic contextual retrieval

### AirgapAI: Inferencing at the Edge with Intel NPU

Optimizing data is only useful when applied in the field. AirgapAI is a powerful, network-independent AI solution designed to run locally on Intel-equipped AI PCs within an insurance company's secure environment; no external connectivity required.

* **Vector Search and Inference**: Approximately 2.2x faster on Intel NPU, enabling quicker analysis of large datasets
* **Accuracy**: RAG-based LLM accuracy increased 40x; vector search precision increased 51%, leading to more reliable information for adjusters and improved policy compliance
* **Retrieval**: Scan approximately 10 million records in less than 1.5 seconds, allowing rapid access to critical information for customer support and claims processing and operational efficiency

After Blockify outputs the distilled dataset, employees load it onto an AirgapAI-enabled workstation. The system retrieves relevant content and launches an LLM inference to draft accurate responses to customer inquiries, ensure policy-compliant claims assessments, or generate compliant internal communications; all fully offline, ensuring PII, HIPAA, and other relevant data security standards are met.

![][image4]

By operating completely offline, AirgapAI upholds stringent data-protection standards; no external connection is required, minimizing potential vulnerabilities and ensuring confidential citizen information and operational data remains strictly private.

As LLMs become more powerful and less compute intensive, the Intel Core line of chips is able to maximize the performance and utilization of highly efficient models with improved LLM accuracy. Accuracy can only be improved if the quality of the data is high. Garbage in, garbage out.

![][image5]

## **ROI and Cost Benefits of On-Premise AI Inference**

At a broader organizational level, the transition to AI PCs for 37,000 employees is projected to yield a total net benefit of over $155 million over 4 years, with a payback period of less than 11 months.

Deploying AI on existing infrastructure like Intel Xeon CPUs and new AI PCs delivers substantial cost savings and a rapid return on investment. For inference workloads suited to the performance profile of a modern CPU, the company avoids an initial capital expenditure of approximately $40,000 per server by leveraging existing Xeon hardware instead of purchasing new, specialized GPU accelerators.

This strategic decision results in a projected 3-year Total Cost of Ownership (TCO) of just $4,221 per Xeon server, compared to $55,942 for a new GPU-based server.

* **Minimized Capital Expenditure**: By using existing Intel Xeon 6767P hardware for inference, the company avoided approximately $40,000 upfront cost per server that would have been required to purchase new H100 GPU servers
* **Lower Total Cost of Ownership (TCO)**: For moderate-throughput workloads, the company achieved a 3-year TCO of only $4,221 per Xeon server, an approximately 92% reduction compared to the projected $55,942 TCO for a new GPU server
* **Cost-Effective Scalability**: For low-to-moderate throughput needs (less than 4.35 billion tokens/year), the Xeon provides superior cost-per-token performance ($0.32/million) compared to a new GPU server ($0.65/million) when factoring in the initial purchase price
* **Exceptional Organizational ROI**: The company-wide AI PC deployment projects an overall ROI of 342.2% over a 4-year period, transforming operations at scale
* **Rapid Payback Period**: The total investment is expected to be recouped in just 10.86 months, driven by significant productivity gains and operational savings
* **Significant Productivity Gains**: The solution is projected to deliver a 2% productivity gain across the workforce, translating to over $171 million in value over four years

This financial model underscores a critical strategic insight: leveraging existing Intel Xeon CPUs for on-premise AI inference is a highly effective way to minimize upfront costs and lower TCO for low-to-moderate demand scenarios. While specialized accelerators offer higher peak throughput, the Xeon platform provides a powerful, cost-efficient, and scalable alternative that enables organizations to deploy AI without significant new capital investment, delivering a faster path to positive ROI.

## **Eliminating Legacy RAG Pitfalls**

A core challenge for insurance companies is how adjusters and agents phrase questions and the overwhelming volume of information within complex policy and claims documents. The AI solution addresses these issues by delivering a 51 percent improvement in the accuracy of retrieved information. It achieves this by focusing on the core intent of a query and guiding the system toward the most relevant content, thereby enhancing customer support, policy compliance, and the general accuracy of claims processing.

![][image6]

## **What We Did: Breaking Down the Framework**

Intel Xeon/Gaudi accelerates LLM inference with high-throughput deep-learning cores, ideal for parallel processing of complex, multi-layered insurance policy documentation. The Top 5 Auto Insurance Company's documents often contain nested specifications and acronym-heavy language. To enable real-time Q&A, content was modularized with Blockify, then embedded as high-density vectors for instantaneous retrieval.

For example, LLAMA 3, fine-tuned via Low-Rank Adaptation (LoRA) on a single Gaudi 2 core, achieved optimal quality by processing 8,000-character segments and generating 1,000 tokens per response with 100 parallel jobs.

### The Blockify Workflow Steps

The workflow consists of three essential phases:

1. **Chunking the Text**: The source documents were divided into smaller content chunks based on a proprietary algorithm. Those chunks were passed into the specially configured LLM, which output modular blocks of content. These blocks offer a robust taxonomy that can be reused or reassembled based on user needs.

![][image7]

2. **Embeddings**: These content blocks were converted into embeddings (vector representations) to capture unique context and structure, enabling content-aware retrieval within AirgapAI.

3. **Retrieval and Response Generation**: Based on user queries, the system retrieves relevant content from the Context-Aware Retrieval Database for accurate, contextually relevant responses.

This enhanced workflow allows instant recall of insights, underwriting rules, and policies, dynamically assembling content into diverse outputs using large language models. The result is real-time expertise for agents, improved customer engagement, and personalized policy information in minutes, saving hours of manual work.

### Business Use Cases: Real-Time AI Inference in Action

* **Policy and Coverage Inquiry Response**: Assemble detailed, accurate responses to customer questions about policy coverage, deductibles, or claim procedures in minutes, ensuring consistency and compliance.  
* **Automated Claims Auditing**: Auto-populate claims files with lineage-tracked policy references and regulatory precedents, reducing manual review time and ensuring compliance.  
* **Underwriting Guideline Generation**: Produce up-to-date, compliant underwriting guidelines for agents by synthesizing information from multiple regulatory and internal policy documents without exposing sensitive source data.  
* **Agent and Adjuster Assistant**: Field real-time questions from agents and adjusters on complex coverage scenarios, claims processing protocols, or state-specific regulations entirely offline.  
* **Onboarding and Training Material Creation**: Draft new-hire training plans and materials by referencing historical claims data, best practices, and policy documents in seconds.

### What This Means for You: Scalable AI Inference for Future Growth

By uniting Intel Xeon/Gaudi and Iternal Technologies' Blockify with the secure, offline capabilities of AirgapAI, Insurance Carriers can harness AI inference at scale, turning decades of unstructured operational data into actionable insights without ever exposing sensitive information to third-party clouds. With Intel Xeon/Gaudi, Blockify, and AirgapAI, a Major Insurance Carrier can:

* **Automate Policy and Claims Data Curation**: Process terabytes of legacy policy documents and claims files while slashing inaccuracies.  
* **Ensure Regulatory and Policy Compliance**: Ensure every generated communication and decision respects privacy, legal, and company guidelines.  
* **Accelerate Claims Processing and Underwriting**: Surface trusted answers in seconds, compressing decision times and improving customer satisfaction.  
* **Protect Customer Data (PII)**: Keep all sensitive customer and policy data within the company's secure network, eliminating cloud-based exposure risks.

AI has moved from conceptual to operational in the insurance industry. Whether generating a rapid-response customer communication, answering internal underwriting inquiries, or drafting claims procedures, Intel and Iternal deliver the secure, accurate, and scalable framework a Major Insurance Carrier needs to maintain competitive advantage.
