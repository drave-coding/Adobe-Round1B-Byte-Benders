# Approach for Persona-Driven Document Intelligence

This document outlines the methodology for a system that analyzes a collection of PDF documents and provides a ranked list of sections that are most relevant to a specific user persona and their stated goal. [cite_start]The solution is built as a self-contained Docker image that operates entirely offline on a CPU, adhering to all specified performance and size constraints [cite: 3357-3361].

### Overall Strategy

The system employs a two-stage, integrated pipeline. First, a robust **Outline Extraction Engine** analyzes each raw PDF to produce a clean, structured list of semantic headings. This module is designed to be highly accurate, learning the typographic hierarchy of each document. Second, a **Persona-Driven Ranking Engine** uses this structured outline to perform a sophisticated relevance analysis, ensuring the final output directly addresses the user's needs.

### Part 1: Data-Driven Outline Extraction

To overcome the challenge of varied PDF layouts, the extractor uses a data-driven, two-pass approach instead of relying on fragile heuristics.

1.  **Font Style Profiling**: The system first performs a full scan of the document to statistically identify the most common font size, which serves as a reliable baseline for the main body text.
2.  **Intelligent Heading Classification**: In the second pass, each line of text is evaluated as a potential heading. A line is only classified as a heading if its font style (size and boldness) is distinct from the body text and it passes a series of strict validation filters. These filters are designed to reject non-semantic text blocks such as figure captions, publication metadata, page headers, and footers. All extracted text is aggressively cleaned to remove PDF artifacts and normalize Unicode characters.

### Part 2: Persona-Driven Relevance Ranking

[cite_start]The core of the solution lies in its "Smart Scoring" system, designed to maximize relevance as per the scoring criteria[cite: 3369]. This system combines two powerful techniques:

1.  **Semantic Similarity**: Using a pre-trained sentence-transformer model (`all-MiniLM-L6-v2`), the system calculates the cosine similarity between the content of each section and the persona's query. To meet the strict performance requirements, only the first 1000 characters of each section are used for this calculation.
2.  **Keyword Heuristics**: This semantic score is then modified. The system applies a significant score **bonus** to sections whose titles contain positive keywords (e.g., "method," "dataset") derived from the `job_to_be_done`, and a score **penalty** for irrelevant sections (e.g., "references," "funding").

For the final `refined_text` output, the system performs a sub-section analysis by splitting the content of top-ranked sections into individual sentences and using the AI model to find the single most semantically relevant sentence, ensuring the output is concise and highly targeted.