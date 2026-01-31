# **Enabling Real-Time Language Translation for a Major US Security Agency with AirgapAI Translator Powered by Intel NPU**

## Executive Summary

Language barriers should never compromise security operations. This case study details the strategic partnership between Intel and Iternal Technologies to provide a Major US Security Agency with AirgapAI Translator. This solution leverages AI inference for real-time, secure, and accurate language translation in remote and disconnected environments, significantly enhancing The Agency's operational effectiveness.

### Key Challenges and Solutions

| Challenge | AirgapAI Translator Solution |
| ----- | ----- |
| Scarcity of Human Translators | Provides real-time translation for over 25 common and 200+ total languages |
| Data Curation and Governance | Operates completely offline, upholding stringent data protection standards |
| Operational Delays and Inaccuracies | Processes audio 5.5x faster than real-time with high accuracy (reduced hallucinations) |
| Disconnected Environments | Edge-based solution running on Intel NPU chips, requiring no internet connection |

### Impact for The Agency

AirgapAI Translator delivers substantial mission advantage across various Agency operations:

* **Real-Time Voice Translation:** Ensures secure and accurate communication with non-English speakers during border encounters
* **Expedited Processing:** Significantly speeds up traveler processing at ports of entry
* **Improved Compliance and Safety:** Reduces errors and misinterpretations, enhancing regulatory compliance and safety
* **Enhanced Interrogation:** Converts lengthy interviews into concise, context-rich segments for rapid information retrieval

This partnership demonstrates the potential for scalable AI inference in critical environments, improving communication, reducing operational burdens, and enhancing security and efficiency across border management.

![][image1]

## Introduction

The mission is clear: communicate effectively with any individual, in any language, at any location, at any time. AI is rapidly becoming a strategic asset for The Agency, and for agents responsible for border security and facilitating lawful trade and travel, the ability to access the right information, at the right time, in a safe, secure, and trusted manner is paramount; all while being confident in the veracity of the information being provided, especially in real-time communication.

Together, Intel and Iternal Technologies have partnered to deliver a unique solution to support The Agency, addressing many of the common challenges associated with the adoption of AI technologies for real-time translation: the scarcity of human translators, data curation for diverse languages, governance, and access control provisioning of critical communication data in highly remote and disconnected environments.

Given the requirement to harness massive amounts of data for effective communication and to stay competitive in a global environment, AI inference, the ability to generate real-time insights and translations from large datasets, is becoming essential. There is simply a lack of available translation personnel to support the demanding use case of communicating with individuals in any foreign language in highly remote and disconnected environments.

Pairing highly performant Intel and Iternal solutions like AirgapAI Translator with the edge-based Intel NPU chips software for local, real-time language translation and data summarization, an end-to-end solution can deliver substantial mission advantage. AirgapAI Translator enables Border Agents to conduct critical work engaging with people who speak a variety of languages, such as Chinese, Arabic, Russian, German, Spanish, and Hindi, even if the agent only speaks English, bridging communication gaps and enhancing operational effectiveness in the field.

## Benchmark Results

Supporting more than 24 of the most common languages, AirgapAI Translator can process input audio at 5.5 times real-time, which means that 5.5 seconds of real-world audio can be transcribed and translated in just 1 second; eliminating time delays and delivering a near real-time experience.

* **Input Time**: 5.5 seconds of Chinese, Arabic, Russian, German, Spanish, Hindi, etc.
* **Processing Time**: 1 second to output into English

Speed alone is insufficient. AirgapAI Translator running on the Intel NPU increased the quality of language translation because the NPU is able to run larger speech-to-text AI models faster, which means that higher precision transcription and translation can occur.

![][image2]

## Why AI Inference Matters

AI inference extends beyond running a trained model; it goes beyond simple data queries. This capability enables the extraction of real-time, accurate, and contextually relevant insights from unstructured data at scale.

In the context of Agency operations, real-time language translation in remote and disconnected environments is a complex and time-consuming process. Without an effective and real-time approach to communication, Agency operations risk misinterpreting crucial information. Garbage in, garbage out; if you cannot trust your AI to always be correct, then you cannot ever trust it to be correct because the mistakes are unpredictable. The lack of available human translators to support the vast linguistic needs across the border is a critical challenge.

Intel and Iternal used AI to bring translations to the field even when limited access to essential translation resources is not possible. AirgapAI Translator enables Border Agents to communicate effectively in any foreign language, even if they only speak English, by providing real-time language translation services in highly remote and disconnected environments.

The result is a highly accurate and optimized screening process for people who do not speak English, ensuring reliable and accurate communication for Agency agents and effective processing and security.

For example, individuals crossing the southern border may be injured, seeking asylum, or have malicious intent. Before, a painful and lengthy process to screen individuals who do not speak English required a translator to speak with the individual. This creates screening and processing delays, which can be dangerous for a person in need. Now with real-time performance, Agents are no longer dependent on a translation resource to screen individuals and route them through the necessary process.

This success underpins the AirgapAI Translator's ability to operate efficiently in low-bandwidth or no-bandwidth environments, providing essential real-time translation capabilities where human translators are scarce.

## AirgapAI: Inferencing at the Edge with Intel NPU

Optimizing a dataset is only as useful as the "in-field" applicability. AirgapAI is a powerful, network-independent AI solution designed to run locally on an AI PC.

AirgapAI can be used to support military operations by running large language models locally on Intel NPU chips. AirgapAI enables mission-critical tasks in environments requiring the highest levels of security.

* **Processing Time**: Using OpenAI Whisper Medium, inference is approximately 5.5x faster than real-time using Intel NPU
* **Accuracy**: Whisper delivers support for more than 25 of the most common languages with over 90% average accuracy
* **Translation Speed**: 5.5 seconds of audio transcribed into English text in approximately 1 second

AirgapAI, powered by open-source large language models like Meta's NLLB (No Language Left Behind) and custom fine-tunes, enables agencies to leverage specialized, role-based guardrails and curated datasets tailored to their operational needs. This approach ensures a secure and highly relevant AI experience, particularly for tasks involving analysis of interviews, screening, and questioning for real-time decision-making, with the added benefit of high-quality translation across 200 languages.

Upon transcribing the information from Whisper running on the Intel NPU via AirgapAI Translator, the relevant information for a user query, an inference leveraging NLLB's multilingual capabilities, translates the key information into a new language (i.e., English), breaking down language barriers and promoting inclusion.

By operating completely offline, AirgapAI upholds stringent data protection standards; no external connection is required, minimizing potential vulnerabilities and ensuring mission-critical information remains strictly confidential. Personnel can rely on AirgapAI to quickly respond to mission requirements and translate content across languages.

With AirgapAI, US government teams can securely harness the power of AI models to support rapid decision-making and communicate more effectively, all within a fully controlled, air-gapped environment.

## What We Did: Breaking Down the Framework

For AI inference to perform at scale, robust infrastructure is essential. The Intel NPU was used to accelerate AI inference for both Whisper's Speech-to-Text model and Facebook Meta's NLLB Text-to-Text language translation capability. The NPU is designed for efficient AI workloads, and its performance in both transcription and translation made it the ideal choice for this project. Its architecture allows for high throughput, enabling the achievement of 5.5x real-time translation speeds. This makes it ideal for tasks that require rapid, parallel processing of complex audio and linguistic data.

To enable real-time translation and facilitate communication across multiple languages, the audio data was processed and the NLLB model leveraged to provide text-to-text translation. This technology significantly benefits people by breaking down language barriers and allowing for seamless communication in diverse linguistic environments.

The Whisper Speech-to-Text model and the NLLB Text-to-Text model were prepared and optimized to run on the Intel NPU. Through extensive optimization testing, Iternal and Intel determined the optimal quality of output and compute performance could be achieved by leveraging the NPU's capabilities for both speech recognition and language translation, enabling rapid and accurate cross-lingual communication.

The result is real-time language translation across more than 25 of the most common languages, all on a local device and able to support fully remote settings that would otherwise be unattainable.

## Business Use Cases: Real-Time AI Inference in Action

The implications for broader expansion of this technology in support of The Agency are extensive, particularly in overcoming language barriers.

* **Real-Time Voice Translation for Border Encounters:** When Agency agents encounter individuals who do not speak English, crucial information can be lost or misinterpreted. The combination of Intel NPU acceleration with Iternal's AirgapAI Translator technology can provide real-time, voice-based AI translation. This ensures secure and accurate communication even in remote or disconnected environments, eliminating the inaccuracies and delays of traditional interpretation methods.  
* **Expedited Processing of Travelers:** Language barriers often lead to prolonged questioning and delays in processing at ports of entry. By leveraging AirgapAI Translator's ability to process and distill conversations in real-time, Agency agents can achieve near-instant understanding with non-English speakers. Intel NPU acceleration ensures rapid translation, while AirgapAI guarantees that mission-critical communications remain available and secure in an air-gapped environment, significantly speeding up traveler processing.  
* **Improved Compliance and Safety:** Misunderstandings due to language differences can lead to non-compliance with regulations or even dangerous situations. AirgapAI Translator can ingest and translate spoken interactions into easily digestible insights, significantly reducing the risk of error or misinterpretation. Paired with NPU and AirgapAI, The Agency achieves high-speed, secure retrieval of vital information for immediate and compliant decision-making, ensuring both traveler safety and operational efficiency.  
* **Enhanced Interrogation and Interview Processes:** Converting lengthy, often complex, interviews into concise, context-rich segments through voice translation allows agents to instantly access the most relevant information. NPU's processing power and AirgapAI's local inference enable secure, offline retrieval that keeps operations running smoothly, even in remote or bandwidth-limited scenarios. This is crucial for obtaining accurate information quickly and efficiently.

For Agency operations, the ability to retrieve accurate, contextually rich voice data in real time is more than an operational advantage; it is a strategic one. By eliminating the operational burden of managing complex language interpretation, teams can focus on their mission, improving communication and reducing the strain on limited resources.

## What This Means for You: Scalable AI Inference for Future Growth

Building on the proven success of Intel NPU and Iternal Technologies' AirgapAI Translator, enterprises and government agencies alike can now harness AI inference at scale with minimal infrastructure overhead. Teams can seamlessly deploy massive AI workloads in secure or fully air-gapped environments, decentralized; turning unstructured voice data into real-time, actionable insights without sacrificing accuracy or speed.

Together, Intel and Iternal's integrated technologies enable you to:

* **Automate Voice Data Ingestion and Curation:** Rapidly process and distill large voice datasets, ensuring accurate answers without hallucinations, overcoming the challenges of interpreting spoken language.  
* **Drive Personalized Experiences:** Tailor information in a reliable way based on the operational requirements of each interaction, providing immediate and understandable communication to individuals regardless of their native language.  
* **Enable Faster Decision-Making:** Confidently retrieve and synthesize trusted voice information to make critical choices in seconds rather than hours, eliminating the delays and inaccuracies associated with traditional language barriers.

With refined data pipelines and robust inference infrastructure available, AI has moved from conceptual to operational across industries. Whether you're streamlining traveler processing, conducting interviews, or ensuring compliance, the tools and frameworks are in place to meet your needs, specifically addressing the critical need for seamless voice-based language translation in a resource-constrained environment.
