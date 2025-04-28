from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import pandas as pd
import fitz  # PyMuPDF
import io

app = FastAPI()

@app.post("/highlight-terms/")
async def highlight_terms(excel_file: UploadFile = File(...), pdf_file: UploadFile = File(...)):
    # Read uploaded files into memory
    excel_contents = await excel_file.read()
    pdf_contents = await pdf_file.read()

    # Process Excel file in memory
    words_to_check = read_excel_words(io.BytesIO(excel_contents))

    # Process PDF file in memory and get output bytes
    output_pdf_stream = check_words_in_text(words_to_check, io.BytesIO(pdf_contents))

    # Return the modified PDF to user
    return StreamingResponse(output_pdf_stream, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=highlighted_output.pdf"})



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
