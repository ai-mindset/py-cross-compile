"""
Complete PDF to Markdown converter using Docling, with a simple TkInter GUI.
Handles PDF conversion with proper stream handling.
"""

import logging
import os
import sys
import tkinter as tk
from functools import partial, wraps
from io import BytesIO
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any

from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption

# Set up logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("converter.log", encoding="utf-8"),
    ],
)

# Type alias for UI elements dictionary
UIElements = dict[str, Any]


def handle_exceptions(func):
    """Decorator to handle exceptions in GUI functions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    return wrapper


def validate_pdf_file(file_path: str | Path) -> bool:
    """
    Validate if the file is a valid PDF.

    Args:
        file_path: Path to the PDF file (string or Path object)

    Returns:
        bool: True if valid

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a PDF or is empty
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {path}")

    if path.stat().st_size == 0:
        raise ValueError(f"PDF file is empty: {path}")

    return True


@handle_exceptions
def setup_converter(accurate_mode: bool = False) -> DocumentConverter:
    """
    Configure and return a Docling DocumentConverter instance.

    Args:
        accurate_mode: Whether to use accurate table mode (slower but better quality)

    Returns:
        DocumentConverter: Configured converter instance
    """
    pipeline_options = PdfPipelineOptions(do_table_structure=True)
    mode = TableFormerMode.ACCURATE if accurate_mode else TableFormerMode.FAST
    pipeline_options.table_structure_options.mode = mode

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )


def convert_pdf_thread(
    pdf_path: str,
    accurate_mode: bool,
    status_var: tk.StringVar,
    ui_elements: UIElements,
    chunk_size: int = 1024 * 1024,
) -> None:
    """
    Handle PDF conversion in a separate thread.

    Args:
        pdf_path: Path to the PDF file
        accurate_mode: Whether to use accurate table mode
        status_var: StringVar for status updates
        ui_elements: Dictionary containing UI elements
        chunk_size: Size of chunks for file operations
    """
    pdf_bytes = None
    try:
        if not validate_pdf_file(pdf_path):
            return

        converter = setup_converter(accurate_mode)

        # Read file into BytesIO
        with open(pdf_path, "rb") as f:
            pdf_bytes = BytesIO(f.read())

        # Create DocumentStream with correct parameters
        doc_stream = DocumentStream(name=os.path.basename(pdf_path), stream=pdf_bytes)

        result = converter.convert(doc_stream)

        if result is None:
            raise ValueError("Conversion failed: No output generated")

        markdown = result.document.export_to_markdown()
        if not markdown:
            raise ValueError("Conversion failed: Empty output")

        # Update UI in main thread
        ui_elements["root"].after(
            0, partial(conversion_complete, markdown, status_var, ui_elements)
        )

    except Exception as e:
        logging.error(f"Error converting PDF: {str(e)}", exc_info=True)
        ui_elements["root"].after(
            0, partial(conversion_error, str(e), status_var, ui_elements)
        )

    finally:
        if pdf_bytes:
            pdf_bytes.close()


def conversion_complete(
    markdown: str, status_var: tk.StringVar, ui_elements: UIElements
) -> None:
    """
    Handle successful PDF conversion.

    Args:
        markdown: Converted markdown text
        status_var: StringVar for status updates
        ui_elements: Dictionary containing UI elements
    """
    try:
        ui_elements["output_text"].delete("1.0", tk.END)
        ui_elements["output_text"].insert("1.0", markdown)
        status_var.set("Conversion completed!")
        ui_elements["select_btn"].configure(state="normal")
        ui_elements["save_btn"].configure(state="normal")
        ui_elements["progress"].stop()
        ui_elements["progress"].grid_remove()
    except Exception as e:  # noqa: BLE001
        logging.error(f"Error completing conversion: {str(e)}")
        messagebox.showerror("Error", "Failed to display conversion results")


def conversion_error(
    error_msg: str, status_var: tk.StringVar, ui_elements: UIElements
) -> None:
    """
    Handle PDF conversion errors.

    Args:
        error_msg: Error message to display
        status_var: StringVar for status updates
        ui_elements: Dictionary containing UI elements
    """
    status_var.set(f"Error: {error_msg}")
    ui_elements["select_btn"].configure(state="normal")
    ui_elements["progress"].stop()
    ui_elements["progress"].grid_remove()
    logging.error(f"Conversion error: {error_msg}")
    messagebox.showerror("Conversion Error", error_msg)


@handle_exceptions
def save_markdown(
    output_text: scrolledtext.ScrolledText,
    status_var: tk.StringVar,
    chunk_size: int = 1024 * 1024,
) -> None:
    """
    Save markdown content to a file.

    Args:
        output_text: ScrolledText widget containing markdown
        status_var: StringVar for status updates
        chunk_size: Size of chunks for file operations
    """
    content = output_text.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("Warning", "No content to save")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".md",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
    )

    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for i in range(0, len(content), chunk_size):
                    f.write(content[i : i + chunk_size])
            status_var.set("File saved successfully!")
            logging.info(f"Markdown saved to: {file_path}")
        except Exception as e:  # noqa: BLE001
            error_msg = f"Error saving file: {str(e)}"
            status_var.set(error_msg)
            logging.error(error_msg)
            messagebox.showerror("Save Error", error_msg)


@handle_exceptions
def select_pdf(
    accurate_mode: tk.BooleanVar, status_var: tk.StringVar, ui_elements: dict[str, Any]
) -> None:
    """
    Handle PDF file selection and initiate conversion.

    Args:
        accurate_mode: BooleanVar indicating if accurate mode is enabled
        status_var: StringVar for status updates
        ui_elements: Dictionary containing UI elements
    """
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )

    if file_path:
        try:
            # Validate file
            validate_pdf_file(file_path)

            # Update UI for conversion
            status_var.set(f"Converting: {Path(file_path).name}")
            ui_elements["select_btn"].configure(state="disabled")
            ui_elements["save_btn"].configure(state="disabled")
            ui_elements["output_text"].delete("1.0", tk.END)
            ui_elements["progress"].grid()

            # Start conversion
            convert_pdf_thread(file_path, accurate_mode.get(), status_var, ui_elements)

        except (FileNotFoundError, ValueError, Exception) as e:
            # Handle errors consistently
            status_var.set(f"Error: {str(e)}")
            ui_elements["select_btn"].configure(state="normal")
            ui_elements["progress"].grid_remove()


def create_ui() -> tk.Tk:
    """
    Create and configure the main UI window.

    Returns:
        tk.Tk: Configured root window with all widgets
    """
    root = tk.Tk()
    root.title("Docling PDF to Markdown Converter")
    root.geometry("800x600")

    # Configure grid weight
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(2, weight=1)

    # Status label
    status_var = tk.StringVar(value="Select a PDF file to convert")
    status_label = ttk.Label(root, textvariable=status_var)
    status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    # Button frame
    btn_frame = ttk.Frame(root)
    btn_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    # Dictionary to store UI elements
    ui_elements = {"root": root}

    # Accurate mode checkbox
    accurate_mode = tk.BooleanVar(value=False)
    accurate_check = ttk.Checkbutton(
        btn_frame, text="Accurate Table Mode", variable=accurate_mode
    )
    accurate_check.pack(side=tk.LEFT, padx=5)

    # Select button
    select_btn = ttk.Button(
        btn_frame,
        text="Select PDF",
        command=lambda: select_pdf(accurate_mode, status_var, ui_elements),
    )
    select_btn.pack(side=tk.LEFT, padx=5)
    ui_elements["select_btn"] = select_btn

    # Progress bar
    progress = ttk.Progressbar(root, mode="indeterminate", length=300)
    progress.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
    progress.grid_remove()  # Hidden by default
    ui_elements["progress"] = progress

    # Output text area
    output_text = ScrolledText(root, wrap=tk.WORD, width=80, height=20)
    output_text.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
    ui_elements["output_text"] = output_text

    # Save button
    save_btn = ttk.Button(
        root,
        text="Save Markdown",
        command=lambda: save_markdown(output_text, status_var),
        state="disabled",
    )
    save_btn.grid(row=4, column=0, padx=10, pady=5)
    ui_elements["save_btn"] = save_btn

    return root


def main() -> None:
    """Entry point for the application."""
    try:
        root = create_ui()
        root.mainloop()
    except Exception as e:  # noqa: BLE001
        logging.critical(f"Application error: {str(e)}", exc_info=True)
        messagebox.showerror("Critical Error", "Application failed to start properly")
        sys.exit(1)


if __name__ == "__main__":
    main()
