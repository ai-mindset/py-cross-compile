"""Pytest fixtures for testing the PDF converter application."""

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

import pytest
from pytest import FixtureRequest, TempPathFactory

from .test_helpers import create_test_root


@pytest.fixture
def tmp_path(request: FixtureRequest, tmp_path_factory: TempPathFactory) -> Path:
    """Built-in pytest fixture that provides a unique temporary directory."""
    return tmp_path_factory.mktemp("data")


@pytest.fixture
def mock_ui():
    """Fixture providing UI elements without requiring a display."""
    root = create_test_root()

    status_var = tk.StringVar()
    output_text = ScrolledText(root)
    select_btn = ttk.Button(root)
    save_btn = ttk.Button(root)
    progress = ttk.Progressbar(root)

    # Initialize widget states
    select_btn.configure(state="normal")
    save_btn.configure(state="disabled")

    ui_elements = {
        "root": root,
        "select_btn": select_btn,
        "save_btn": save_btn,
        "progress": progress,
        "output_text": output_text,
    }

    yield root, status_var, output_text, ui_elements

    try:
        root.destroy()
    except:
        pass


@pytest.fixture
def sample_pdf(tmp_path) -> Path:
    """
    Create a minimal valid PDF file for testing.

    Args:
        tmp_path: pytest built-in fixture for temporary directory

    Returns:
        Path: Path to the test PDF file
    """
    pdf_content = b"""%PDF-1.7
1 0 obj
<< /Type /Catalog
   /Pages 2 0 R
>>
endobj

2 0 obj
<< /Type /Pages
   /Kids [3 0 R]
   /Count 1
>>
endobj

3 0 obj
<< /Type /Page
   /Parent 2 0 R
   /MediaBox [0 0 612 792]
   /Contents 4 0 R
>>
endobj

4 0 obj
<< /Length 51 >>
stream
BT
/F1 12 Tf
72 712 Td
(Test PDF Document) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f
0000000010 00000 n
0000000064 00000 n
0000000125 00000 n
0000000210 00000 n
trailer
<< /Size 5
   /Root 1 0 R
>>
startxref
312
%%EOF"""

    # Create PDF in temporary directory
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(pdf_content)

    yield pdf_path

    # Cleanup happens automatically as tmp_path is managed by pytest


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """
    Fixture providing a temporary directory for output files.

    Args:
        tmp_path: pytest built-in fixture for temporary directory

    Returns:
        Path: Path to the temporary output directory
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def ui_setup():
    """
    Fixture providing UI elements for tests.

    Returns:
        tuple: (root, status_var, output_text, ui_elements)
    """
    root = tk.Tk()
    status_var = tk.StringVar()
    output_text = ScrolledText(root)
    ui_elements = {
        "root": root,
        "select_btn": ttk.Button(root),
        "save_btn": ttk.Button(root),
        "progress": ttk.Progressbar(root),
        "output_text": output_text,
    }

    yield root, status_var, output_text, ui_elements

    root.destroy()
