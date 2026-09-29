#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import os
import json

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QSpinBox, QPushButton, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Qt


class SprucerConfigDialog(QDialog):
    def __init__(self, current_char=" ", current_size=4, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sprucer Settings")
        self.setModal(True)
        self.setMinimumWidth(300)

        self.indent_char = current_char
        self.indent_size = current_size
        self.run_plugin = False

        main_layout = QVBoxLayout()
        char_layout = QHBoxLayout()
        size_layout = QHBoxLayout()
        btn_layout = QHBoxLayout()

        char_label = QLabel("Indentation Character:")
        self.radio_spaces = QRadioButton("Spaces")
        self.radio_tabs = QRadioButton("Tabs")

        if self.indent_char == "\t":
            self.radio_tabs.setChecked(True)
        else:
            self.radio_spaces.setChecked(True)

        self.char_group = QButtonGroup(self)
        self.char_group.addButton(self.radio_spaces)
        self.char_group.addButton(self.radio_tabs)

        char_layout.addWidget(char_label)
        char_layout.addWidget(self.radio_spaces)
        char_layout.addWidget(self.radio_tabs)
        char_layout.addStretch()

        size_label = QLabel("Indentation Multiplier:")
        self.spin_size = QSpinBox()
        self.spin_size.setRange(1, 8)
        self.spin_size.setValue(self.indent_size)

        size_layout.addWidget(size_label)
        size_layout.addWidget(self.spin_size)
        size_layout.addStretch()

        self.btn_run = QPushButton("Run Formatter")
        self.btn_run.setDefault(True)
        self.btn_cancel = QPushButton("Cancel")

        self.btn_run.clicked.connect(self.on_run_clicked)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_run)

        main_layout.addLayout(char_layout)
        main_layout.addLayout(size_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def on_run_clicked(self):
        self.run_plugin = True
        self.indent_char = "\t" if self.radio_tabs.isChecked() else " "
        self.indent_size = self.spin_size.value()
        self.accept()


def run(bk):
    # ==========================================
    # 0. CONFIGURATION & UI
    # ==========================================
    plugin_dir = os.path.dirname(__file__)
    config_path = os.path.join(plugin_dir, 'config.json')

    indent_char = " "
    indent_size = 4

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                indent_char = config.get('indent_char', " ")
                indent_size = config.get('indent_size', 4)
        except Exception:
            pass

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    dialog = SprucerConfigDialog(current_char=indent_char, current_size=indent_size)
    dialog.exec()

    if not dialog.run_plugin:
        return 0

    new_config = {
        'indent_char': dialog.indent_char,
        'indent_size': dialog.indent_size
    }
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=4)
    except Exception as e:
        print(f"Could not save config to {config_path}: {e}")

    # ==========================================
    # 0.5 PRE-SCAN FOR SENSITIVE CSS
    # ==========================================
    whitespace_regex = re.compile(r'white-space\s*:\s*(pre|pre-wrap|pre-line|break-spaces)', re.IGNORECASE)
    found_sensitive_css = False

    # Check external stylesheets
    for file_id, href in bk.css_iter():
        css_data = bk.readfile(file_id)
        if css_data and whitespace_regex.search(css_data):
            found_sensitive_css = True
            break

    # Check HTML files for <style> blocks and inline style attributes
    if not found_sensitive_css:
        for file_id, href in bk.text_iter():
            html_data = bk.readfile(file_id)
            if html_data and whitespace_regex.search(html_data):
                found_sensitive_css = True
                break

    if found_sensitive_css:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Sensitive CSS Detected")
        msg_box.setText(
            "Sprucer found CSS rules (like 'pre-wrap' or 'pre-line') that rely on literal spaces and line breaks.")
        msg_box.setInformativeText(
            "Because Sprucer normalizes HTML spacing, it may alter the intended formatting of the elements using these rules.\n\nDo you wish to proceed with formatting?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        # Abort if the user selects No
        if msg_box.exec() == QMessageBox.StandardButton.No:
            return 0

    # ==========================================
    # 1. THE EXHAUSTIVE W3C & XHTML 1.1 LEXICON
    # ==========================================
    skeleton_tags = {
        'html', 'head', 'body', 'div', 'section', 'article', 'aside', 'nav',
        'header', 'footer', 'main', 'figure', 'figcaption', 'table', 'thead',
        'tbody', 'tfoot', 'tr', 'ul', 'ol', 'dl', 'style', 'script', 'noscript',
        'fieldset', 'form', 'details', 'summary', 'dialog', 'menu', 'colgroup',
        'center', 'dir', 'frameset', 'noframes', 'blockquote'
    }

    prose_tags = {
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li',
        'th', 'td', 'title', 'dt', 'dd', 'address', 'pre', 'caption', 'legend'
    }

    void_tags = {
        'area', 'base', 'col', 'command', 'embed', 'hr',
        'input', 'keygen', 'link', 'meta', 'param', 'source', 'track',
        'basefont', 'frame', 'isindex'
    }

    inline_tags = {
        'a', 'em', 'strong', 'small', 's', 'cite', 'q', 'dfn', 'abbr',
        'time', 'code', 'var', 'samp', 'kbd', 'sub', 'sup', 'i', 'b',
        'u', 'mark', 'ruby', 'rt', 'rp', 'bdi', 'bdo', 'span', 'wbr', 'img',
        'font', 'tt', 'big', 'strike', 'acronym', 'applet', 'blink', 'marquee', 'nobr'
    }

    for file_id, href in bk.text_iter():
        raw_html = bk.readfile(file_id)
        if raw_html is None:
            continue

        raw_html = re.sub(r'&(?![A-Za-z0-9#]+;)', '&amp;', raw_html)
        prolog = []

        def pluck_prolog(match):
            prolog.append(match.group(0).strip())
            return ""

        body_payload = re.sub(r'<\?xml[^>]*>', pluck_prolog, raw_html, flags=re.IGNORECASE)
        body_payload = re.sub(r'<!DOCTYPE[^>]*>', pluck_prolog, body_payload, flags=re.IGNORECASE)

        # ==========================================
        # 3.5 PRESERVE SENSITIVE BLOCKS
        # ==========================================
        preserved_blocks = {}
        block_counter = 0

        def preserve_block(match):
            nonlocal block_counter
            tag = match.group(1).upper()
            placeholder = f"___SPRUCER_{tag}_{block_counter}___"
            preserved_blocks[placeholder] = match.group(0)
            block_counter += 1
            return placeholder

        preserve_pattern = r'<(pre|style|script)\b[^>]*>.*?</\1>'
        body_payload = re.sub(preserve_pattern, preserve_block, body_payload, flags=re.IGNORECASE | re.DOTALL)

        # 4. NORMALIZE SPACING (ASCII ONLY)
        flat = re.sub(r'\s+', ' ', body_payload, flags=re.ASCII).strip()

        # 5. INJECT STRUCTURAL NEWLINES (ASCII ONLY)
        skel_pattern = r'\s*(</?(' + '|'.join(skeleton_tags) + r')\b[^>]*>)\s*'
        flat = re.sub(skel_pattern, r'\n\1\n', flat, flags=re.IGNORECASE | re.ASCII)

        prose_open = r'\s*(<(' + '|'.join(prose_tags) + r')\b[^>]*>)\s*'
        flat = re.sub(prose_open, r'\n\1', flat, flags=re.IGNORECASE | re.ASCII)

        prose_close = r'\s*(</(' + '|'.join(prose_tags) + r')>)\s*'
        flat = re.sub(prose_close, r'\1\n', flat, flags=re.IGNORECASE | re.ASCII)

        void_pattern = r'\s*(<(' + '|'.join(void_tags) + r')\b[^>]*>)\s*'
        flat = re.sub(void_pattern, r'\n\1\n', flat, flags=re.IGNORECASE | re.ASCII)

        flat = re.sub(r'\s*(<br\b[^>]*>)\s*', r'\1\n', flat, flags=re.IGNORECASE | re.ASCII)

        flat = re.sub(r'\s*(___SPRUCER_(PRE|STYLE|SCRIPT)_\d+___)\s*', r'\n\1\n', flat, flags=re.ASCII)
        flat = re.sub(r'\n+', '\n', flat).strip()

        # ==========================================
        # 6. ENFORCE DYNAMIC INDENTATION
        # ==========================================
        final_lines = prolog.copy()
        indent = 0
        indent_tags = skeleton_tags - {'html'}

        for line in flat.splitlines():
            line = line.strip()
            if not line:
                continue

            if re.match(r'^</(' + '|'.join(indent_tags) + r')>', line, flags=re.IGNORECASE):
                indent = max(0, indent - 1)

            indent_str = (dialog.indent_char * dialog.indent_size) * indent
            final_lines.append(indent_str + line)

            if re.match(r'^<(' + '|'.join(indent_tags) + r')\b[^>]*(?<!/)>$', line, flags=re.IGNORECASE):
                indent += 1

        # ==========================================
        # 7. RESTORE PRESERVED BLOCKS & WRITE
        # ==========================================
        final_html = '\n'.join(final_lines) + '\n'

        for placeholder, original_content in preserved_blocks.items():
            match = re.search(r'^([ \t]*)' + re.escape(placeholder), final_html, flags=re.MULTILINE)
            indent_prefix = match.group(1) if match else ""

            if "PRE" in placeholder:
                final_html = final_html.replace(placeholder, original_content)
            else:
                tag_name = "style" if "STYLE" in placeholder else "script"
                padded_content = re.sub(r'\s*(</' + tag_name + r'>)$', r'\n' + indent_prefix + r'\1', original_content,
                                        flags=re.IGNORECASE | re.ASCII)
                final_html = final_html.replace(placeholder, padded_content)

        bk.writefile(file_id, final_html)

    return 0

def main():
    print("I reached main when I should not have\n")
    return -1

if __name__ == "__main__":
    sys.exit(main())