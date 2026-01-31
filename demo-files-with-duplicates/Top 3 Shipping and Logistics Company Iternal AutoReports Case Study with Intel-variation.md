# **Transforming a Top-Three Global Shipping Company's Security Questionnaire Processing with AutoReports: Achieving 10X Cost Reduction and 97,250 Hour Annual Savings**

Security questionnaires stand between opportunity and revenue. AI is rapidly becoming a strategic asset for major global logistics and shipping organizations, and for the Top-Three Global Shipping Company, the world's third-largest container shipping company with operations in 160 countries, manually answering security questionnaires by searching through extensive documentation is slow, costly, and leads to inconsistent responses.

Between complex security requirements, strict compliance regulations, and the financial implications of potential security breaches, the Top-Three Global Shipping Company's need for fast, accurate, and secure insights has never been greater. The volume of questionnaires is immense; the complexity is formidable; the cost of delayed responses is measured in lost deals.

Together, Intel and Iternal Technologies have partnered to deliver a unique solution that supports the Top-Three Global Shipping Company via the Turnkey AI platform and its no-code Generative AI document analysis solution, AutoReports, to transform security questionnaire analysis.

The Top-Three Global Shipping Company can now confidently extract key actionable insights: security requirement answers, policy compliance details, and more, significantly accelerating their security review processes.

## **Benchmark Results**

Running LLAMA 3.1 70B, an Intel Gaudi Server can process a security document of approximately 161 questions (49,377 words) in approximately 336 seconds generating approximately 6,850 tokens. The ability to process approximately 2 million pages of text per month on a single Gaudi 2 core demonstrates the scalability and efficiency of this approach.

Assuming 3,890 minutes for a security professional to complete the same 161-question document, including all policy review and response mapping (1,610 minutes) and new policy drafting (2,280 minutes), the AI can save approximately 64.83 hours per questionnaire, or 97,250 hours per year at a rate of 1,500 questionnaires per year.

* **Average Response Length in Tokens**: 452 tokens  
* **Response Time per Token**: 22.36 - 22.89 tokens per second  
* **Security Questions per Minute**: Approximately 100  
* **Number of Security Questions per Month**: 20,125  
* **Security Policies Updates Made per Month**: Approximately 9,500

### Cost-Benefit Analysis

| Category | Manual Method (Baseline) | Spreadsheet Processing LLM Framework | Benefit/Impact |
| :---- | :---- | :---- | :---- |
| Processing Time | 1 requirement every 10 minutes; 30 minutes for each drafted policy | 30 seconds per requirement (one at a time; can scale to run 10+ simultaneously) | Substantial reduction |
| Cost per Requirement | Approximately $15 per requirement response plus approximately $45 per policy (assumes $180k/yr salary) | Approximately $2.1 per requirement response including policy draft | Significant cost savings |
| Accuracy | Variable, human-dependent | 95%+ | Improved consistency and accuracy |
| Scalability | Limited by headcount | Unlimited | Enterprise-ready |

At this capacity and scale, a single Gaudi 8X Server can provide enough capacity to support the entire security department of the Top-Three Global Shipping Company, saving the company thousands of hours of expensive security review.

## **Why GenAI for Security Questionnaire Analysis Matters**

Deploying AI to evaluate thousands of pages of security questionnaires, policies, standards, and compliance documents goes far beyond simple data lookups. It requires extracting quality, accurate, and contextually relevant insights at scale.

The Top-Three Global Shipping Company's security analysts have traditionally faced a time-consuming process for data preparation and security document information gathering. In the past, analysts would have to sift through millions of security documents manually each year, a feat near impossible because of the cost, to identify opportunities for quickly mapping existing policies with customer questions, as well as other security actions such as updating policy language for compliance upon renewal.

The highly complex and mentally taxing process of manually reviewing documents makes it hard to quickly identify and categorize security terms, policy thresholds, or expiration timelines. Additionally, if a security questionnaire fails to be provided in time, the deal may be lost; this introduces revenue risk and loss to the business.

With thousands of security questionnaires under management, the risk exposure can add up to hundreds of millions of dollars.

Leveraging the Turnkey AI platform and AutoReports, the Top-Three Global Shipping Company can seamlessly ingest massive volumes of security text from internal repositories, security management systems, and even external websites. By using trusted information and a patented indexing approach, AutoReports helps analyze the long and complex security documents through no-code workflows at millions scale, extract key insights, and makes it easy for security teams to determine which security questionnaires should be the highest priority to work on based on business value.

![A screenshot of a computer - Description automatically generated][image1]

## **AutoReports In Action: A Summary of the Document Analysis Solution**

At its core, AutoReports streamlines unstructured text analysis by enabling users to quickly assemble no-code fully automated LLM workflows. The solution can ingest multiple data sources such as word documents, PDFs, TXT files, emails, and other media formats and then process those documents through a specific user-specified workflow, empowering The Logistics Company to extract and highlight critical security details in minutes rather than hours or days.

### Ingestion and Optimization with Blockify

AutoReports uses Iternal's patented Blockify technology to break documents down into "IdeaBlocks" of verified content. These IdeaBlocks are rich with a robust metadata taxonomy containing information specific to the questions and information needed by the security team. This approach improves retrieval speed, practically eliminates AI hallucinations, and boosts LLM accuracy by as much as 78x compared to traditional generative AI pipelines.

### AI-Driven Insights with AutoReports

Once documents have been "Blockified," AutoReports employs large language models to extract and identify key information such as policy mappings, compliance obligations, or approaching certification expiration dates.

Queries using AutoReports are fully configurable and can be deployed as LLM prompts via the Critical Question prompt field contained within each IdeaBlock.

![][image2]

AutoReports makes it easy for users to quickly respond to security questionnaires and provide tailored hybrid-responses to questions that would require answering from multiple policy documents:

* How do you process and store customer data in transit and at rest?
* Are all privileged actions captured with sufficient detail and forwarded in near-real time to a central monitoring platform that is protected against tampering?
* Has every asset inside the secure environment been reviewed to confirm it directly supports a defined business or SWIFT-related function, with written justification for any out-of-scope components that remain?
* Throughout their entire lifecycle, from creation, storage, rotation, to archival, are cryptographic keys safeguarded by approved technical controls and documented operational procedures, with clear assignment of ownership?
* Is each hardware and software component covered by an active vendor or third-party support agreement, and are contract expirations proactively tracked to prevent lapses?

Each query can be run in just a few seconds. Because the Turnkey AI platform running on Intel Gaudi supports "Bring Your Own Model," the AutoReports solution can plug and play the latest GenAI LLMs to process information with the highest degree of performance.

Additionally, because of how AutoReports processes insights at the IdeaBlock level, different parts of the AutoReport can tap into different LLMs; this means a document could be processed using one, two, three, or more unique LLMs, whether standard or fine-tuned, for even more specialized processing.

### Flexible Deployment of Iternal Turnkey AI with Intel Gaudi

Through the global partnership with Intel, the Turnkey AI platform scales to meet enterprise demands by leveraging the Gaudi platform for inference at scale.

Turnkey AI features a robust API for bulk jobs, paired with Zero Trust security, version control, real-time updates, and compliance. The API makes it easy for customers to quickly integrate AutoReports seamlessly, in just hours, into existing contract management, customer relationship management (CRM), document management, or enterprise resource planning (ERP) systems, ensuring faster lifecycles and better collaboration across teams.

## **Use Cases for Security and Compliance Teams**

The following solutions can be deployed at scale to accelerate questionnaire turnaround time and secure revenue:

* **Security Requirement Mapping and Draft Response Generation:** Automatically align each customer question with the most relevant policy excerpt. AutoReports surfaces the precise paragraph or control, then produces a draft answer that can be dropped directly into the spreadsheet. The Top-Three Global Shipping Company's pilot showed sub-second processing for batches of questions, eliminating days of manual search.  
* **High-Quality Draft Policy Generation:** Create new draft policies in seconds, designed to fill identified security gaps and ensure comprehensive coverage.  
* **Meta-analysis of Questionnaires for Aggregate Insights:** Combine data from hundreds of completed questionnaires to reveal recurring customer concerns, common control gaps, and trending regulatory demands. These insights guide proactive policy updates and streamline future responses.  
* **Policy Revision and Renewal Tracking:** Flag internal security documents that are approaching review dates or have conflicting language with current customer requirements. Automated alerts help teams stay ahead of audits and avoid deal-blocking discrepancies.  
* **Gap Analysis and Redlining Between Requirements and Policies:** Instantly highlight areas where existing controls do not satisfy a customer's requested standard (e.g., ISO 27001 vs. NIST). AutoReports produces a side-by-side "redline" view so remediation steps can be prioritized before the questionnaire deadline.  
* **Vendor Assessment and Eligibility Scoring:** Evaluate third-party vendor questionnaires against the Top-Three Global Shipping Company's own security baseline. The system scores each vendor's controls, spotlighting high-risk suppliers and accelerating onboarding decisions.  
* **Risk Exposure Identification Across Documentation:** Extract potential vulnerabilities or non-compliance indicators from SOC 2 reports, penetration-test summaries, and security policies. Consolidating these findings into a single dashboard gives leadership an enterprise-wide view of exposure in near real time.

## **Business Use Cases: Real-Time AI Analysis in Action**

AutoReports' adaptability delivers immediate value across the Top-Three Global Shipping Company's global shipping and logistics operations:

* **Customer Onboarding Security Assurance:** Major shippers often require completed security questionnaires before booking high-value cargo. The pilot's LLM workflow now lets account teams answer 160-question spreadsheets in minutes, safeguarding multimillion-dollar deals that would otherwise stall.  
* **Service-Level Agreement (SLA) Renewal Acceleration:** As contracts for port services and warehousing come up for renewal, AutoReports cross-references customer security clauses with the Top-Three Global Shipping Company's latest controls, recommending wording changes and ensuring compliance before signatures are due.  
* **Mergers and Acquisitions Due-Diligence Harmonization:** When acquiring a logistics provider or terminal operator, the Top-Three Global Shipping Company inherits a patchwork of security policies. AutoReports consolidates and categorizes these documents, flagging conflicting controls and surfacing integration priorities days, rather than months, before closing.  
* **Regulatory Reporting and Audit Readiness:** Generate export-ready spreadsheets that map policy controls to maritime cybersecurity mandates (e.g., IMO 2021 guidelines). By distilling thousands of pages into concise compliance statements, the Top-Three Global Shipping Company slashes audit preparation time and reduces the risk of fines.

By automating what was once a heavily manual, error-prone workflow, the Top-Three Global Shipping Company meets tight customer deadlines, preserves revenue, and maintains a consistently high security posture; at a validated 95% cost reduction versus manual methods.

## **Conclusion**

For a Top-Three Global Shipping Company processing thousands of security questionnaires each year, harnessing AI-driven policy mapping is transformative. Powered by Iternal's AutoReports and Intel Gaudi, key controls like data-encryption standards, incident-response timelines, or access-management procedures are no longer buried in dense PDFs. Critical answers are generated in seconds, with 95%+ accuracy and sub-second latency, protecting revenue and freeing security personnel to focus on strategic improvements.

With proven results showing drastic cost and time savings, the Top-Three Global Shipping Company can now:

* Scale the workflow to every incoming security questionnaire  
* Expand its curated knowledge base of security documents  
* Launch full production deployment to unlock ongoing operational gains  
* Transform questionnaire bottlenecks into a competitive advantage, ensuring the Top-Three Global Shipping Company never loses a deal because a security deadline was missed, using AutoReports
