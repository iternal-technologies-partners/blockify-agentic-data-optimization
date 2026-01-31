# Supporting a Top 3 Oil and Gas Company’s Operations through Improving LLM Accuracy by 78x with Blockify and AirgapAI

AI is rapidly becoming a strategic asset for the Energy industry. To enhance operational efficiency, ensure safety compliance, and improve the general accuracy of remote site operations, engineers and field operators must access the right information, at the right time, in a safe, secure, and trusted manner \- while being absolutely certain every insight is factually correct and within the rules, regulations, and legal frameworks provided.

![][image1]

Intel and Iternal Technologies have partnered to provide a unique solution that addresses the most common challenges energy companies face when adopting AI technologies: hallucinations, data curation, governance, and ultra-granular access-control of sensitive and restricted data.

Pairing highly performant data-center solutions like Gaudi 2/Xeon & Blockify® for data preparation and optimization with edge-based Intel NPU chips & AirgapAI™ software for 100 percent local inference delivers an end-to-end platform that allows company personnel to draft compliant reports, answer technical inquiries, and surface operational documentation \- with 78X greater accuracy.

## **Benchmark Results**

The Top 3 Oil and Gas Company’s 404 page operational and safety handbooks contains 70,881 words of essential conduct materials that must be processed.  
Depending on business and technology objectives there are multiple methods to process the information, using Intel AI PCs, Intel Xeon, or Intel Gaudi 2\.

### Intel Core Ultra 7 265V:

Leveraging Intel Core Ultra 7 265V AI PC CPU, processing is completed in about 35,441 seconds. The ability to process 4,860 pages of text per month (2 words per second) on a Intel Core Ultra 7 265V AI PC CPU demonstrates the ability to start small and scale.

* Total Time: ≈ 35441 seconds  
* Total Responses: ≈ 496 chunks

### Intel Xeon 6767P:

Leveraging Intel Xeon 6767P Series 6 CPUs, processing is completed in about 844 seconds. The ability to process 622 thousand pages of text per month (84 words per second) on a single Xeon 6767P CPU demonstrates the scalability and efficiency of this approach on non-GPU hardware.

* Total Time: ≈ 844 seconds  
* Total Responses: ≈ 496 chunks

### Intel Gaudi 2:

Leveraging Gaudi 2, processing is completed in about 105 seconds. The ability to process 5 million pages of text per month (675 words per second) on a single Gaudi 2 core demonstrates the scalability and efficiency of this approach.

* Total Time: ≈ 105 seconds  
* Total Responses: ≈ 496 chunks

Beyond speed, Blockify’s approach increased the precision of vector searches and RAG models, virtually eliminating hallucinations and improving LLM accuracy by approximately 78× (7,800 percent) compared with a traditional RAG pipeline.

## **Why AI Inference Matters and Why You Should Care**

AI inference is more than running a trained model; it goes beyond simple document search. It empowers energy teams to process real-time, accurate, and contextually relevant insights from critical operational and safety procedures at scale.  
Traditional operation efforts require manual research across countless repositories. Without an AI-driven content-lifecycle approach, Energy Organizations risk delays, non-compliant actions, or accidents in field operations. Garbage in, garbage out \- and if you can’t trust your AI every time, you can’t trust it at all.

![][image2]

Intel and Iternal used AI to bring structure to unstructured documents: maintenance logs, sensor data, safety incident reports, and operational guidelines, through an advanced data-ingestion and optimization approach powered by Blockify.

![][image3]

The result is a single source of truth distilled to only 2.5 percent of its original size \- easier to govern, quicker to query, and fully aligned to export-control rules.

## **A Summary of the AI Inference Solution**

### Blockify Data Ingestion with Gaudi

Leveraging Intel Gaudi 2 AI accelerators / Xeon CPUs and Iternal’s patented Blockify solution, Major Energy Company teams can ingest and optimize thousands of documents for an improved large-language-model inferencing pipeline paired with RAG.

* Processing Speed: ≈ 900 words / sec  
* Accuracy: RAG-based LLM accuracy ↑ 40×; vector search precision ↑ 51 %  
* Inference Throughput: 0.68 inferences / sec (≈ 5,404 bytes / sec)

Blockify’s three-pronged ingestion, distillation, and taxonomy workflow:

* Ingestion \- Extract essential information from source.  
* Distillation \- eliminate redundant clauses, legacy specs, and obsolete standards.  
* Taxonomy Creation \- index every block for dynamic contextual retrieval

### AirgapAI – Inferencing at the Edge with Intel NPU

Optimizing data is only useful when applied in the field. AirgapAI is a powerful, network-independent AI solution designed to run locally on Intel-equipped AI PCs within a company’s secure environment – no external connectivity required.

* Vector Search & Inference: ≈ 2.2× faster on Intel NPU, enabling quicker analysis of large datasets.  
* Accuracy: RAG-based LLM accuracy ↑ 40×; vector search precision ↑ 51%, leading to more reliable information for engineers and improved safety compliance.  
* Retrieval: Scan ≈ 10 million records in \< 1.5 sec, allowing rapid access to critical information for operational efficiency and support.

After Blockify outputs the distilled dataset, operators load it onto an AirgapAI-enabled workstation. The system retrieves relevant content and launches an LLM inference to draft accurate responses to technical inquiries, ensure safety-checked incident reports, or generate compliant internal communications – all fully offline, ensuring OSHA and other relevant data security standards are met.  
![][image4]

By operating completely offline, AirgapAI upholds stringent data-protection standards, as no external connection is required, minimizing potential vulnerabilities and ensuring confidential operational data remains strictly private.

As LLMs become more powerful and less compute intensive, the Intel Core line of chips is able to maximize the performance and utilization of highly efficient models with improved LLM accuracy. However accuracy only can be improved if the quality of the data is high. Garbage in, garbage out.

![][image5]

## **ROI and Cost Benefits**

The deployment of this AI solution is projected to deliver a transformative financial impact. Over a three-year period, the company is expected to realize a total net benefit of $45,747,000, achieving a remarkable 708.9% return on investment. The initial AI deployment cost of $6,453,000 is projected to be recovered in just 4.45 months, driven by significant operational savings.

* Projected Total Net Benefit: $45,747,000 over 3 years  
* Projected Return on Investment (ROI): 708.9%  
* Projected Payback Period: 4.45 months  
* Projected Total Savings: $52,200,000 (from $36,000,000 in downtime savings and $16,200,000 in safety savings)  
* Projected Operational Improvements: 1% reduction in equipment downtime and a 2% reduction in safety incidents.

![][image6]

These projections highlight the substantial value driven by enhancing predictive maintenance and safety procedures. By focusing on integrating equipment data, the company can maximize its return, positioning itself as an industry leader in both efficiency and safety.

## **Eliminating Legacy RAG Pitfalls**

A core challenge for energy companies is how engineers phrase questions and the overwhelming volume of information within technical documents. Our AI solution addresses these issues by delivering a 51 percent improvement in the accuracy of retrieved information. It achieves this by focusing on the core intent of a query and guiding the system toward the most relevant content, thereby enhancing operational efficiency, safety compliance, and the general accuracy of remote site operations.

![][image7]

## **What We Did: Breaking Down the Framework**

Intel Gaudi 2 / Xeon accelerates LLM inference with high-throughput deep-learning cores, ideal for parallel processing of complex, multi-tiered technical and safety documentation. The Major Energy Company’s documents often contain nested specifications and acronym-heavy language. To enable real-time Q\&A, content was modularized with Blockify, then embedded as high-density vectors for instantaneous retrieval.

LLAMA 3, fine-tuned via Low-Rank Adaptation (LoRA) on a single Gaudi 2 core or Xeon Chip, achieved optimal quality by processing 8,000-character segments and generating 1,000 tokens per response with 100 parallel jobs.

### The Blockify workflow steps included:

1. Chunking the Text: The source documents were divided into smaller content chunks based on a proprietary algorithm. Those chunks were passed into the specially configured LLM, which output modular blocks of content. These blocks offer a robust taxonomy that can be reused or reassembled based on user needs.

![][image8]

2. Embeddings: These content blocks were converted into embeddings (vector representations)  
   to capture unique context and structure, enabling content-aware retrieval within AirgapAI.  
3. Retrieval and Response Generation: Based on user queries, the system retrieves relevant content from the Context-Aware Retrieval Database for accurate, contextually relevant responses.

This enhanced workflow allows instant recall of insights, strategies, policies, dynamically assembling content into diverse outputs using large language models. The result is real-time expertise, engagement, and personalized content in minutes, saving hours of manual work.

### Business Use Cases: Real-Time AI Inference in Action

* Technical Query Response \- assemble detailed responses to common technical questions about equipment specifications, maintenance schedules, or safety procedures in minutes while ensuring data privacy rules are met.  
* Safety Compliance Audits \- auto-populate incident reports with lineage-tracked safety procedures and regulatory precedents.  
* Internal & Partner Briefings \- produce legally compliant, publicly releasable marketing collateral for joint venture programs without exposing sensitive source data.  
* Field Operations Assistant \- field real-time questions from operators on protocol deviations, jurisdiction boundaries, or emergency response metrics entirely offline.  
* Training Procedure Authoring \- draft qualification training plans referencing historical incident outcomes or operational feedback in seconds.

### What This Means for You: Scalable AI Inference for Future Growth

By uniting Intel Gaudi 2 / Xeon and Iternal Technologies’ Blockify with the secure, offline capabilities of AirgapAI, Energy Companies can harness AI inference at scale, turning decades of unstructured operational data into actionable insights without ever exposing sensitive information to third-party clouds. With Intel Gaudi 2/Xeon, Blockify, and AirgapAI, a Major Energy Company can:

* Automate Data Ingestion & Curation \- process terabytes of legacy documentation while slashing inaccuracies.  
* Drive Hyper-Compliant Content \- ensure every generated paragraph respects privacy, legal, and departmental guidelines.  
* Accelerate Decision-Making \- surface trusted answers in seconds, compressing response times and boosting public trust.  
* Protect Operational Data \- keep all sensitive data within the company’s secure network, eliminating cloud-based exposure risks.

AI has moved from conceptual to operational in the energy sector. Whether generating a rapid-response internal communication, answering technical inquiries, or drafting operational procedures, Intel and Iternal deliver the secure, accurate, and scalable framework a Major Energy Company needs to maintain mission advantage.  









