from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import fitz  # PyMuPDF
import io
import re

app = FastAPI()

# Add this after app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- For now, allow all origins (you can restrict later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/flag-terms/")
async def flag_terms(
    excel_file: UploadFile | None = None,
    pdf_file: UploadFile = File(...),
):
    if excel_file:
        excel_contents = await excel_file.read()
        words_to_check = read_excel_words(io.BytesIO(excel_contents))
    else:
        words_to_check = DEFAULT_LIST

    pdf_contents = await pdf_file.read()
    analysis_result = find_words_in_text(words_to_check, io.BytesIO(pdf_contents))

    return JSONResponse(content=analysis_result)

@app.post("/highlight-terms/")
async def highlight_terms(excel_file: UploadFile | None = None, pdf_file: UploadFile = File(...)):
    # Read uploaded files into memory
    if excel_file:
        excel_contents = await excel_file.read()
        words_to_check = read_excel_words(io.BytesIO(excel_contents))
    else:
        words_to_check = DEFAULT_LIST
    
    pdf_contents = await pdf_file.read()

    # Process PDF file in memory and get output bytes
    output_pdf_stream = highlight_words_in_text(words_to_check, io.BytesIO(pdf_contents))

    # Return the modified PDF to user
    return StreamingResponse(output_pdf_stream, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=highlighted_output.pdf"})



def read_excel_words(excel_stream):
    """Read Excel file from BytesIO stream."""
    df = pd.read_excel(excel_stream)
    words = df.iloc[:, 0].dropna().tolist()
    return words


def normalize_text(text):
    # Fix hyphenated line breaks like "multicul-\ntural" → "multicultural"
    text = re.sub(r'-\s*\n\s*', '', text)
    # Replace remaining newlines with spaces to preserve sentence flow
    text = re.sub(r'\n+', ' ', text)
    return text

def find_words_in_text(words, pdf_stream, case_sensitive=False):
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    results = {}

    flags = 0 if case_sensitive else re.IGNORECASE

    for page_num, page in enumerate(doc, start=1):
        raw_text = page.get_text()
        text = normalize_text(raw_text)
        for word in words:
            # Use regex to find word occurrences
            matches = re.findall(re.escape(word), text, flags=flags)
            count = len(matches)
            if count > 0:
                if word not in results:
                    results[word] = {"count": 0, "pages": []}
                results[word]["pages"].append(page_num)
                results[word]["count"] += count

    return results

def highlight_words_in_text(words, pdf_stream):
    """Highlight words in a PDF loaded from BytesIO, and return a new BytesIO with modified PDF."""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")

    found_words = {}

    for page in doc:
        for word in words:
            word_instances = page.search_for(word)
            for inst in word_instances:
                if word in found_words:
                    found_words[word] += 1
                else:
                    found_words[word] = 1
                highlight = page.add_highlight_annot(inst)
                highlight.update()

    # Save to a new BytesIO object
    output_stream = io.BytesIO()
    doc.save(output_stream, garbage=4, deflate=True, clean=True)
    output_stream.seek(0)  # Rewind to the beginning for StreamingResponse

    return output_stream

DEFAULT_LIST = [
    'activism',
    'activists',
    'advocacy',
    'advocate',
    'advocates',
    'barrier', 
    'barriers',
    'biased',
    'biased toward',
    'biases',
    'biases towards',
    'bipoc',
    'black and latinx',
    'community diversity',
    'community equity',
    'cultural differences',
    'cultural heritage',
    'culturally responsive',
    'disabilities',
    'disability',
    'discriminated',
    'discrimination',
    'discriminatory',
    'diverse backgrounds',
    'diverse communities',
    'diverse community',
    'diverse group',
    'diverse groups',
    'diversified',
    'diversify',
    'diversifying',
    'diversity and inclusion',
    'diversity equity',
    'enhance the diversity',
    'enhancing diversity',
    'equal opportunity', 
    'equality', 
    'equitable', 
    'equity', 
    'ethnicity', 
    'excluded', 
    'female', 
    'females',
    'fostering inclusivity',
    'gender', 
    'gender diversity', 
    'genders', 
    'hate speech',
    'hispanic minority',
    'historically',
    'lgbt', 
    'implicit bias', 
    'implicit biases', 
    'inclusion', 
    'inclusive',
    'inclusiveness',
    'inclusivity',
    'increase diversity', 
    'increase the diversity', 
    'indigenous community',
    'inequalities', 
    'inequality', 
    'inequitable', 
    'inequities', 
    'institutional', 
    'marginalize', 
    'marginalized',
    'minorities',
    'minority',
    'multicultural',
    'polarization',
    'political',
    'prejudice', 
    'privileges',
    'promoting diversity',
    'race and ethnicity',
    'racial',
    'racial diversity', 
    'racial inequality',
    'racial justice',
    'racially',
    'racism',
    'sense of belonging',
    'sexual preferences', 
    'social justice',
    'sociocultural',
    'socioeconomic',
    'status',
    'stereotypes',
    'systemic',
    'trauma', 
    'under appreciated',
    'under represented',
    'under served',
    'underrepresentation',
    'underrepresented', 
    'underserved', 
    'undervalued',
    'victim',
    'women',
    'women and underrepresented'
]
