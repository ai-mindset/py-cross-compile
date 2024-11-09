import os
import tempfile
from pathlib import Path
from tkinter import END, Button, StringVar, Tk, ttk
from tkinter.scrolledtext import ScrolledText
from unittest.mock import Mock, patch

import pytest
from src.pdf_converter.app import (
    conversion_complete,
    conversion_error,
    convert_pdf_to_text,
    save_markdown,
    validate_pdf_file,
)


## % Fixtures
@pytest.fixture
def sample_pdf():
    """Create a temporary valid PDF file."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(b"%PDF-1.4\n%TEST PDF")
    yield Path(tmp.name)
    os.unlink(tmp.name)


@pytest.fixture
def empty_pdf():
    """Create a temporary empty PDF file."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pass
    yield Path(tmp.name)
    os.unlink(tmp.name)


@pytest.fixture
def tk_root():
    """Create and yield a Tk root instance."""
    root = Tk()
    yield root
    root.destroy()


@pytest.fixture
def tk_elements(tk_root):
    """Set up basic tkinter elements needed for testing."""
    root = Tk()
    elements = {
        "root": root,
        "output_text": ScrolledText(root),
        "select_btn": Button(root),
        "save_btn": Button(root),
        "progress": ttk.Progressbar(root),
    }
    yield elements
    root.destroy()


## % File Validation Tests
def test_valid_pdf_file_passes_validation(sample_pdf):
    assert validate_pdf_file(sample_pdf) is True


def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        validate_pdf_file("nonexistent.pdf")


def test_empty_pdf_file_raises_error(empty_pdf):
    with pytest.raises(ValueError, match="PDF file is empty"):
        validate_pdf_file(empty_pdf)


def test_non_pdf_file_raises_error(tmp_path):
    text_file = tmp_path / "test.txt"
    text_file.write_text("not a pdf")
    with pytest.raises(ValueError, match="File is not a PDF"):
        validate_pdf_file(text_file)


## % PDF Conversion Tests
@patch("src.pdf_converter.app.PdfReader")
def test_pdf_conversion_extracts_text_from_all_pages(mock_pdf_reader, sample_pdf):
    # Setup mock pages
    page1, page2 = Mock(), Mock()
    page1.extract_text.return_value = "First page"
    page2.extract_text.return_value = "Second page"
    mock_pdf_reader.return_value.pages = [page1, page2]

    result = convert_pdf_to_text(sample_pdf)

    assert result == "First page\n\nSecond page"
    mock_pdf_reader.assert_called_once_with(sample_pdf)


## % UI Callback Tests
def test_successful_conversion_updates_ui(tk_elements):
    status_var = StringVar(master=tk_elements["root"])
    test_text = "Converted PDF content"

    conversion_complete(test_text, status_var, tk_elements)

    assert status_var.get() == "Conversion completed!"
    assert tk_elements["select_btn"]["state"] == "normal"
    assert tk_elements["save_btn"]["state"] == "normal"
    assert tk_elements["output_text"].get("1.0", END).strip() == test_text


def test_conversion_error_shows_error_message(tk_elements):
    status_var = StringVar(master=tk_elements["root"])
    error_msg = "Failed to convert PDF"

    conversion_error(error_msg, status_var, tk_elements)

    assert status_var.get() == f"Error: {error_msg}"
    assert tk_elements["select_btn"]["state"] == "normal"


## % File Saving Tests
def test_cannot_save_empty_content(tk_root):
    output_text = Mock()
    output_text.get.return_value = "   "
    status_var = StringVar(master=tk_root)

    save_markdown(output_text, status_var)

    assert status_var.get() == "No content to save"


@patch("src.pdf_converter.app.filedialog.asksaveasfilename")
def test_saves_content_to_file_successfully(mock_save_dialog, tmp_path, tk_root):
    test_content = "PDF content to save"
    output_text = Mock()
    output_text.get.return_value = test_content
    status_var = StringVar(master=tk_root)

    save_path = tmp_path / "test_output.txt"
    mock_save_dialog.return_value = str(save_path)

    save_markdown(output_text, status_var)

    assert status_var.get() == "File saved successfully!"
    assert save_path.read_text(encoding="utf-8") == test_content
