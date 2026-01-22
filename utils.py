from pypdf import PdfReader
from typing import List, Dict, Any
import re

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts all text from a PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def parse_qa_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Parses Question and Answer pairs from text.
    Expected format:
    Q: Question text...
    A: Answer text...
    """
    qa_list = []
    
    # Normalize newlines
    text = text.replace('\r\n', '\n')
    
    # Simple state machine parsing
    lines = text.split('\n')
    current_q = None
    current_a = None
    current_mode = None # 'Q' or 'A'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # check for markers
        if line.upper().startswith("Q:") or line.upper().startswith("Q."):
            # If we were processing a previous QA pair, save it
            if current_q and current_a:
                qa_list.append({"question": current_q.strip(), "answer": current_a.strip()})
                current_q = None
                current_a = None
            elif current_q and current_mode == 'Q':
                pass # Continue appending to Q
            elif current_q and not current_a and current_mode == 'A':
                # Found new Q but haven't finished previous Q (no A found)? 
                # Or maybe previous Q had no A.
                # For now assumes strictly Q... A... Q... A...
                # If we encounter Q again while in A mode, we finish previous pair
                pass
            
            # Start new Question
            clean_line = re.sub(r'^[Qq][:.]\s*', '', line)
            current_q = clean_line
            current_mode = 'Q'
            
        elif line.upper().startswith("A:") or line.upper().startswith("A."):
            if current_mode == 'Q':
                # Switch to Answer mode
                clean_line = re.sub(r'^[Aa][:.]\s*', '', line)
                current_a = clean_line
                current_mode = 'A'
            elif current_mode == 'A':
                # Maybe a new Answer line? (Shouldn't happen if we just append)
                # If multiple A lines, just append
                pass
        else:
            # Continuation line
            if current_mode == 'Q':
                current_q += " " + line
            elif current_mode == 'A':
                if current_a is None: current_a = ""
                current_a += " " + line

    # Capture the last pair
    if current_q and current_a:
        qa_list.append({"question": current_q.strip(), "answer": current_a.strip()})
        
    return qa_list
