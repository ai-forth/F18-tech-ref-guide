#!/usr/bin/env python3
"""Create a clean, conservatively copy-edited source edition of Moore's book."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PDF = ROOT / "archive" / "moore-book-original.pdf"
OUTPUT = ROOT / "manuscripts" / "programming-a-problem-oriented-language.md"

CHAPTERS = {
    "1. Introduction", "2. Programs without input", "3. Programs with input",
    "4. Programs that grow", "5. Programs with memory", "6. Programs with output",
    "7. Programs that share", "8. Programs that think", "9. Programs that bootstrap",
}
SUBHEADINGS = {
    "1.1 The Basic Principle", "1.2 Preview", "2.1 Choosing a language",
    "2.2 Choosing a computer", "2.3 Arrangement and formatting", "2.4 Mnemonics",
    "2.5 Routines and subroutines", "3.1 Nouns and verbs", "3.2 Control loop",
    "3.3 Word subroutine", "3.4 Decimal conversion", "3.5 Stacks", "3.6 Dictionary",
    "3.7 Control language, example", "4.1 Adding dictionary entries",
    "4.2 Deleting entries", "4.3 Operations", "4.4 Definition entries",
    "4.5 Code entries", "5.1 Organization of disk", "5.2 Text on disk",
    "6.1 Output routines", "6.2 Acknowledgement", "6.3 Character strings",
    "6.4 Field entries", "7.1 User control", "7.2 Queing", "7.3 Private dictionaries",
    "7.4 Disk buffers", "7.5 User swapping", "8.1 Word dissection",
    "8.2 Level definitions", "8.3 Infinite dictionary", "8.4 Infinite memory",
    "9.1 Getting started", "9.2 The roots", "9.3 The branches",
}

CORRECTIONS = {
    "Problem-Oriented-Language": "Problem-Oriented Language",
    "problem-oriented-language": "problem-oriented language",
    "ORIENTEDLANGUAGE": "ORIENTED LANGUAGE", "a least": "at least",
    "accomodated": "accommodated", "acess": "access", "adddress": "address",
    "aditive": "additive", "advangage": "advantage", "allright": "all right",
    "andd": "and", "apparant": "apparent", "availabe": "available",
    "bacause": "because", "betwen": "between", "brusk": "brusque",
    "buffeer": "buffer", "capabililties": "capabilities", "catagorize": "categorize",
    "charactere": "character", "competely": "completely", "consistant": "consistent",
    "consistantly": "consistently", "constsitute": "constitute",
    "conventionsl": "conventional", "defintion": "definition", "dfferent": "different",
    "dicussed": "discussed", "diffcult": "difficult", "dispair": "despair",
    "evereything": "everything", "everytime": "every time", "expecially": "especially",
    "explicitely": "explicitly", "extrememly": "extremely", "goiong": "going",
    "grammer": "grammar", "grammers": "grammars", "guaranted": "guaranteed",
    "heirarchies": "hierarchies", "heirarchy": "hierarchy",
    "inadvertant": "inadvertent", "incidently": "incidentally",
    "inforrmation": "information", "instructons": "instructions",
    "langage": "language", "millenium": "millennium", "Moreovere": "Moreover",
    "moreovere": "moreover", "multipled": "multiplied", "noticable": "noticeable",
    "occassionally": "occasionally", "occassions": "occasions",
    "occassion": "occasion", "occuppied": "occupied", "onorous": "onerous",
    "preceeding": "preceding", "preceeds": "precedes", "probablity": "probability",
    "prodigous": "prodigious", "rathere": "rather", "religously": "religiously",
    "thie": "this", "unduely": "unduly", "veery": "very", "wil": "will",
    "youself": "yourself", "Your're": "You're", "your realize": "you realize",
    "can not even": "cannot even", "the the": "the", "longer that": "longer than",
    "Firsts,": "First,", "an a-typical": "an atypical", "Queing": "Queuing",
    "in order to to intelligible": "in order to be intelligible",
    "are a class of extensions": "is a class of extensions",
    "but the increase the capability": "but they increase the capability",
    "COBOL is great a processing": "COBOL is great at processing",
    "ALGOL is great a providing": "ALGOL is great at providing",
    "branch. you modify": "branch. You modify",
    "machine- independence": "machine-independence",
    "a enormous": "an enormous",
}

FRONT_MATTER = r"""---
title: "Programming a Problem-Oriented Language"
author: "Charles H. Moore"
publisher: "Cartheur Research"
date: "Original manuscript: c. June 1970 · Cartheur Research edition: 2026"
lang: en-US
toc-depth: 2
header-includes:
  - |
    \renewcommand{\maketitle}{}
---

\thispagestyle{empty}
\vspace*{\fill}
\begin{center}
{\Huge\bfseries PROGRAMMING A PROBLEM-ORIENTED LANGUAGE\par}
\vspace{1.5cm}
{\Large Charles H. Moore\par}
\vspace{1.2cm}
\vspace{2.8cm}
{\Large CARTHEUR RESEARCH\par}
\vspace{0.4cm}
{\normalsize 2026\par}
\end{center}
\vspace*{\fill}
\newpage

\thispagestyle{empty}
© Charles H. Moore, original manuscript c. 1970.

This Cartheur Research edition is prepared from Charles H. Moore’s later web transcription of the manuscript. It corrects clear transcription and typographic errors, regularizes headings and punctuation, and improves reading typography. Original technical examples, terminology, and the author’s period voice have been retained.

Published by Cartheur Research · 2026
\newpage

# Editorial Note

Charles H. Moore described this work as an unpublished book written just after the first versions of Forth. In a 2011 web transcription, he retained much of the original language and noted that some remaining typographical errors were modern. This edition keeps the historical argument intact while making the manuscript more legible as a book.

The editorial policy is deliberately conservative: obvious transcription errors are corrected; headings, punctuation, and paragraph flow are regularized; and historical terminology and technical examples are preserved. Editorial changes do not alter the technical claims or arguments of the original.

\newpage
\tableofcontents
\newpage
"""


def correct(text: str) -> str:
    for original, replacement in CORRECTIONS.items():
        text = re.sub(rf"\b{re.escape(original)}\b", replacement, text)
    return text


def main() -> None:
    raw = subprocess.check_output(
        ["pdftotext", "-layout", str(SOURCE_PDF), "-"], text=True
    )
    raw = raw.split("Dates\n", 1)[1].replace("\f", "\n")
    lines = [line.strip() for line in raw.splitlines()]
    output, paragraph = [], []

    def flush() -> None:
        if paragraph:
            output.append(correct(" ".join(paragraph)))
            paragraph.clear()

    for line in lines:
        if not line:
            flush()
        elif line in CHAPTERS or line in SUBHEADINGS:
            flush()
            output.append(("#" if line in CHAPTERS else "##") + " " + correct(line))
        else:
            paragraph.append(line)
    flush()
    OUTPUT.write_text(FRONT_MATTER + "\n\n".join(output) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
