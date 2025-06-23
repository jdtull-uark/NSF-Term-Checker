# NSF Language Checker API

This project provides a FastAPI-based web service for analyzing and highlighting flagged terms in PDF-formatted proposals, with optional support for custom term lists via Excel files. It is designed to help review proposals for specific language commonly flagged in NSF proposals.

## Features

- **/flag-terms/**: Upload a PDF (and optionally an Excel file of terms) to receive a JSON report of flagged terms and their occurrences.
- **/highlight-terms/**: Upload a PDF (and optionally an Excel file of terms) to receive a PDF with all flagged terms highlighted.
- Uses a default list of diversity-related terms if no Excel file is provided.
- CORS enabled for easy integration with web frontends.

## Folder Structure

- [`main.py`](main.py): FastAPI server with endpoints for flagging and highlighting terms in PDFs.
- [`api_profile.py`](api_profile.py): Script for profiling and testing the API endpoints.
- `requirements.txt`: Python dependencies.
- `.gitignore`: Files and folders excluded from version control.
- `Flagged Terms.xlsx`: Example Excel file for custom flagged terms.
- `diversity_paper_output.pdf`, `diversity_paper2.pdf`: Example PDF files for testing.

## Requirements

- Python 3.10+
- See [`requirements.txt`](requirements.txt) for all dependencies.

## Installation

1. Clone this repository.
2. (Recommended) Create and activate a virtual environment:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Running the API Server

```sh
uvicorn main:app --reload
```

- The API will be available at `http://127.0.0.1:8000`.

### Endpoints

#### `/flag-terms/` (POST)

- **Parameters**:
  - `pdf_file`: PDF file to analyze (required)
  - `excel_file`: Excel file with custom terms (optional)
- **Returns**: JSON with flagged terms, counts, and page numbers.

#### `/highlight-terms/` (POST)

- **Parameters**:
  - `pdf_file`: PDF file to highlight (required)
  - `excel_file`: Excel file with custom terms (optional)
- **Returns**: PDF with highlighted terms.

### Example: Profiling the API

Use [`api_profile.py`](api_profile.py) to test and profile the endpoints:

```sh
python api_profile.py
```

## Customizing Flagged Terms

- By default, the API uses a built-in list of diversity-related terms.
- To use your own list, upload an Excel file (`.xlsx`) with the terms in the first column.

## License

This project is for internal/proposal review use. Please adapt as needed for your organization.

---
