import os
import sys
import logging
from typing import List, Literal

OutputFmt = Literal['xml', 'markdown']

def _write_one_file_xml(outfile, rel_path, abs_path, skip_binfiles=None):
    if is_binary_file(abs_path):
        if skip_binfiles is not None:
            skip_binfiles.append(rel_path)
        return
    outfile.write(f"{rel_path}:\n<code>\n")
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as infile:
            outfile.write(infile.read())
    except Exception:
        outfile.write(".. contents skipped (read error) ..")
    outfile.write("\n</code>\n\n")

from aicodeprep_gui.smart_logic import is_binary_file

def _write_one_file_md(outfile, rel_path, abs_path, skip_binfiles=None):
    if is_binary_file(abs_path):
        if skip_binfiles is not None:
            skip_binfiles.append(rel_path)
        return
    outfile.write(f"### START OF FILE {rel_path} ###\n")
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as infile:
            outfile.write(infile.read())
    except Exception:
        outfile.write(".. contents skipped (read error) ..\n")
    outfile.write(f"\n### END OF FILE {rel_path} ###\n\n")

def process_files(
    selected_files: List[str],
    output_file: str,
    fmt: OutputFmt = 'xml',
    prompt: str = "",
    prompt_to_top: bool = False,
    prompt_to_bottom: bool = True
) -> int:
    """
    Process selected files and write their contents to output_file.
    Optionally prepend and/or append a prompt/question.
    Returns the number of files processed.
    """
    try:
        output_path = os.path.join(os.getcwd(), output_file)
        logging.info(f"Writing output to: {output_path}")

        skip_binfiles = []
        writer = _write_one_file_xml if fmt == 'xml' else _write_one_file_md

        with open(output_path, 'w', encoding='utf-8') as outfile:
            # Write prompt at the top if requested
            if prompt and prompt_to_top:
                outfile.write(prompt.strip() + "\n\n")

            for file_path in selected_files:
                try:
                    try:
                        rel_path = os.path.relpath(file_path, os.getcwd())
                    except ValueError:
                        rel_path = file_path
                    writer(outfile, rel_path, file_path, skip_binfiles=skip_binfiles)
                    logging.info(f"Processed: {rel_path}")
                except Exception as exc:
                    logging.error(f"Error processing {file_path}: {exc}")

            if skip_binfiles:
                outfile.write("\n")
                for rel_path in skip_binfiles:
                    outfile.write(f"{rel_path} binary file skipped..\n")

            # Write prompt at the bottom if requested
            if prompt and prompt_to_bottom:
                outfile.write("\n\n" + prompt.strip())

        return len(selected_files)
    except Exception as exc:
        logging.error(f"Error writing output file: {exc}")
        return 0
