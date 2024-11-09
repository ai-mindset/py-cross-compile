"""PDF to Text converter using pypdf."""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Any, Final

from pypdf import PdfReader


def get_resource_path() -> Path:
    """Get the absolute path to the resources directory.

    Returns:
        Path: Absolute path to resources directory
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        # Normal Python installation
        base_path = Path(__file__).resolve().parent

    return base_path / "resources"


RESOURCE_PATH: Final[Path] = get_resource_path()


def get_resource_file(filename: str) -> Path:
    """Get path to a specific resource file.

    Args:
        filename: Name of the resource file

    Returns:
        Path: Absolute path to the resource file
    """
    return RESOURCE_PATH / filename


def validate_pdf_file(file_path: str | Path) -> bool:
    """
    Validate if the file is a valid PDF.

    Args:
        file_path: Path to the PDF file

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


def convert_pdf_to_text(file_path: str | Path) -> str:
    """
    Convert PDF to text.

    Args:
        file_path: Path to PDF file

    Returns:
        str: Extracted text
    """
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text())
    return "\n\n".join(text)


def convert_pdf_thread(
    file_path: str | Path,
    accurate_mode: bool,
    status_var: tk.StringVar,
    ui_elements: dict[str, Any],
) -> None:
    """Convert PDF in a separate thread."""
    try:
        text = convert_pdf_to_text(file_path)
        ui_elements["root"].after(
            0, lambda: conversion_complete(text, status_var, ui_elements)
        )
    except Exception as e:  # noqa: BLE001
        error: str = str(e)
        ui_elements["root"].after(
            0, lambda: conversion_error(error, status_var, ui_elements)
        )


def conversion_complete(
    text: str,
    status_var: tk.StringVar,
    ui_elements: dict[str, Any],
) -> None:
    """Handle successful conversion."""
    ui_elements["output_text"].delete("1.0", tk.END)
    ui_elements["output_text"].insert("1.0", text)
    status_var.set("Conversion completed!")
    ui_elements["select_btn"].configure(state="normal")
    ui_elements["save_btn"].configure(state="normal")
    ui_elements["progress"].grid_remove()


def conversion_error(
    error_msg: str,
    status_var: tk.StringVar,
    ui_elements: dict[str, Any],
) -> None:
    """Handle conversion error."""
    status_var.set(f"Error: {error_msg}")
    ui_elements["select_btn"].configure(state="normal")
    ui_elements["progress"].grid_remove()


def save_markdown(
    output_text: ScrolledText,
    status_var: tk.StringVar,
) -> None:
    """Save text content to file."""
    content = output_text.get("1.0", tk.END).strip()
    if not content:
        status_var.set("No content to save")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )

    if file_path:
        try:
            Path(file_path).write_text(content, encoding="utf-8")
            status_var.set("File saved successfully!")
        except Exception as e:  # noqa: BLE001
            status_var.set(f"Error saving file: {e}")


def select_pdf(
    accurate_mode: tk.BooleanVar,
    status_var: tk.StringVar,
    ui_elements: dict[str, Any],
) -> None:
    """Handle PDF file selection and conversion."""
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )

    if file_path:
        try:
            validate_pdf_file(file_path)
            status_var.set(f"Converting: {Path(file_path).name}")
            ui_elements["select_btn"].configure(state="disabled")
            ui_elements["save_btn"].configure(state="disabled")
            ui_elements["output_text"].delete("1.0", tk.END)
            ui_elements["progress"].grid()
            convert_pdf_thread(file_path, accurate_mode.get(), status_var, ui_elements)

        except Exception as e:  # noqa: BLE001
            status_var.set(f"Error: {str(e)}")
            ui_elements["select_btn"].configure(state="normal")
            ui_elements["progress"].grid_remove()


def create_ui() -> tk.Tk:
    """Create and configure the main UI window."""
    root = tk.Tk()
    root.title("PDF to Text Converter")
    root.geometry("800x600")

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(2, weight=1)

    status_var = tk.StringVar(value="Select a PDF file to convert")
    ttk.Label(root, textvariable=status_var).grid(
        row=0, column=0, padx=10, pady=5, sticky="w"
    )

    btn_frame = ttk.Frame(root)
    btn_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    ui_elements = {"root": root}

    accurate_mode = tk.BooleanVar(value=False)
    ttk.Checkbutton(btn_frame, text="Accurate Table Mode", variable=accurate_mode).pack(
        side=tk.LEFT, padx=5
    )

    select_btn = ttk.Button(
        btn_frame,
        text="Select PDF",
        command=lambda: select_pdf(accurate_mode, status_var, ui_elements),
    )
    select_btn.pack(side=tk.LEFT, padx=5)
    ui_elements["select_btn"] = select_btn  # type: ignore

    progress = ttk.Progressbar(root, mode="indeterminate", length=300)
    progress.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
    progress.grid_remove()
    ui_elements["progress"] = progress  # type: ignore

    output_text = ScrolledText(root, wrap=tk.WORD, width=80, height=20)
    output_text.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
    ui_elements["output_text"] = output_text  # type: ignore

    save_btn = ttk.Button(
        root,
        text="Save Text",
        command=lambda: save_markdown(output_text, status_var),
        state="disabled",
    )
    save_btn.grid(row=4, column=0, padx=10, pady=5)
    ui_elements["save_btn"] = save_btn  # type: ignore

    # Example of using resources
    info_file = get_resource_file(".gitkeep")
    if info_file.exists():
        with info_file.open() as f:
            info_text = f.read()
            ttk.Label(root, text=info_text).pack()

    return root


def main() -> None:
    """Application entry point."""
    root = create_ui()
    root.mainloop()


if __name__ == "__main__":
    main()
