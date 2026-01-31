# Supporting Major Food Retailer Employee Operations through Improving LLM Accuracy by 78x with Blockify and AirgapAI

Artificial intelligence is rapidly becoming a strategic asset for major food retailers. To streamline operations and empower employees, a major food retailer must quickly enable thousands of employees with HR onboarding policies and procedures that feel individually tailored yet remain fully compliant with company policies and state labor laws across 9 states and 443 stores in the USA. 

Accelerating access to employee HR resources at scale requires instant access to the right information, at the right time, in a safe, secure, and trusted manner—while being certain each insight is factually correct and never exposes sensitive employee data. 

Intel and Iternal Technologies have partnered to provide a unique solution that addresses the most common challenges food retailers face when adopting AI technologies: hallucinations, data curation, governance, and ultra-granular access-control of confidential employee information. 

Pairing highly-performant data-center solutions like Gaudi 2 & Blockify® for data preparation and optimization, with edge-based Intel NPU chips & AirgapAI™ software for 100 percent local inference, delivers a major food retailer an end-to-end platform for hyper-personalized employee enablement; without ever letting sensitive data leave the corporate network.

## **Benchmark Results:**

A corpus of 81 pages of employee handbook materials (approx. 21,297 words) was processed in about 42 seconds. The ability to process 5 million pages of text per month on a single Gaudi 2 core demonstrates the scalability and efficiency of this approach.

* Total Time: ≈41.47 seconds  
* Total Responses: ≈73

This process wasn’t just about speed; it was about enhancing accuracy while minimizing issues like AI hallucinations. Blockify’s approach increased the precision of vector searches and RAG models, ensuring that the system retrieved the most relevant, contextually accurate information from the Retailer’s knowledge base.

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







