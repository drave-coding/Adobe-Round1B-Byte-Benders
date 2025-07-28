# part-1b/src/main.py
import os
import json
import fitz
import numpy as np
from sentence_transformers import SentenceTransformer, util
import datetime
import time
import glob
import sys
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extractor.handler import generate_outline
# --- THIS IS THE FIX: Import the cleaning function ---
from extractor.handler import clean_text as advanced_cleaner

# --- Constants ---
INPUT_DIR = os.getenv('INPUT_DIR', 'test_data/input')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'test_data/output')
MODEL_PATH = 'src/models/all-MiniLM-L6-v2'

def load_model():
    print("Loading sentence transformer model...")
    return SentenceTransformer(MODEL_PATH)

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_relevance_score(section_title, section_embedding, query_embedding) -> float:
    """Calculates a smart relevance score."""
    positive_keywords = ['method', 'dataset', 'benchmark', 'result', 'evaluation', 'experiment', 'model', 'algorithm', 'analysis', 'kinetic', 'mechanism', 'concept', 'rate law', 'reaction']
    negative_keywords = ['reference', 'declaration', 'funding', 'appendix', 'acknowledgment', 'competing interest', 'further reading', 'conclusion']
    score = util.cos_sim(query_embedding, section_embedding)[0][0].item()
    title_lower = section_title.lower()
    for keyword in positive_keywords:
        if keyword in title_lower: score *= 1.5
    for keyword in negative_keywords:
        if keyword in title_lower: score *= 0.2
    return float(score)

def find_most_relevant_snippet(section_content, model, query_embedding):
    """Finds the most relevant sentence from a block of text."""
    sentences = re.split(r'(?<=[.!?])\s+', section_content)
    sentences = [s.strip() for s in sentences if len(s.split()) > 7]
    if not sentences: return section_content[:500]
    
    sentence_embeddings = model.encode(sentences)
    similarities = util.cos_sim(query_embedding, sentence_embeddings)
    best_sentence_index = np.argmax(similarities)
    return sentences[best_sentence_index]

def extract_text_from_sections(pdf_path, outline):
    """Extracts text for each section."""
    if not outline: return []
    doc = fitz.open(pdf_path)
    sections = []
    
    for i, current_heading in enumerate(outline):
        start_page = current_heading['page']
        end_page = outline[i + 1]['page'] if i + 1 < len(outline) else doc.page_count + 1
        content = ""
        for page_num in range(start_page - 1, end_page - 1):
            if page_num < doc.page_count:
                content += doc[page_num].get_text()
        
        if content.strip():
            sections.append({'title': current_heading['text'], 'page': start_page, 'content': content.strip()})
            
    doc.close()
    return sections

def process_all_documents(model):
    """Main function."""
    persona_data = load_json(os.path.join(INPUT_DIR, 'persona.json'))
    persona_query = f"Role: {persona_data['persona']['role']}. Task: {persona_data['job_to_be_done']}"
    query_embedding = model.encode([persona_query])

    all_sections = []
    pdf_files = glob.glob(os.path.join(INPUT_DIR, '*.pdf'))
    for pdf_path in pdf_files:
        pdf_filename = os.path.basename(pdf_path)
        outline_data = generate_outline(pdf_path)
        print(f"Extractor found {len(outline_data.get('outline', []))} headings in {pdf_filename}.")
        
        sections = extract_text_from_sections(pdf_path, outline_data.get("outline", []))
        if not sections:
            print(f"Warning: No sections were extracted from {pdf_filename}.")
            continue

        section_contents = [s['content'] for s in sections]
        section_embeddings = model.encode(section_contents)

        for i, section in enumerate(sections):
            score = get_relevance_score(section['title'], section_embeddings[i], query_embedding)
            section['relevance_score'] = score
            section['document'] = pdf_filename
            all_sections.append(section)

    ranked_sections = sorted(all_sections, key=lambda x: x['relevance_score'], reverse=True)

    output_data = {
        "metadata": {"input_documents": [os.path.basename(p) for p in pdf_files], "persona": persona_data['persona'], "job_to_be_done": persona_data['job_to_be_done'], "processing_timestamp": datetime.datetime.utcnow().isoformat() + "Z"},
        "extracted_section": [{"document": s['document'], "page_number": s['page'], "section_title": s['title'], "importance_rank": i + 1} for i, s in enumerate(ranked_sections)],
        "sub-section_analysis": [{"document": s['document'], "page_number": s['page'], "refined_text": advanced_cleaner(find_most_relevant_snippet(s['content'], model, query_embedding))} for s in ranked_sections[:10]]
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_filepath = os.path.join(OUTPUT_DIR, 'challenge1b_output.json')
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
    print(f"✅ Success! High-quality output generated at {output_filepath}")

if __name__ == "__main__":
    start_time = time.time()
    model = load_model()
    process_all_documents(model)
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")