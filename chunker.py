"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`fallback_split` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `chunk_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _split_oversized(paragraph: str, max_chars: int) -> list[str]:
    """Break one paragraph that is longer than max_chars into smaller pieces.

    Tries line breaks first (a reply per line is common in threads), then
    sentence ends. A single sentence longer than max_chars is kept whole rather
    than cut mid-sentence.
    """
    units: list[str] = []
    for line in paragraph.split("\n"):
        line = line.strip()
        if not line:
            continue
        if len(line) <= max_chars:
            units.append(line)
        else:
            units.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", line) if s.strip())

    pieces: list[str] = []
    current = ""
    for unit in units:
        if current and len(current) + len(unit) + 1 > max_chars:
            pieces.append(current)
            current = unit
        else:
            current = f"{current}\n{unit}" if current else unit
    if current:
        pieces.append(current)
    return pieces


def chunk_documents(documents: list[Document]) -> list[Chunk]:
    """
    Paragraph-based chunker.

    For each document:
      1. Split the text on blank lines into paragraphs. A paragraph longer
         than MAX_CHARS is first broken at line breaks, then at sentence ends.
      2. Pack consecutive paragraphs into one chunk until adding the next
         one would push it past MAX_CHARS.
      3. If the final chunk is shorter than MIN_CHARS, merge it into the
         previous chunk instead of leaving a fragment.

    No overlap: chunks break only at paragraph, line or sentence boundaries.
    """
    MAX_CHARS = 1000  # close a chunk once adding another paragraph would pass this
    MIN_CHARS = 150   # a final chunk shorter than this is merged into the previous one

    chunks: list[Chunk] = []
    for doc in documents:
        paras: list[str] = []
        for p in doc.text.split("\n\n"):
            p = p.strip()
            if not p:
                continue
            paras.extend(_split_oversized(p, MAX_CHARS) if len(p) > MAX_CHARS else [p])

        pieces: list[str] = []
        current = ""
        for p in paras:
            if current and len(current) + len(p) + 2 > MAX_CHARS:
                pieces.append(current)
                current = p
            else:
                current = f"{current}\n\n{p}" if current else p
        if current:
            if pieces and len(current) < MIN_CHARS:
                pieces[-1] += "\n\n" + current
            else:
                pieces.append(current)

        for i, piece in enumerate(pieces):
            chunks.append(
                Chunk(
                    text=piece,
                    source=doc.source,
                    index=i,
                    produced_by="chunker.py::chunk_documents",
                )
            )

    return chunks


def chunk_documents_v2(documents: list[Document]) -> list[Chunk]:
    """
    Second chunking strategy, for the unit 2 before/after comparison.

    Smaller chunks (MAX_CHARS 500 vs 1000) with a one-paragraph overlap: when a
    chunk closes, its last paragraph is repeated at the start of the next one if
    it is short enough. Smaller chunks keep each one on a single point; the
    overlap keeps a thought that straddles a boundary whole in at least one
    chunk. Change the numbers to match the failure you diagnosed.

    Build it with:  python app.py --corpus advice_threads --variant v2 index
    """
    MAX_CHARS = 500      # smaller than chunk_documents, to keep chunks on one point
    OVERLAP_CHARS = 200  # repeat the previous chunk's last paragraph if it is this short or less

    chunks: list[Chunk] = []
    for doc in documents:
        paras: list[str] = []
        for p in doc.text.split("\n\n"):
            p = p.strip()
            if not p:
                continue
            paras.extend(_split_oversized(p, MAX_CHARS) if len(p) > MAX_CHARS else [p])

        pieces: list[str] = []
        current: list[str] = []
        for p in paras:
            if current and len("\n\n".join(current)) + len(p) + 2 > MAX_CHARS:
                pieces.append("\n\n".join(current))
                last = current[-1]
                keep = len(last) <= OVERLAP_CHARS and len(last) + len(p) + 2 <= MAX_CHARS
                current = [last] if keep else []
            current.append(p)
        if current:
            pieces.append("\n\n".join(current))

        for i, piece in enumerate(pieces):
            chunks.append(
                Chunk(
                    text=piece,
                    source=doc.source,
                    index=i,
                    produced_by="chunker.py::chunk_documents_v2",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = chunk_documents(load_documents())
    print(describe(chunks))