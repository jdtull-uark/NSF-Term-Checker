from fastapi import Response, FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
import pandas as pd
import fitz  # PyMuPDF
import io

app = FastAPI()

@app.post("/highlight-terms/")
async def highlight_terms(
    pdf_file: UploadFile = File(...),
    excel_file: Optional[UploadFile] = File(None),
):
    # Validate that at least excel_file or words are provided
    if not pdf_file:
        raise HTTPException(status_code=400, detail="You must provide a PDF for review.")

    # If Excel file is provided
    if excel_file:
        excel_content = await excel_file.read()
        words_to_check = read_excel_words(io.BytesIO(excel_content))
    else:
        words_to_check = DEFAULT_LIST

    if not words_to_check:
        raise HTTPException(status_code=400, detail="No words provided for checking.")

    pdf_content = await pdf_file.read()
    highlighted_pdf = check_words_in_text(words_to_check, io.BytesIO(pdf_content))

    return StreamingResponse(
        content=highlighted_pdf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=highlighted_output.pdf"}
    )


def read_excel_words(excel_stream):
    """Read Excel file from BytesIO stream."""
    df = pd.read_excel(excel_stream)
    words = df.iloc[:, 0].dropna().tolist()
    return words


def check_words_in_text(words, pdf_stream):
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