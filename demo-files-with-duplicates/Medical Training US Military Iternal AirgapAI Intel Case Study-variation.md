# **Supporting US Military Medical Teams: Improving LLM Accuracy by 78x with Blockify and AirgapAI**

The mission is clear: deliver the right information at the right time to those who protect and heal. AI is rapidly becoming a strategic asset for the US military, and for commands responsible for medical training and education, the stakes could not be higher. In environments where seconds determine outcomes and precision determines survival, the veracity of AI-generated information is paramount.

Military medical training institutions face a distinct challenge. The volume of information is immense; the complexity is formidable; the margin for error is nonexistent. Harnessing AI offers significant operational advantages: personalizing triage training simulations that mimic real medical scenarios, performing in-field data collection that transforms automatically into post-scenario briefings, rapidly analyzing new medical research to update protocols, and ultimately improving quality of care for personnel on the field.

Together, Intel and Iternal Technologies have partnered to deliver a solution that confronts the most common challenges associated with AI adoption in the military medical context: hallucinations in AI models, data curation complexity, governance requirements, and lifecycle management to maintain veracity over time for critical medical data.

The requirement is straightforward in concept but demanding in execution. Medical teams must harness massive amounts of data, from research publications and treatment guidelines to field-improvised protocols, and generate real-time insights from large datasets. This enables personalized and dynamic training simulations, accurate in-field decision support, and continuous updates to evolving medical protocols.

Pairing highly performant data center solutions like Gaudi 2 and Blockify for data preparation and optimization, with edge-based Intel NPU chips and AirgapAI software for local inference and medical data summarization, delivers an end-to-end solution that provides substantial mission advantage for the US military's medical training and education branch.

## **Benchmark Results**

To demonstrate the ability to extract key information from a robust medical dataset, a collection of field manuals for medical triage were selected, with topics ranging from blast trauma to nuclear and biological treatment. Over 1,100 pages of text (approximately 429,276 words) were processed in around 6 minutes; this scalability and efficiency enables the processing of up to 5 million pages of medical text per month on a single Gaudi 2 core.

* **Total Time**: Approximately 6 minutes  
* **Total Responses**: Approximately 2,495 requests

Speed alone is insufficient. The process was designed to improve accuracy while minimizing issues like AI hallucinations. Blockify increased the precision of vector searches and RAG models, ensuring that the system retrieved the most relevant, contextually accurate medical information.

![][image1]

## **Why AI Inference Matters**

AI inference extends beyond running a trained model; it enables the extraction of real-time, accurate, and contextually relevant insights from unstructured data at scale. For the military medical community, this capability translates into tangible operational improvements:

* **Personalizing medical triage training simulations:** Trainees interact with AI-driven, realistic medical scenarios, practicing triage and treatment protocols with immediate feedback via intelligent AI coaching.  
* **In-field data collection and post-scenario briefings:** Medics record voice notes on the spot, and AI automatically transforms them into concise after-action reports ready for use during transport or at a medical facility.  
* **Rapidly incorporating new medical knowledge:** Summaries of the latest scientific publications or treatment breakthroughs can be ingested and integrated into operating procedures quickly to improve quality and effectiveness of care.  
* **Reviewing and updating medical treatment documentation:** Treatment protocols can be instantly cross-referenced with the latest guidelines, ensuring accurate and consistent care delivery.  
* **Drafting and developing new treatment protocols and education materials:** AI-driven synthesis of the most recent medical research expedites the creation of new courses and guidelines for medics and trainees.

For medical teams operating in the field, hallucinations via AI are dangerous. Therefore more emphasis must be placed on data preparation and optimization, which is typically time-consuming. Without a robust, real-time approach to organizing content, the risk remains that an AI tool could provide inaccurate or incomplete medical advice. Trust is essential; you must be able to rely on AI accuracy especially when medical life or death situations are involved.

Intel and Iternal used Blockify to bring structure to unstructured operational and medical documents, including treatment protocols, triage guidelines, research papers, and field manuals, through Iternal's patented advanced data ingestion and optimization approach running on Intel Gaudi.

The result is a highly accurate and optimized dataset that streamlines governance, control, and data quality while simplifying human oversight. These improvements combine to virtually eliminate AI hallucinations associated with RAG (Retrieval-Augmented Generation) and improve Large Language Model (LLM) accuracy by approximately 78x (7,800%) compared to a traditional RAG pipeline.

![][image2]

Blockify's patented approach creates a single source of truth for medical content where content lifecycle management and governance can be applied to constantly evolving information as new procedures and medical technologies are developed. Blockify distills information down to 2.5% of its original size, simplifying the content lifecycle and eliminating redundancies between different documentation that can cause AI hallucinations. This makes it far easier for military training commands to manage, revise, and distribute official medical guidance, which is especially relevant when continuous updates are required.

## **A Summary of the AI Inference Solution**

### **Blockify Data Ingestion with Gaudi**

Leveraging Intel Gaudi 2 AI accelerators and Iternal's patented data ingestion solution, Blockify, military medical training teams can ingest and optimize medical documents and guidelines to significantly improve downstream LLM performance when paired with retrieval-augmented generation (RAG).

![][image3]

* **Processing Time**: Documents processed at an average speed of 900 words per second.  
* **Accuracy**: Retrieval-augmented generation (RAG)-based LLM accuracy increased by 40 times, with vector search precision improved by 51%.  
* **Inference Speed**: Achieved 0.68 inferences per second, with a throughput of 5,404 bytes per second.

These results emerged from an efficient pipeline combining Iternal's Blockify data ingestion technology with the powerful Intel Gaudi 2 AI Accelerators. Blockify deduplicates and cleanses data, creating an optimized data taxonomy of modular content indexed for dynamic contextual responses; this approach is especially valuable for large volumes of medical guidelines and research studies.

This three-pronged approach of ingestion, distillation, and taxonomy drastically optimized how a RAG-based system could interact with, search, and utilize medical data to power a large language model.

This use case demonstrates how scalable AI inference hardware paired with highly capable software can solve real-world challenges, especially where speed, accuracy, and scalability are vital, such as providing real-time solutions for medical training and in-field care.

### **AirgapAI: Inferencing at the Edge with Intel NPU**

Optimizing a dataset matters only if it has in-field applicability. AirgapAI is a powerful, network-independent AI solution designed to run locally on an AI PC, leveraging Intel NPU chips for in-field inference capabilities.

![][image4]

For US Military personnel tasked with medical training and support, AirgapAI enables mission-critical tasks such as triage guidance, localized medical reference checks, and the ability to debrief or update protocols offline in secure, air-gapped environments.

* **Processing Time**: Vector Search and Inference is approximately 2.2x faster using Intel NPU.  
* **Accuracy**: Retrieval-augmented generation (RAG)-based LLM accuracy increased by 40 times, and vector search precision improved by 51%.  
* **Retrieval Speed**: Approximately 6.6 million records in 1 second.

AirgapAI supports any open-source large language model, including custom fine-tunes focused on military medicine. When paired with Blockify, medical teams can utilize specialized, role-based guardrails and curated datasets specific to medical operations. This ensures a safe and highly relevant AI experience for tasks such as analyzing medical intelligence reports, generating documentation, and making real-time decisions on triage protocols.

After outputting the dataset from Blockify, the newly created Blockified dataset is loaded onto the AI PC running AirgapAI, where in-field inference is conducted entirely offline. For sensitive medical information, this is critical in ensuring mission confidentiality. Personnel can rely on AirgapAI and medical datasets to quickly respond to queries, compile situational medical reports, produce or update policy documentation, and translate medical content across languages.

By operating completely offline, AirgapAI upholds stringent data protection standards; no external connection is required, minimizing vulnerabilities and ensuring that mission-critical medical information remains confidential.

One of the primary issues with legacy RAG is the semantic gap in how unique user questions are represented in vector space, plus the dilution of vector accuracy by incorporating extraneous text within large chunks. Blockify eliminates these issues by providing a 51% improvement in vector accuracy and a dedicated query element to aid in retrieving the right medical information.

## **What We Did: Breaking Down the Framework**

For AI inference to perform at scale in a military medical context, robust infrastructure is essential. Intel Gaudi 2 was used to accelerate large language model (LLM) inference. Gaudi 2 is designed for deep learning workloads, with an architecture that delivers high throughput; this is vital for tasks requiring parallel processing of complex data, such as thousands of medical documents and scientific articles.

To showcase the technology, a collection of field handbooks for medical treatment and triage were selected, such as the "Combat Casualty Care Handbook," the "Field Management of Chemical and Biological Casualties Handbook," and nearly a dozen other similar documents.

To support real-time retrieval and deliver trusted answers to medics, instructors, and trainees engaged in triage scenarios or course creation, the documentation was pre-processed and indexed using Iternal's Blockify technology to modularize content into manageable "IdeaBlocks." These IdeaBlocks are then deduplicated, distilled, indexed, tagged, and aggregated into a final output dataset.

Through testing across diverse medical documents and use cases, Iternal and Intel determined that optimal output quality and compute performance could be achieved by running 8,000-character segments, generating 1,000 tokens per query output, with 100 parallel jobs.

The Blockify workflow steps included:

* **Chunking the Text**: Source documents, including treatment manuals, triage guidelines, and research articles, were divided into smaller content chunks. These are passed into the specially configured LLM, which outputs modular blocks of content with a robust taxonomy for reusability.  
* **Embeddings**: The content blocks are converted into embeddings (vector representations) capturing their unique context, enabling intelligent retrieval within AirgapAI.  
* **Retrieval and Response Generation**: Based on user queries, from a medic in the field or a trainee in a simulation, the system retrieves relevant content for accurate, contextually relevant answers.

The result is real-time expertise and tailored outputs. Personalized triage training can occur within minutes, while integrating new treatment protocols that once took days or weeks is now possible at scale.

## **Business Use Cases: Real-Time AI Inference in Action**

The potential expansions of this technology to support the US military, especially for its medical training and education branch, are extensive. The following examples illustrate how the integrated Intel and Iternal solution delivers operational advantage:

* **Personalized Medical Triage Training Simulations**  
  Instructors can design AI-driven scenarios that mimic real combat injuries or mass casualty events. Trainees practice prioritizing care while AI provides adaptive feedback and references to best-practice protocols.  
* **In-field Data Collection and Post-scenario Debrief**  
  Medics record audio notes while treating casualties. AI transforms these voice memos into detailed briefings and after-action reports during transport. This drastically shortens the feedback loop and allows on-the-fly learning or reflection on what went right or wrong.  
* **Analysis and Summarization of Scientific Publications**  
  Medical training commands can upload fresh research and clinical trial data into Blockify. The solution rapidly ingests these sources, summarizes critical findings, and disseminates updated protocols to instructors and trainees.  
* **Reviewing and Updating Medical Treatment Documentation**  
  Policy, procedure, and treatment manuals can be quickly updated based on the latest insights. Curated materials push to in-field devices, ensuring that even offline forward bases have near-real-time access to the latest medical standards.  
* **Drafting and Developing New Treatment Protocols and Courses**  
  LLM-driven summarizations of new research help leadership craft emergent protocols, while instructors receive AI recommendations for new course materials and scenario designs that reflect the most current medical knowledge.

Beyond these medical-specific applications, the same system supports broader military needs:

* **Intelligence Reports**: Combine Intel Gaudi 2 acceleration with Iternal's Blockify to swiftly process operational data for actionable insights. AirgapAI ensures these analyses remain both secure and continuously accessible, even in disconnected environments.  
* **Strategy Documents**: With Blockify, large strategic briefs become modularized for quick updates and cross-referencing. Gaudi 2 acceleration delivers near-instant recall, while AirgapAI ensures mission-critical planning remains available in an air-gapped environment.  
* **Policy and Procedure Documents**: Blockify ingests, distills, and tags policy materials, significantly reducing any risk of error. Paired with Gaudi 2 and AirgapAI, high-speed, secure retrieval of vital documents becomes the standard.  
* **Repair and Maintenance Manuals**: By converting lengthy manuals into concise, context-rich segments, field technicians, similar to field medics, can instantly access relevant procedures, even in remote or bandwidth-limited scenarios.

For medical operations, the ability to retrieve accurate, contextually rich healthcare information rapidly is more than an operational advantage; it can be lifesaving. By reducing the operational burden of managing complex AI datasets, medical teams can focus on the mission: providing the best care possible in complex mission environments.

## **What This Means for You: Scalable AI Inference for Future Growth**

Building on the success of Intel Gaudi 2 and Iternal Technologies' Blockify combined with AirgapAI, defense and civilian agencies alike can now harness AI inference at scale. Teams can seamlessly deploy AI workloads in secure or fully air-gapped environments, turning unstructured medical data into real-time, actionable insights without sacrificing accuracy or speed.

Together, Intel and Iternal's integrated technologies enable you to:

* **Automate Data Ingestion and Curation**: Rapidly process and distill large medical datasets, from field manuals to cutting-edge research, ensuring accurate answers with virtually zero hallucinations, followed by human review and governance for accuracy.  
* **Drive Personalized Learning Experiences**: Create reliable, situation-aware triage training simulations and in-field support systems that adapt to each medic's level of expertise and situational complexity.  
* **Enable Faster, More Confident Decision-Making**: Retrieve and synthesize trusted information in seconds rather than hours; this is critical for triage, surgery, or large-scale casualty events.

With refined data pipelines and robust inference infrastructure, AI has moved from the conceptual to the operational across military sectors, including the critical role of medical training and care. Whether you're streamlining medical treatment documents, evaluating the latest research publications, or generating on-the-fly triage protocols, these tools are ready to meet evolving mission demands.
