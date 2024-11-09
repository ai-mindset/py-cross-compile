"""Unit tests for the PDF converter application."""

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from unittest.mock import Mock, patch

import pytest
from docling.document_converter import DocumentConverter
from docling_converter.app import (
    conversion_complete,
    conversion_error,
    convert_pdf_thread,
    create_ui,
    save_markdown,
    select_pdf,
    setup_converter,
    validate_pdf_file,
)


def test_validate_pdf_file(sample_pdf):
    """Test PDF file validation with different path types."""
    # Test with Path object
    assert validate_pdf_file(sample_pdf) is True

    # Test with string path
    assert validate_pdf_file(str(sample_pdf)) is True

    # Test non-existent file
    with pytest.raises(FileNotFoundError):
        validate_pdf_file(Path("nonexistent.pdf"))

    # Test non-PDF file
    text_file = sample_pdf.parent / "test.txt"
    text_file.write_text("test")
    with pytest.raises(ValueError, match="not a PDF"):
        validate_pdf_file(text_file)
    text_file.unlink()

    # Test empty PDF
    empty_pdf = sample_pdf.parent / "empty.pdf"
    empty_pdf.write_bytes(b"")
    with pytest.raises(ValueError, match="empty"):
        validate_pdf_file(empty_pdf)
    empty_pdf.unlink()


def test_setup_converter():
    """Test converter setup with different modes."""
    # Test fast mode
    converter_fast = setup_converter(accurate_mode=False)
    assert isinstance(converter_fast, DocumentConverter)

    # Test accurate mode
    converter_accurate = setup_converter(accurate_mode=True)
    assert isinstance(converter_accurate, DocumentConverter)


@patch("docling_converter.app.DocumentConverter")
def test_convert_pdf_thread(mock_converter, mock_ui, sample_pdf):
    """Test PDF conversion thread."""
    root, status_var, _, ui_elements = mock_ui

    # Mock converter
    mock_instance = Mock()
    mock_converter.return_value = mock_instance
    mock_instance.convert.return_value = Mock(
        document=Mock(export_to_markdown=Mock(return_value="# Test Markdown"))
    )

    # Test conversion
    convert_pdf_thread(str(sample_pdf), False, status_var, ui_elements)

    mock_converter.assert_called_once()
    mock_instance.convert.assert_called_once()


def test_conversion_complete(mock_ui):
    """Test successful conversion handling."""
    root, status_var, _, ui_elements = mock_ui

    test_markdown = "# Test Markdown"
    conversion_complete(test_markdown, status_var, ui_elements)

    assert ui_elements["output_text"].get("1.0", tk.END).strip() == test_markdown
    assert status_var.get() == "Conversion completed!"


def test_conversion_error(ui_setup):
    """Test error handling during conversion."""
    root, status_var, _, ui_elements = ui_setup

    error_msg = "Test error"
    conversion_error(error_msg, status_var, ui_elements)

    assert status_var.get() == f"Error: {error_msg}"


@pytest.mark.parametrize(
    "content,dialog_shown",
    [
        ("# Test Content", True),
        ("", False),
    ],
)
def test_save_markdown(mock_ui_elements, temp_output_dir, content, dialog_shown):
    """
    Test markdown saving functionality.

    Args:
        mock_ui_elements: Fixture providing UI elements
        temp_output_dir: Fixture providing temporary output directory
        content: Content to save
        dialog_shown: Whether file dialog should be shown
    """
    _, status_var, output_text, _ = mock_ui_elements
    output_file = temp_output_dir / "test.md"

    with patch("tkinter.filedialog.asksaveasfilename") as mock_dialog:
        mock_dialog.return_value = str(output_file)

        output_text.delete("1.0", tk.END)
        output_text.insert("1.0", content)
        save_markdown(output_text, status_var)

        assert mock_dialog.called == dialog_shown

        if content:
            assert output_file.read_text().strip() == content
            assert status_var.get() == "File saved successfully!"


@patch("docling_converter.app.convert_pdf_thread")
def test_select_pdf(mock_convert, ui_setup, sample_pdf):
    """Test PDF file selection."""
    root, status_var, _, ui_elements = ui_setup

    with patch("tkinter.filedialog.askopenfilename", return_value=str(sample_pdf)):
        select_pdf(tk.BooleanVar(), status_var, ui_elements)

        assert status_var.get() == f"Converting: {sample_pdf.name}"
        mock_convert.assert_called_once()


@pytest.fixture
def mock_ui_elements():
    """Fixture providing mocked UI elements with headless configuration."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    status_var = tk.StringVar(value="Initial state")
    output_text = ScrolledText(root)
    select_btn = ttk.Button(root)
    save_btn = ttk.Button(root)
    progress = ttk.Progressbar(root)

    # Initialize widget states
    select_btn.configure(state="normal")
    save_btn.configure(state="disabled")
    progress.grid_remove()

    ui_elements = {
        "root": root,
        "output_text": output_text,
        "select_btn": select_btn,
        "save_btn": save_btn,
        "progress": progress,
    }

    yield root, status_var, output_text, ui_elements
    root.destroy()


@pytest.fixture
def ui_root():
    """Fixture providing the UI root for testing in headless mode."""
    root = create_ui()
    root.withdraw()  # Hide the root window
    yield root
    root.destroy()


def test_window_basics(ui_root):
    """Test basic window properties."""
    assert isinstance(ui_root, tk.Tk)
    assert ui_root.title() == "Docling PDF to Markdown Converter"
    assert ui_root.geometry() == "1x1+0+0"


def test_window_grid_config(ui_root):
    """Test window grid configuration."""
    assert ui_root.grid_columnconfigure(0)["weight"] == 1
    assert ui_root.grid_rowconfigure(2)["weight"] == 1


def test_status_label(ui_root):
    """Test status label configuration."""
    status_labels = [w for w in ui_root.winfo_children() if isinstance(w, ttk.Label)]
    assert len(status_labels) == 1
    status_label = status_labels[0]
    assert status_label.cget("text") == "Select a PDF file to convert"


def test_button_frame_exists(ui_root):
    """Test button frame existence and configuration."""
    frames = [w for w in ui_root.winfo_children() if isinstance(w, ttk.Frame)]
    assert len(frames) == 1
    btn_frame = frames[0]
    assert btn_frame.grid_info()["row"] == 1
    assert btn_frame.grid_info()["sticky"] == "ew"


def test_button_frame_contents(ui_root):
    """Test buttons within the button frame."""
    btn_frame = next(w for w in ui_root.winfo_children() if isinstance(w, ttk.Frame))

    # Check checkbox
    checkbuttons = [
        w for w in btn_frame.winfo_children() if isinstance(w, ttk.Checkbutton)
    ]
    assert len(checkbuttons) == 1
    assert checkbuttons[0].cget("text") == "Accurate Table Mode"

    # Check PDF selection button
    buttons = [w for w in btn_frame.winfo_children() if isinstance(w, ttk.Button)]
    assert any(b.cget("text") == "Select PDF" for b in buttons)


def test_progress_bar(ui_root):
    """Test progress bar configuration."""
    progress_bars = [
        w for w in ui_root.winfo_children() if isinstance(w, ttk.Progressbar)
    ]
    assert len(progress_bars) == 1
    progress = progress_bars[0]
    assert progress.cget("length") == 300
    assert not progress.winfo_viewable()  # Should be hidden by default


def test_save_button(ui_root):
    """Test save button configuration."""
    save_buttons = [
        w
        for w in ui_root.winfo_children()
        if isinstance(w, ttk.Button) and w.cget("text") == "Save Markdown"
    ]
    assert len(save_buttons) == 1
    save_btn = save_buttons[0]
    assert save_btn.grid_info()["row"] == 4


def test_widget_layout_order(ui_root):
    """Test the layout order of main widgets."""
    widgets = ui_root.winfo_children()
    widget_types = [type(w) for w in widgets]

    expected_order = [
        ttk.Label,
        ttk.Frame,
        ttk.Progressbar,
        tk.Frame,
        ttk.Button,
        ttk.Label,
    ]

    for actual, expected in zip(widget_types, expected_order, strict=False):
        assert actual == expected


@pytest.mark.parametrize(
    "error_type,error_msg,expected_status",
    [
        (FileNotFoundError, "File not found", "Error: File not found"),
        (ValueError, "Invalid PDF", "Error: Invalid PDF"),
        (Exception, "Unknown error", "Error: Unknown error"),
    ],
)
def test_error_handling(mock_ui_elements, error_type, error_msg, expected_status):
    """
    Test error handling in PDF selection and validation.

    Args:
        mock_ui_elements: Fixture providing UI elements
        error_type: Type of error to simulate
        error_msg: Error message to use
        expected_status: Expected status message after error
    """
    # Setup
    root, status_var, _, ui_elements = mock_ui_elements

    # Verify initial state
    assert not ui_elements["progress"].winfo_viewable()

    # Mock the validation function to raise our test error
    with patch("docling_converter.app.validate_pdf_file") as mock_validate:
        mock_validate.side_effect = error_type(error_msg)

        # Mock the file dialog to return a "selected" file
        with patch("tkinter.filedialog.askopenfilename", return_value="test.pdf"):
            # Trigger the PDF selection
            select_pdf(tk.BooleanVar(value=False), status_var, ui_elements)

            # Verify error handling
            assert status_var.get() == expected_status
            assert not ui_elements["progress"].winfo_viewable()

            # Verify validation was called
            mock_validate.assert_called_once_with("test.pdf")


# TkInter checks - Remove if GitHub Action keeps throwing an error
# - test_validate_pdf_file
# - test_setup_converter
# - test_convert_pdf_thread
# - test_save_markdown
# - test_error_handling
