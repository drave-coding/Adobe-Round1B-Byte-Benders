# Persona-Driven Document Intelligence (Round 1B)

This project is a solution for the Adobe India Hackathon "Connecting the Dots" Challenge, Round 1B. It's a self-contained Docker application that intelligently analyzes a collection of PDF documents to find and rank the sections most relevant to a specific user persona and their goals.

---
## ✨ Features

* **Intelligent Outline Extraction**: A robust, two-pass engine that learns the typographic hierarchy of each document to accurately identify semantic headings.
* **Smart Relevance Ranking**: A hybrid scoring model that combines deep semantic understanding with keyword-based bonuses and penalties to achieve highly accurate, persona-driven ranking.
* **Advanced Sub-Section Analysis**: For top-ranked sections, the system performs a sentence-level analysis to extract the single most relevant snippet, providing concise and targeted insights.
* **Robust & Performant**: The entire solution is containerized with Docker, runs completely offline on a CPU, and is optimized to meet the strict time and size constraints of the hackathon.

---
## ⚙️ How It Works

The solution operates as a two-stage pipeline within a single Docker container:

1.  **The Extractor**: For each PDF, a data-driven extractor first profiles the document's font styles to identify the main body text. It then re-scans the document to find text blocks with distinct font properties (larger size, bold), passing them through a series of strict filters to ensure only true headings are selected.
2.  **The Analyzer**: The main script takes this clean list of headings and extracts the text content for each section. It then uses a sentence-transformer model to score each section's relevance to the user's query. The final ranking is determined by a "Smart Score" that blends this semantic score with keyword-based adjustments. Finally, it generates the `refined_text` by finding the most relevant sentence within each top-ranked section.

---
## 🛠️ Technology Stack

* **Language**: Python 3.9
* **Containerization**: Docker
* **PDF Processing**: PyMuPDF (fitz)
* **NLP / AI Model**: Sentence-Transformers (`all-MiniLM-L6-v2`)
* **Core Libraries**: NumPy, SciKit-Learn

---
## 🚀 Getting Started

### Prerequisites
* Docker Desktop must be installed and running.

### Directory Structure
Before running, ensure your project contains separate input folders for each test case (e.g., `test_case_1/input`, `test_case_2/input`, etc.). Each input folder must contain:
* All the PDF documents you want to analyze for that case.
* A single `persona.json` file describing the user and their goal.

### Build the Docker Image
Navigate to the project's root directory in your terminal and run the build command.

```bash
docker build --platform linux/amd64 -t adobe-solution-1b .
```

### Run the Docker Container
Use the following commands to run the container for each specific test case. The output will be generated in the corresponding `/output` folder for that test case.

#### **For Test Case 1 (Academic Research):**
```powershell
# For PowerShell
docker run --rm `
  -v "$(pwd)/test_case_1/input:/app/input" `
  -v "$(pwd)/test_case_1/output:/app/output" `
  --network none `
  adobe-solution-1b
```

#### **For Test Case 2 (Business Analysis):**
```powershell
# For PowerShell
docker run --rm `
  -v "$(pwd)/test_case_2/input:/app/input" `
  -v "$(pwd)/test_case_2/output:/app/output" `
  --network none `
  adobe-solution-1b
```

#### **For Test Case 3 (Policy and Data Analysis):**
```powershell
# For PowerShell
docker run --rm `
  -v "$(pwd)/test_case_3/input:/app/input" `
  -v "$(pwd)/test_case_3/output:/app/output" `
  --network none `
  adobe-solution-1b
```

---
## 🧪 Test Cases

The solution has been optimized and tested for three distinct types of professional documents:

1.  **Academic Research**: A PhD Researcher reviewing scientific papers for methodologies and datasets.
2.  **Business Analysis**: An Investment Analyst examining annual reports for financial trends and strategy.
3.  **Policy and Data Analysis**: A Policy Advisor for a government committee synthesizing reports on climate change to identify key data and recommendations.