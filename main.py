from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import fitz  # PyMuPDF
import io
import json

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
async def highlight_terms(
    excel_file: UploadFile | None = None,
    pdf_file: UploadFile = File(...),
):
    if excel_file:
        excel_contents = await excel_file.read()
        words_to_check = read_excel_words(io.BytesIO(excel_contents))
    else:
        words_to_check = DEFAULT_LIST

    pdf_contents = await pdf_file.read()

    # Highlight and get both PDF stream and found words
    output_pdf_stream = highlight_words_in_text(words_to_check, io.BytesIO(pdf_contents))

    response = StreamingResponse(
        output_pdf_stream,
        media_type="application/pdf",
    )
    return response


def read_excel_words(excel_stream):
    """Read Excel file from BytesIO stream."""
    df = pd.read_excel(excel_stream)
    words = df.iloc[:, 0].dropna().tolist()
    return words

def find_words_in_text(words, pdf_stream):
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    results = {}

    for page_num, page in enumerate(doc, start=1):
        for word in words:
            instances = page.search_for(word)
            if instances:
                if word not in results:
                    results[word] = {"count": 0, "pages": []}
                results[word]["count"] += len(instances)
                results[word]["pages"].append(page_num)

    return results

def highlight_words_in_text(words, pdf_stream):
    """Highlight words in a PDF loaded from BytesIO, and return a new BytesIO with modified PDF."""
    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    found_words = {}

    for page in doc:
        for word in words:
            for inst in page.search_for(word):
                found_words[word] = found_words.get(word, 0) + 1
                highlight = page.add_highlight_annot(inst)
                highlight.update()

    output_stream = io.BytesIO()
    doc.save(output_stream, garbage=4, deflate=True, clean=True)
    output_stream.seek(0)

    return output_stream, found_words

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
