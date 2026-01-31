**Supporting the US Military through improving LLM Accuracy by 78x with Blockify and AirgapAI**

AI is rapidly becoming a strategic asset for the US military. To stay ahead of potential threats it is more important than ever that the US military is able to access the right information, at the right time, in a safe, secure, and trusted manner – all while being confident in the veracity of the information being provided. 

Together Intel and Iternal Technologies have partnered to provide a unique solution to support the US military, addressing many of the common challenges associated with adoption of AI technologies, such as hallucinations, data curation, governance, and access control provisioning of critical data.

Given the requirement to harness massive amounts of data to stay competitive, AI inference – the ability to generate real-time insights from large datasets – is becoming essential. 

Pairing highly performant data center solutions like Gaudi 2 & Blockify® for data preparation and optimization, with edge based Intel NPU chips & AirgapAI™ software for local inference capabilities and data summarization, an end to end solution can deliver substantial competitive advantage.

**Why AI Inference Matters and Why You Should Care**

AI inference is more than just running a trained model; it goes beyond simple data queries. It allows you to extract real-time, accurate, and contextually relevant insights from unstructured data at scale. 

In the context of military operations, data preparation and optimization is usually a complex and time consuming process. Without an effective and real time approach to content lifecycle, military operations risk utilizing an AI that will never be fully accurate. It’s garbage in, garbage out. And if you can’t trust your AI to always be correct, then you can’t ever trust it to be correct because the mistakes are unpredictable.

Intel and Iternal used AI to bring structure to unstructured operational documents such as strategy, policies, procedures, and manuals, through an advanced data ingestion and optimization approach, powered by Blockify. 

The result is a highly accurate and optimized dataset that includes greater governance, control, management, and quality of data while simplifying human control and accuracy. These improvements combine to virtually eliminate all AI hallucinations associated with RAG and improve LLM accuracy by approximately 78x (7800%) compared to a traditional RAG pipeline.

![][image1]

Blockify’s patented approach creates a single source of truth. Distilling your information, content, and knowledge down to 2.5% of the original size, allowing for easy content lifecycle management.

**A Summary of the AI Inference Solution** 

**Blockify Data Ingestion with Gaudi**

Leveraging Intel Gaudi 2 AI accelerators, and Iternal’s patented data ingestion solution, Blockify. The customer was able to provide documents and information sources to ingest, and optimize for an improved large language model inferencing pipeline when paired with retrieval augmented generation (RAG).

* **Processing Time**: The documents were processed at an average speed of 900 words per second.

* **Accuracy**: We increased retrieval-augmented generation (RAG)-based LLM accuracy by 40 times and improved vector search precision by 51%.

* **Inference Speed**: Achieved 0.68 inferences per second, with a throughput of 5,404 bytes per second.

These results came from an efficient pipeline combining Iternal’s Blockify data ingestion technology with the powerful Intel Gaudi 2 AI Accelerators. Iternal’s Blockify deduplication and data cleansing solution was then applied to create an optimized data taxonomy of modular content indexed for dynamic contextual responses. 

This three-pronged ingestion, distillation, and taxonomy approach drastically optimized how a RAG based system could interact with, search, and utilize the data to power a large language model. 

This use case demonstrates how scalable AI inference hardware paired with highly capable software can solve real-world problems, particularly in industries where speed, accuracy, and scalability are vital. 

**AirgapAI \- Inferencing at the Edge with Intel NPU**

Optimizing a dataset is only as useful as the “in-field” applicability. AirgapAI is a powerful, network independent AI solution designed to run locally on an AI PC. 

AirgapAI can be used to support military operations by running large language model locally on Intel NPU chips. AirgapAI enables mission-critical tasks in environments requiring the highest levels of security.

* **Processing Time**: Vector Search and Inference is approximately 2.2x faster using Intel NPU.

* **Accuracy**: We increased retrieval-augmented generation (RAG)-based LLM accuracy by 40 times and improved vector search precision by 51%.

* **Retrieval Speed**: Achieved vector search of ≈6.6 Million records in 1 second.

AirgapAI supports running any open-source large language model, including custom fine-tunes. When paired with Blockify, agencies can utilize specialized role based guardrails and curated datasets specific to their operational requirements. This approach ensures a safe and highly relevant AI experience for tasks such as analyzing intelligence reports, generating detailed documentation, and making real time decisions on robust strategy briefs.

After outputting the dataset from Blockify, we loaded the newly created Blockified dataset onto the AI PC and into AirgapAI, where in-field inference was conducted. AirgapAI utilizes Intel chips to scan through up-to 10 million records in the vector database in just under 1.5 seconds. After identifying the right information for the user query, a LLM inference is initiated to summarize the key information into a user digestible answer.

By operating completely offline, AirgapAI upholds stringent data protection standards—no external connection is required, minimizing potential vulnerabilities and ensuring mission-critical information remains strictly confidential. Personnel can rely on AirgapAI to quickly respond to FAQs, create situational reports, produce policy documentation, translate content across languages, and more.

With AirgapAI, US government and military teams can securely harness the power of AI-driven language models to support rapid decision-making, streamline documentation, and safeguard sensitive information—all within a fully controlled, air-gapped environment.

One of the primary issues with legacy RAG is the semantic differences in how unique user questions are represented in vector space, paired with a dilution of vector accuracy by incorporating extraneous information in a given chunk of text. Blockify eliminates these issues by providing a 51% improvement in vector accuracy, and a dedicated query element to aid in retrieving the right information.

![][image2]

**What We Did: Breaking Down the Framework**

For AI inference to perform at scale, robust infrastructure is essential. Intel Gaudi 2 was used to accelerate the inference of large language models (LLMs). Gaudi 2 is designed for deep learning workloads, and its efficiency in both training and inference made it the ideal choice for this inference project. Its architecture allows for high throughput, making it perfect for tasks that require parallel processing of complex, layered data—like military documents.

Military documentation are known for their length, complexity and frequent use of layered acronyms where context is key. To enable real-time retrieval and answer detailed questions, the documentation was pre-processed and indexed using Iternal’s Blockify technology to modularize content into manageable blocks. These blocks are then deduplicated, distilled, indexed, tagged, and merged into a final output dataset. The output dataset can then be packaged into a secure file which can be loaded onto an edge device running AirgapAI.  

The LLAMA 3 LLM was prepared and fine-tuned using Low-Rank Adaptation (LoRA) and run on a single Intel Gaudi 2 core. Through extensive optimization testing across documents from all industries and use cases, Iternal and Intel determined the optimal quality of output and compute performance could be achieved by running 8,000-characters segments and generating 1,000 tokens per query output with 100 parallel jobs. 

The Blockify workflow steps included:

1. **Chunking the Text:**  The source documents were divided into smaller content chunks based on a proprietary chunking algorithm, the chunks are passed into the specially configured LLM where modular blocks of content are output. These blocks have a robust taxonomy that can be reused or reassembled based on user needs.

![][image3]

2. **Embeddings**: These content blocks were converted into embeddings (vector representations) to capture their unique context and structure, enabling content-aware retrieval within AirgapAI.

3. **Retrieval and Response Generation**: Based on user queries, the system retrieves relevant content from the Context-Aware Retrieval Database for accurate, contextually relevant responses. 

This enhanced workflow enabled the system to instantly recall specific insights, acronyms, strategics, and procedures with the capability to dynamically assemble content into different structured outputs using large language models. 

The result? Real-time expertise, engagement, and personalized content in just a few minutes – achievement that traditional methods would require 48 human hours to accomplish. output that would otherwise be unattainable.

**Benchmark Results**:

A corpus of approx. 11 million words was processed in approximately 2 hours. The ability to process 5 million pages of text per month on a single Gaudi 2 core demonstrates the scalability and efficiency of the approach.

**Total Time**: ≈2.04 hours

**Total Responses**: ≈63,953

This process wasn’t just about speed; it was about improving accuracy while minimizing issues like AI hallucinations. Blockify increased the precision of vector searches and RAG models, ensuring that the system retrieved the most relevant, contextually accurate information from the dataset. 

**Business Use Cases: Real-Time AI Inference in Action**

The implications for broader expansion of this technology in support of the US military is extensive. 

* **Intelligence Reports:** By combining Intel Gaudi 2 acceleration with Iternal’s Blockify technology, intelligence analysts can swiftly process vast amounts of operational data to extract precise insights. AirgapAI ensures these analyses remain both secure and accurate in real-time, even in disconnected environments.

* **Strategy Documents:** With Blockify’s chunking and deduplication creating a single source of truth, strategy briefs can be modularized for quick updates and cross-referencing. Intel Gaudi 2 acceleration delivers near-instant recall of critical information, while AirgapAI ensures mission-critical plans stay available in an air-gapped environment.

* **Policy and Procedure Documents:** Blockify ingests and distills detailed policy materials into easily searchable content blocks, significantly reducing risk of error or misinterpretation. Paired with Gaudi 2 and AirgapAI, organizations achieve high-speed, secure retrieval of vital documents for immediate and compliant decision-making.

* **Repair and Maintenance Manuals:** By converting lengthy manuals into concise, context-rich segments, field technicians can instantly access the most relevant procedures. Gaudi 2’s processing power and AirgapAI’s local inference enable secure, offline retrieval that keeps operations running smoothly, even in remote or bandwidth-limited scenarios.

For military operations the ability to retrieve accurate, contextually rich data in real time isn’t just an operational advantage—it’s a strategic one. By eliminating the operational burden of managing AI systems, teams can focus on mission.

**What This Means for You: Scalable AI Inference for Future Growth**  

Building on the proven success of Intel Gaudi 2 and Iternal Technologies’ Blockify, enterprises and government agencies alike can now harness AI inference at scale with minimal infrastructure overhead. Teams can seamlessly deploy massive AI workloads in secure or fully air-gapped environments—turning unstructured data into real-time, actionable insights without sacrificing accuracy or speed.  

Together Intel and Iternal’s integrated technologies allow you to:  

* **Automate Data ingestion and Curation:** Rapidly process and distill large datasets, ensuring you get accurate answers without hallucinations.    
* **Drive Personalized Experiences:** Tailor information in a reliable way based on the operational requirements of each mission or command.    
* **Enable Faster Decision-Making:** Confidently retrieve and synthesize trusted information to make critical choices in seconds rather than hours.  

With refined data pipelines and robust inference infrastructure available, AI has moved from conceptual to operational across industries. Whether you’re streamlining policy documents, evaluating strategy documents, or generating real-time intelligence reports, the tools and frameworks are in place to meet your needs. 



