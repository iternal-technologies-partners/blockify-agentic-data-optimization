# Supporting University Alumni Relations through Improving LLM Accuracy by 78x with Blockify and AirgapAI

Artificial intelligence is rapidly becoming a strategic asset for higher-education advancement teams. To strengthen lifelong bonds and inspire new endowments, The University must reach more than 70,000 living alumni and thousands of current parents and potential donors with messages that feel individually crafted yet remain fully compliant with FERPA, and state privacy mandates. 

Doing this at scale requires instant access to the right information, at the right time, in a safe, secure, and trusted manner—while being certain each insight is factually correct and never exposes sensitive donor data.

Intel and Iternal Technologies have partnered to provide a unique solution that addresses the most common challenges higher-education advancement offices face when adopting AI technologies: hallucinations, data curation, governance, and ultra-granular access-control of confidential donor information.

Pairing highly-performant data-center solutions like Gaudi 2 & Blockify® for data preparation and optimization, with edge-based Intel NPU chips & AirgapAI™ software for 100 percent local inference, delivers The University an end-to-end platform for hyper-personalized outreach; without ever letting sensitive data leave campus.

## **Benchmark Results:**

A corpus of 55 pages of university alumni materials decks and white papers (approx. 16,782 words) was processed in about 32 seconds. The ability to process 5 million pages of text per month on a single Gaudi 2 core demonstrates the scalability and efficiency of this approach.

* Total Time: ≈32.68 seconds  
* Total Responses: ≈61

This process wasn’t just about speed; it was about enhancing accuracy while minimizing issues like AI hallucinations. Blockify’s approach increased the precision of vector searches and RAG models, ensuring that the system retrieved the most relevant, contextually accurate information from the University’s knowledge base.

## **Why AI Inference Matters and Why You Should Care**

AI inference is more than processing a trained model; it goes beyond mail-merge and list segmentation. It empowers The University's Advancement and Alumni Relations teams to extract real-time, accurate, and contextually relevant insights from decades of scholarship, giving histories, event attendance, and engagement notes at scale.

Traditional advancement systems require manual segmentation and generic messaging. Without an effective AI-driven content lifecycle, The University risks sending communications that feel impersonal or, worse, inadvertently reveal private donor details. Garbage in, garbage out \- and if you can’t trust your AI to be correct every time, you can’t trust it at all because the mistakes are unpredictable.

![][image1]

Intel and Iternal used AI to bring structure to unstructured engagement artifacts, annual fund letters, stewardship reports, endowed-chair agreements, gift-processing policies, event recaps, and handwritten prospect notes; through an advanced data-ingestion and optimization approach powered by Blockify.

![][image2]

The result is a highly accurate and optimized dataset that includes greater governance, control, management, and quality of data while simplifying human oversight. These improvements virtually eliminate AI hallucinations in Retrieval-Augmented Generation (RAG) workflows and improve LLM accuracy by approximately 78x (7,800 percent) compared to a traditional RAG pipeline.

Blockify’s patented approach creates a single source of truth. Distilling The University's accumulated institutional knowledge down to 2.5 percent of the original size allows for easy content-lifecycle management.

## **A Summary of the AI Inference Solution**

### Blockify Data Ingestion with Gaudi

Leveraging Intel Gaudi 2 AI accelerators and Iternal’s patented Blockify solution, The University's Advancement Services team ingests and optimizes thousands of documents for an improved LLM inferencing pipeline paired with RAG.

* Processing Time: Vector search and inference is approximately 2.2x faster using Intel NPU.  
* Accuracy: Retrieval-augmented generation (RAG)-based LLM accuracy increased by 40 times, and vector search precision improved by 51%.  
* Retrieval Speed: Achieved vector search of ≈6.6 million records in 1 second.

These results stem from an efficient pipeline combining Iternal’s Blockify deduplication and data-cleansing with the powerful Intel Gaudi 2 AI Accelerators. Blockify outputs an optimized taxonomy of modular content indexed for dynamic contextual responses:

* Ingestion and de-duplication of 30+ years of donor marketing, alumni programs, FAQs, agreements, campaign collateral, and event transcripts.  
* Distillation into concise, reusable blocks tagged with donor-privacy attributes and FERPA classifications.  
* Creation of a secure, portable dataset ready for air-gapped deployment.

### AirgapAI – Inferencing at the Edge with Intel NPU

Optimizing a dataset is only as useful as its “in-field” applicability. AirgapAI is a powerful, network-independent AI solution designed to run locally on any Intel-equipped AI PC inside The University's firewalled environment.

Stored securely on the local device, the Blockified dataset never leaves The University’s property. Advancement Officers can run any open-source LLM, including custom fine-tunes that understand University alumni-specific vernacular, directly on their laptops while meeting with donors across the globe, even without internet connectivity.

After loading the dataset onto an AirgapAI-enabled AI PC, the system can scan 10 million vector records in under 1.5 seconds, retrieve the most relevant donor stories, and generate a bespoke stewardship note or proposal addendum on the spot—all without touching the public cloud.

By operating completely offline, AirgapAI upholds stringent data-protection standards, no external connection is required, minimizing potential vulnerabilities and ensuring confidential gift agreements remain strictly private. Officers can quickly respond to donor inquiries, craft event follow-ups, translate stewardship messages into multiple languages, and more.

One of the primary issues with legacy RAG is the semantic drift between how unique donor questions are represented in vector space, compounded by vector dilution when extraneous details pollute a chunk of text. Blockify eliminates these issues by delivering a 51 percent improvement in vector accuracy and by embedding a dedicated query element that guides retrieval toward the most appropriate content.  
![][image3]

## **What We Did: Breaking Down the Framework**

For AI inference to perform at scale, robust infrastructure is essential. Intel Gaudi 2 accelerated the inference of large language models (LLMs). Gaudi 2 is purpose-built for deep-learning workloads; its architecture allows for high throughput—ideal for parallel processing of complex, layered data such as campaigns spanning multiple decades.

The University's advancement materials often contain high degrees of dense context that would confuse traditional RAG systems. To enable real-time retrieval and deliver detailed responses, these documents were pre-processed and indexed using Iternal’s Blockify to modularize content into manageable blocks. Blocks are deduplicated, distilled, indexed, tagged, and merged into a final output dataset packaged for edge deployment.

The LLAMA 3 LLM was fine-tuned via Low-Rank Adaptation (LoRA) and run on a single Intel Gaudi 2 core. 

After extensive testing, Iternal and Intel determined optimal output quality and compute performance when processing 8,000-character segments, generating 1,000 tokens per query with 100 parallel jobs.

### The Blockify workflow steps included:

1. Chunking the Text: The source documents were divided into smaller content chunks based on a proprietary algorithm. Those chunks were passed into the specially configured LLM, which output modular blocks of content. These blocks offer a robust taxonomy that can be reused or reassembled based on user needs.

![][image4]

2. Embeddings: These content blocks were converted into embeddings (vector representations) to capture unique context and structure, enabling content-aware retrieval within AirgapAI.  
3. Retrieval and Response Generation: Based on user queries, the system retrieves relevant content from the Context-Aware Retrieval Database for accurate, contextually relevant responses.

This enhanced workflow allows the system to instantly recall specific insights, marketing strategies, service offerings, and proposals, with the ability to dynamically assemble content into diverse structured outputs using large language models.

The result? Real-time expertise, engagement, and personalized content in minutes \- something that would otherwise require hours of manual research and compilation.

## **Business Use Cases: Real-Time AI Inference in Action**

The implications for broader expansion of this technology across The University are extensive.

* Personalized Alumni Newsletters: Combine Blockify and AirgapAI to craft unique emails that highlight class-specific events, research breakthroughs, and giving opportunities, all vetted for donor-preference tags.   
* Major-Gift Proposals: Instantly assemble endowment agreements featuring tailored impact statements, scholarship details, and naming-rights language, ensuring compliance with The University's gift-acceptance policies.  
* Stewardship & Annual Reports: Generate individualized “thank-you” letters that reference a donor’s specific scholarship recipient or funded research project, complete with photos and impact metrics.  
* Campaign Event Briefings: Before a stadium ribbon-cutting or annual gala, advancement officers can pull personalized briefing packets that summarize each VIP’s lifetime giving, preferred talking points, and dietary restrictions—completely offline.  
* Scholarship Matching: Match newly admitted students to potential scholarship funds in real time, using AI-driven analysis of donor criteria and student profiles while ensuring FERPA compliance.

### What This Means for You: Scalable AI Inference for Future Growth

By uniting Intel Gaudi 2 and Iternal Technologies’ Blockify with the secure, offline capabilities of AirgapAI, higher-education institutions can harness AI inference at scale, turning decades of unstructured advancement data into actionable insights without ever exposing sensitive information to third-party clouds.

### Together, Intel and Iternal help Universities:

* Automate Data Ingestion & Curation: Rapidly process and distill mountains of stewardship documents and donor records, ensuring you get accurate answers without hallucinations.  
* Drive Hyper-Personalized Experiences: Tailor every alumni interaction \- from newsletters to event invites \- based on individual affinity and past engagement.  
* Enable Faster Decision-Making: Confidently retrieve and synthesize trusted information to craft proposals and acknowledgments in seconds rather than hours.  
* Protect Donor Trust: Keep all sensitive data, giving histories, contact details, donor preferences, inside your firewall at all times.

With refined data pipelines and robust inference infrastructure now available, AI has moved from conceptual to operational in higher education. Whether you’re cultivating the next nine-figure endowment, stewarding first-time donors, or inspiring future generations of students, the tools and frameworks are in place to meet your needs. Securely, accurately, and at scale.  





