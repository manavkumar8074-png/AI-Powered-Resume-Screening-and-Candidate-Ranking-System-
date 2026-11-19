import os
import subprocess
import tempfile

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".txt", ".jpg", ".jpeg", ".png"
}


def extract_pdf(file_path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF extraction requires the 'pypdf' package. "
            "Install it with: pip install pypdf"
        ) from exc

    text_parts = []
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_docx(file_path):
    from docx import Document
    document = Document(file_path)
    text_parts = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            text_parts.append(text)

    for table in document.tables:
        for row in table.rows:
            cells = []
            for cell in row.cells:
                text = cell.text.strip()
                if text:
                    cells.append(text)
            if cells:
                text_parts.append(" ".join(cells))

    return "\n".join(text_parts)


def extract_doc(file_path):
    temp_dir = tempfile.mkdtemp()
    try:
        output_file = os.path.join(
            temp_dir,
            os.path.splitext(os.path.basename(file_path))[0] + ".txt"
        )

        for command in ("soffice", "libreoffice"):
            try:
                subprocess.run(
                    [
                        command,
                        "--headless",
                        "--convert-to", "txt:Text",
                        "--outdir", temp_dir,
                        file_path,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=False,
                )

                if os.path.exists(output_file):
                    with open(output_file, "r", encoding="utf-8", errors="ignore") as f:
                        return f.read()
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        raise RuntimeError(
            "Could not read .DOC file. Install LibreOffice and make sure soffice is on PATH."
        )
    finally:
        try:
            for name in os.listdir(temp_dir):
                path = os.path.join(temp_dir, name)
                if os.path.isfile(path):
                    os.remove(path)
            os.rmdir(temp_dir)
        except Exception:
            pass


def extract_txt(file_path):
    for encoding in ("utf-8", "utf-16", "cp1252", "latin-1"):
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise RuntimeError("Could not decode TXT resume.")


def extract_image(file_path):
    from importlib import import_module

    try:
        Image = import_module("PIL.Image")
    except ImportError as exc:
        raise RuntimeError(
            "Image extraction requires Pillow. Install it with: pip install Pillow"
        ) from exc

    try:
        pytesseract = import_module("pytesseract")
    except ImportError as exc:
        raise RuntimeError(
            "Image extraction requires pytesseract. "
            "Install it with: pip install pytesseract"
        ) from exc

    image = Image.open(file_path)
    if image.mode != "RGB":
        image = image.convert("RGB")
    return pytesseract.image_to_string(image)


def extract_text_from_resume(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported resume format: {extension}")

    if extension == ".pdf":
        return extract_pdf(file_path)
    if extension == ".docx":
        return extract_docx(file_path)
    if extension == ".doc":
        return extract_doc(file_path)
    if extension == ".txt":
        return extract_txt(file_path)
    if extension in {".jpg", ".jpeg", ".png"}:
        return extract_image(file_path)

    raise ValueError(f"Unsupported resume format: {extension}")
