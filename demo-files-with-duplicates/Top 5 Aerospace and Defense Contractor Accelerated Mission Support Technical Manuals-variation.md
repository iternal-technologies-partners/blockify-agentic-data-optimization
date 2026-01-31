# How a Top 5 Aerospace and Defense Contractor Accelerated Mission Support: Boosting LLM Accuracy by 78x for Technical Manuals

![][image1]

## Executive Summary

Maintenance, manufacturing, and field service performance hinges on technicians and operators getting the right instruction at the right time, in the right order, with the right cautions preserved.

Traditional retrieval-augmented generation (RAG) approaches fail this test because they ignore sequence and context. Equal-sized text chunks blend unrelated steps or fragment prerequisites and cautions from procedures they govern; this creates conditions for hallucination, operator confusion, and costly rework.

A Top 5 Aerospace and Defense contractor modernized how it ingests, structures, and serves its technical manuals using Blockify's Technical Manual Ingest model, deployed alongside Intel's datacenter and edge hardware. The Aerospace Company converted thousands of pages of ordered procedures into compact, validated "IdeaBlocks" that preserve step order, prerequisites, cautions, specs, and effectiveness; all the details that make a procedure safe and compliant in the real world.

## Results

* AI-ready instruction steps technicians and manufacturing teams can trust
* Measurable accuracy gains over traditional RAG
* Faster time-to-answer on the flight line and shop floor
* Lower compute and storage costs for downstream AI use

![][image2]

## Highlights

* **78x improvement** in LLM accuracy across the corpus vs. traditional RAG; more accurate than chunking; search precision improved approximately 52%
* **Step/sequence-ordered, context-rich IdeaBlocks** preserve prerequisites, cautions, torque specs, and effectivity; Step 4 never appears before Step 3 without the preceding warning or tool callouts
* **Offline, secure AI assistance at the edge** with AirgapAI on Intel AI PCs; vector retrieval and inference 2.2x faster on Intel NPU; scan approximately 10 million records in under 1.5 seconds
* **Processing scalability** from AI PCs to Gaudi 3 accelerators: from roughly 4,860 pages/month on a single Intel Core Ultra 7 265V to approximately 17.8 million pages/month on a single Gaudi 3 core (8X GPU Server)
* **Distilled single source of truth** approximately 2.5% of raw corpus size, reducing storage and accelerating retrieval
* **Mean time to the right instruction** dropped from multiple minutes to approximately 15 seconds, with downstream reductions in rework and improved asset readiness/throughput

## Context and Challenge

The Aerospace Company maintains complex airframes and produces mission-critical components across multiple facilities. Technical manuals arrive in mixed formats (PDFs, scanned appendices) with frequent updates and high stakes for errors.

![][image3]

Prior to Blockify, RAG attempts failed due to:

* **Loss of procedural order:** Prerequisites and specs split or merged incorrectly
* **Cautions/advisories adrift:** Important context often separated from governed steps
* **Confused or partial answers:** Plausible but out-of-order or irrelevant content returned
* **Governance and vendor lock-in fears:** CIO required readiness, low cost, data control, vendor-agnosticism, and full auditability

The Aerospace Company needed a model and workflow built for ordered step-by-step guides like technical documentation content: preserving sequence and adjacent context, with discrete, unambiguous instruction and trusted provenance; at scale and with secure, fast edge delivery.

![][image4]

## The Solution in Brief: Blockify + Intel + AirgapAI

Blockify's Technical Manual Ingest Model ingests, standardizes, and restructures procedural content into small, validated IdeaBlocks:

* A concise, unambiguous instruction capturing one idea
* Built-in Q&A anticipating natural-language field queries
* Rich metadata preserving order, provenance, effectivity, and source links

Auditable workflows orchestrate intake to publication. IdeaBlocks become the enterprise knowledge source for AI, search, and field portals; critical procedures get SME sign-off; non-critical content follows automated anomaly detection.

**Hardware:**

* **Data center:** Intel Xeon and Gaudi for ingestion
* **Edge:** AirgapAI runs 100% offline on Intel AI PCs/NPU acceleration

## Why Ordered Content Beats Chunked RAG

Procedures are a sequence of dependent operations. They are ordered, and order matters; prerequisites and cautions qualify downstream steps. Properties like torque values and effectivity are contextual and local.

Legacy Chunked RAG fails: steps and their qualifiers get separated, so the model may retrieve only part of a process.

Blockify's approach enforces step structure and context, preserving dependencies and reducing hallucinations; improving LLM answer accuracy by approximately 78x vs. traditional RAG.

## The Pipeline in Detail

![][image5]

### Intake and Collection

The initial phase of the pipeline focuses on the intake and collection of all relevant documentation. This involves gathering new and revised manuals, Engineering Change Notices (ECNs), bulletins, and guidelines. Once collected, the text is normalized and extracted, with careful preservation of tables, lists, and original formatting.

Throughout this process, essential metadata such as document IDs, classification, and access controls are retained to ensure complete provenance.

![][image6]

### Standardization to Structured Text

Following intake, the collected information undergoes standardization into a clean, hierarchical text format called Markdown. This step is critical for preserving list semantics and nesting, and the resulting structured text becomes the definitive source of truth for all subsequent parsing and validation activities.

### Ordered Chunking With Context

The standardization process leads to ordered chunking, where the content is split strictly along procedural boundaries rather than arbitrary tokens. Each individual step is then bundled with its adjacent context, including prerequisites, cautions, and verification steps, ensuring that each chunk is self-contained and operationally complete.

### Blockify Technical Manual Ingest

Each contextualized step is then converted into an "IdeaBlock," which represents a single operational idea. These IdeaBlocks are designed to be self-sufficient, clearly stating the necessary tools, specifications, and effectivity. They also embed Q&A sections to address common technician queries, such as the specific torque for an actuator bolt on a given tail number. Each IdeaBlock is enriched with comprehensive metadata, including document ID, heading, revision, step number, effectivity, timestamp, and a checksum, providing a complete audit trail. Through this process, the corpus is significantly distilled.

![][image7]

### Human-in-the-Loop Review

A crucial human-in-the-loop review process is implemented to maintain accuracy and quality. All critical procedures undergo 100% Subject Matter Expert (SME) review. For non-critical procedures, a combination of sampling and anomaly detection is utilized to ensure consistency and correctness.

### Publication and Distribution

Once approved, the IdeaBlocks are published and distributed to various platforms, including search systems, APIs, and field tools. Access controls are rigorously enforced, and full traceability to the origin and revision of each IdeaBlock is maintained. Every ingestion, review, and publication event is meticulously recorded, providing a complete audit trail.

![][image8]

## AirgapAI for Offline Edge Inference

For scenarios requiring offline access and enhanced security, AirgapAI is deployed on Intel AI PCs, leveraging their Core Ultra NPUs. This enables vector search and LLM inference to run locally, achieving 2.2x faster performance and processing approximately 10 million records in under 1.5 seconds. Critically, AirgapAI upholds ITAR/CMMC compliance by operating with zero external connectivity.

## Why the Hardware Matters

The choice of hardware is fundamental to the pipeline's efficiency and security. In the data center, Intel Xeon and Gaudi processors are utilized for high throughput. At the edge, Intel Core Ultra (NPU) in conjunction with AirgapAI provides local, secure, and fast inference capabilities. This intentional hardware selection ensures that throughput aligns with project milestones while maintaining a lean and secure operational environment.

## What Changed for Technicians and Operators

| Feature | Before (Generic/Untraceable Answers) | After (New System with IdeaBlocks) |
| ----- | ----- | ----- |
| Information Access | Reliance on generic or untraceable answers | Provides ordered IdeaBlocks with specific instruction steps |
| Response Detail | Limited | Each response includes clearly flagged specifications, tools, and effectivity; it also presents the preceding step (prerequisites and cautions) and the following step (verification and post-checks) |
| Anticipatory Q&A | Absent | Embedded Q&A within each IdeaBlock anticipates and addresses subsequent questions |
| Information Reliability | Low | Every answer provides a direct link back to the exact manual section and revision, fostering trust through fast, exact, and reliable information |
| User Experience | Frustrating, time-consuming | Significant improvements for technicians and operators in how they access information |

## Quantified Outcomes

The implementation of this system has yielded substantial quantitative improvements:

* **LLM Accuracy:** Improved by approximately 78 times, with IdeaBlock answers compared to those derived from equal-sized chunks
* **User Efficiency:** Users are now 52% more likely to find the correct information on their first attempt, and the mean time to answer has dramatically decreased from minutes to approximately 15 seconds
* **Corpus Optimization:** The entire corpus has been distilled to roughly 2.5% of its original size, leading to reduced rework and fewer misapplied steps, thereby enhancing readiness and throughput
* **Compute Efficiency:** Optimized through the use of the right hardware for scale (Gaudi), cost (Xeon), and offline/fast inference (Core Ultra/NPU)

## People, Process, and Governance Changes

### Maintenance Leadership

Maintenance leadership has played a pivotal role in standardizing the validation and capture of procedures. They have enforced the use of the new pipeline for all new manuals and revisions and have defined clear sign-off tiers, including SME review, sampling, and anomaly triggers.

![][image9]

### Engineering Tech Publications

The Engineering Tech Publications team shifts its focus to reviewing and stewarding auto-generated IdeaBlocks. Their primary responsibilities now revolve around ensuring operational clarity, verifying effectivity, and disambiguating complex instructions. Rich metadata provides enhanced traceability and auditability for all documentation.

### Manufacturing Engineering and Quality

For Manufacturing Engineering and Quality, the system provides structured, step-level digital instructions. This enables faster adaptation of instructions in response to ECNs and other change orders, ensuring precise alignment of inspection and verification processes with revised steps.

### Change Management

Change management efforts have included training frontline personnel in conversational AI and manual verification techniques. Continuous feedback loops have been instrumental in refining Q&A and phrasing, and trust has been built through transparency and the preservation of instructional sequence.

### Security, Compliance, and Auditability

The system is built on a foundation of robust security, compliance, and auditability features. Every IdeaBlock includes provenance data such as document ID, revision, step, effectivity, and a checksum, allowing for one-tap verification.

Access control is role and classification-based, with all events meticulously logged. Review gates, including tiered SME sign-off and sampling with anomaly detection, ensure quality and compliance.

Crucially, all retrieval and offline inference operations are performed on Intel AI PCs, ensuring no external exposure and upholding the highest levels of data security.

## Scenarios in Practice

### Aircraft Servicing: Flight Line

The Aircraft Servicing scenario highlights the contrast between outdated and modern approaches to technical manual usage. It demonstrates how Blockify can significantly improve efficiency and safety compared to relying on imprecise, traditional methods.

| Scenario | Before | After |
| ----- | ----- | ----- |
| Flight Actuator Swap | Scanning a PDF or relying on a vague chatbot answer for torque sequence and cautions | Crew chief receives three precise IdeaBlocks, detailing exact specifications, prerequisites, and verification steps, along with explicit effectivity information and a source link for the torque sequence and associated cautions for a flight actuator swap |

![][image10]

### Machine Part Production: Shop Floor

When an engineer updates a CNC process and inspection point, the system responds by ingesting and republishing the revised steps as new ordered IdeaBlocks. The Manufacturing Execution System (MES) then delivers the exact sequence and relevant Q&A directly to the shop floor.

### Shop Floor Assistance: Field Query

If a worker queries, "What's the prep cleaning procedure for pump housing, rev H?", the assistant immediately returns the exact step, prerequisites, the next action, relevant Q&A, and a direct link to the specific manual and revision.

### Technical Publications Team

For the technical publications team, facing a flood of revisions from multiple offices, the process is streamlined. They now review auto-generated IdeaBlocks, focusing on clarity and effectiveness, and can approve and republish updates in seconds.

## Implementation Timeline and Operating Model

### Weeks 1-2: Mobilize and Govern

The initial two weeks focus on mobilization and governance. This involves identifying high-value manuals and procedures, defining rules for tiers, review, and access, building a cross-functional team, and setting up necessary integrations.

### Weeks 3-6: Pilot and Validate

During weeks three through six, a pilot ingestion is conducted, and the system is validated in the field. This phase includes connecting to enterprise portals and systems, establishing baseline measurements, and comparing them against the pilot results.

### Weeks 7-10: Scale and Operationalize

The final phase, spanning weeks seven to ten, focuses on scaling and operationalization. More manuals are ingested, leveraging Gaudi acceleration. Sign-off procedures, sampling, and anomaly detection are fully implemented, and the system is published to the AirgapAI edge. Ongoing monitoring for accuracy, adoption, and time-to-answer ensures continuous improvement.

## Quantifying ROI

| Area | Improvement/Metric | Value Added |
| ----- | ----- | ----- |
| Time-to-Answer | Reduced from minutes to approximately 15 seconds | Hundreds of daily queries creating significant value-added time |
| Accuracy and Compliance | Approximately 52% more accurate answers, 78x LLM accuracy improvement | Fewer errors and less rework |
| Readiness and Throughput | Faster aircraft turnaround, smoother manufacturing processes | Improved operational efficiency |
| Risk | Offline operation, provenance tracking, robust access controls | Minimized potential for breaches or misuse |

## How and Why Accuracy Improved

The dramatic improvement in accuracy can be attributed to three critical choices made during the system's development:

* The implementation of **ordered chunking with adjacent context** ensures that step boundaries define the splits, and each chunk carries its prerequisites and verifications
* Adopting the principle of **"one idea per block"** significantly shrinks ambiguity, allowing models to cite vetted steps rather than blended or multi-concept blobs
* The **embedded Q&A at the block level** uses technician-targeted phrasing to steer queries and retrieval, effectively bridging colloquial language with formal documentation

These combined strategies have drastically reduced hallucination and misinterpretation, resulting in 78x LLM accuracy improvement over standard RAG.

## Scalability in Practice

The system demonstrates impressive scalability in practice. For instance, a 1,741-page manual comprising 1,096,830 words is transformed into 1,305 IdeaBlocks. Processing time for such a manual is dramatically reduced from 548,415 seconds on a Core Ultra 7 265V AI PC to just 270 seconds on a Gaudi 3 core.

Monthly capacity for manual processing varies significantly based on hardware, ranging from 4,860 pages on a Core Ultra 7 265V to 17.8 million pages with an 8x Gaudi 3 setup.

### What We Did: Breaking Down the Framework

![][image11]

#### 1. Ingestion, Distillation, Taxonomy

The framework begins with the ingestion, distillation, and taxonomy of information. This involves extracting essential information, normalizing it, and meticulously preserving its original structure. Redundancy and obsolete content are eliminated, and the corpus is distilled. The result is an indexed, contextual hierarchy that forms the foundation of the knowledge base.

#### 2. Embeddings and Retrieval

IdeaBlocks are then converted into structured vectors. Similarity for retrieval is carefully tuned to prioritize order and effectivity, in addition to semantic content. AirgapAI search enables sub-second, context-rich results, ensuring rapid and relevant information retrieval.

#### 3. Response Generation Strategy

The response generation strategy involves assembling answers from the retrieved IdeaBlocks and their embedded Q&A. Free-form generation is constrained and always cited, ensuring accuracy and traceability. Every answer includes a one-tap link to its source and revision, empowering users with instant verification.

### Risk Management and Safety Outcomes

The system significantly enhances risk management and safety outcomes. It provides irrefutable proof of which instruction was visible to whom, when, and under what classification. Every change, from source to field, is traceable, allowing for exact answers to audit and regulatory queries. Access and classification controls are rigorously enforced down to the block, device, and user level, safeguarding critical information.

### Cultural Impact: From Scanning to Executing

The cultural impact of this system is profound, shifting user behavior from simply scanning PDFs to confidently executing the next step. This leads to fewer interruptions, a reduction in errors, and fewer quality assurance issues, fostering a more efficient and reliable operational environment.

## Conclusion

The result is the transformation of sprawling technical text into a compact, trusted, and readily searchable knowledge base.

By adopting Blockify's ingest model and integrating with Intel and AirgapAI, a Top 5 Aerospace and Defense Contractor has achieved remarkable outcomes.

The broader implications are clear: readiness and throughput are directly contingent on having the correct, traceable instructions available at the precise moment they are needed.

Traditional RAG is demonstrably insufficient for this challenge.

Ordered, structured content; accelerated by Blockify and the appropriate compute resources, deployed at the right location; represents the essential blueprint for trusted AI solutions within the aerospace and defense sectors.
