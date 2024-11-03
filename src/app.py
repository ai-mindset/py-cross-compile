import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption


def setup_converter(accurate_mode=False):
    """Create a configured Docling converter"""
    pipeline_options = PdfPipelineOptions(do_table_structure=True)
    mode = TableFormerMode.ACCURATE if accurate_mode else TableFormerMode.FAST
    pipeline_options.table_structure_options.mode = mode

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )


def convert_pdf_thread(pdf_path, accurate_mode, status_var, ui_elements):
    """Handle PDF conversion in a separate thread"""
    try:
        converter = setup_converter(accurate_mode)
        result = converter.convert(pdf_path)
        markdown = result.document.export_to_markdown()

        # Update UI in main thread
        ui_elements["root"].after(
            0, lambda: conversion_complete(markdown, status_var, ui_elements)
        )
    except Exception as e:
        ui_elements["root"].after(
            0, lambda: conversion_error(str(e), status_var, ui_elements)
        )


def conversion_complete(markdown, status_var, ui_elements):
    """Handle successful conversion"""
    ui_elements["output_text"].delete("1.0", tk.END)
    ui_elements["output_text"].insert("1.0", markdown)
    status_var.set("Conversion completed!")
    ui_elements["select_btn"].configure(state="normal")
    ui_elements["save_btn"].configure(state="normal")
    ui_elements["progress"].stop()
    ui_elements["progress"].grid_remove()


def conversion_error(error_msg, status_var, ui_elements):
    """Handle conversion error"""
    status_var.set(f"Error: {error_msg}")
    ui_elements["select_btn"].configure(state="normal")
    ui_elements["progress"].stop()
    ui_elements["progress"].grid_remove()


def save_markdown(output_text, status_var):
    """Save markdown content to file"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".md",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
    )

    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output_text.get("1.0", tk.END))
            status_var.set("File saved successfully!")
        except Exception as e:
            status_var.set(f"Error saving file: {str(e)}")


def select_pdf(accurate_mode, status_var, ui_elements):
    """Handle PDF file selection and start conversion"""
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )

    if file_path:
        # Update UI state
        status_var.set(f"Converting: {Path(file_path).name}")
        ui_elements["select_btn"].configure(state="disabled")
        ui_elements["save_btn"].configure(state="disabled")
        ui_elements["output_text"].delete("1.0", tk.END)
        ui_elements["progress"].grid()
        ui_elements["progress"].start()

        # Start conversion in separate thread
        thread = threading.Thread(
            target=convert_pdf_thread,
            args=(file_path, accurate_mode.get(), status_var, ui_elements),
            daemon=True,
        )
        thread.start()


def create_ui():
    """Create the main UI"""
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

    # UI Elements dictionary
    ui_elements = {}
    ui_elements["root"] = root

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
    progress.grid_remove()
    ui_elements["progress"] = progress

    # Output text area
    output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
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


def main():
    root = create_ui()
    root.mainloop()


if __name__ == "__main__":
    main()
