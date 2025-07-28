# part-1b/extractor/handler.py
import fitz
import statistics
import re
import unicodedata
from collections import Counter
import os

# In part-1b/extractor/handler.py

def clean_text(text: str) -> str:
    """A definitive text cleaner."""
    # Step 1: Replace newlines and other problematic whitespace with a single space
    text = re.sub(r'[\n\r\t]+', ' ', text)
    
    # Step 2: Normalize to decompose combined characters (like ligatures)
    text = unicodedata.normalize('NFKD', text)
    ligatures = {'\ufb00': 'ff', '\ufb01': 'fi', '\ufb02': 'fl', '\ufb03': 'ffi', '\ufb04': 'ffl'}
    for search, replace in ligatures.items():
        text = text.replace(search, replace)
    
    # Step 3: Encode to ASCII, ignoring any characters that can't be converted.
    text = text.encode('ascii', 'ignore').decode('utf-8')

    # Step 4: Final cleanup of extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ... (the rest of your handler.py file remains unchanged) ...

def is_valid_heading(text: str) -> bool:
    """A final, very strict filter for what constitutes a real heading."""
    if not text or len(text) < 4 or len(text) > 150: return False
    if text.endswith('.') or text.endswith(':') or text.endswith(','): return False
    if not (text[0].isupper() or text[0].isdigit()): return False
    if re.search(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', text, re.IGNORECASE) and re.search(r'\b\d{1,4}\b', text): return False
    if not re.search(r'\b[a-zA-Z]{4,}\b', text): return False
    if any(keyword in text.lower() for keyword in ['et al', 'copyright', 'journal of', 'figure', 'table', 'supplementary', 'author', 'university', 'abstract', 'keywords', 'references', 'acknowledgements', 'appendix', 'open access']): return False
    return True

def classify_heading(size: float, font: str, body_size: float) -> str or None:
    """Classifies a heading level."""
    is_bold = any(s in font.lower() for s in ['bold', 'black', 'heavy', 'oblique'])
    if size > body_size * 1.3 or (size > body_size * 1.2 and is_bold): return "H1"
    if size > body_size * 1.15 or (size > body_size * 1.05 and is_bold): return "H2"
    if size > body_size and is_bold: return "H3"
    return None

def generate_outline(pdf_path: str) -> dict:
    """A definitive, robust function to extract a clean outline from a PDF."""
    print(f"Extractor: Analyzing '{os.path.basename(pdf_path)}'...")
    doc = fitz.open(pdf_path)
    title = clean_text(doc.metadata.get('title', ''))
    outline = []
    
    styles = Counter()
    for page in doc:
        blocks = page.get_text("dict").get("blocks", [])
        for block in blocks:
            if block.get('type') == 0:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        styles[(round(span['size']), span['font'])] += len(span['text'])

    if not styles: return {"title": title or "Untitled", "outline": []}
    body_size = styles.most_common(1)[0][0][0]

    unique_headings = set()
    for page_num, page in enumerate(doc, 1):
        blocks = sorted(page.get_text("dict").get("blocks", []), key=lambda b: b.get('bbox', [0,0,0,0])[1])
        for block in blocks:
            if block.get('type') == 0:
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans: continue
                    
                    # Heuristic: A heading often has a consistent style throughout the line.
                    if len(set(s['font'] for s in spans)) == 1 and len(set(round(s['size']) for s in spans)) == 1:
                        span = spans[0]
                        text = clean_text(" ".join(s['text'] for s in spans))
                        
                        if is_valid_heading(text) and text.lower() not in unique_headings:
                            level = classify_heading(round(span['size']), span['font'], body_size)
                            if level:
                                outline.append({"level": level, "text": text, "page": page_num})
                                unique_headings.add(text.lower())

    if not title and outline: title = outline[0]['text']
    doc.close()
    return {"title": title or "Untitled", "outline": outline}