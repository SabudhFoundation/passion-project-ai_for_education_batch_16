import os
import random
from typing import List, Dict, Any, Literal

# Environment Variables
from dotenv import load_dotenv

# LangChain Core (Prompts, Messages, Output Parsers, Runnables)
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnableParallel, RunnableBranch, RunnableLambda
from langchain_core.tools import Tool, tool

# Models (OpenAI)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Document Loaders
from langchain_community.document_loaders import TextLoader,PyPDFLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser

# Text Splitters
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)

# Vector Stores (ChromaDB)
from langchain_chroma import Chroma

# Tools & Utilities (Experimental - REPL)
from langchain_experimental.tools import PythonREPLTool
from langchain_experimental.utilities import PythonREPL
# Pydantic (Data Validation)
from pydantic import BaseModel, Field

# --- Initialize Environment ---
load_dotenv()


from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os 

# For plain text and code (.txt, .md)
from langchain_community.document_loaders import TextLoader

# For fast, text-based PDFs (.pdf)
from langchain_community.document_loaders import PyMuPDFLoader

# For scanned/image-heavy PDFs (OCR)
from langchain_community.document_loaders import UnstructuredPDFLoader

# For web links and URLs
from langchain_community.document_loaders import WebBaseLoader

from typing import Callable, Dict
from collections.abc import Callable
import asyncio
import re
from langchain_community.document_loaders import Docx2txtLoader, UnstructuredWordDocumentLoader
from pathlib import Path
import re
import tempfile
import requests
import asyncio
from urllib.parse import urlparse
from pathlib import Path
import re
import tempfile
import requests
import asyncio
from urllib.parse import urlparse
from pathlib import Path
from langchain_core.documents import Document
import sys


_LOADER_REGISTRY: Dict[str, Callable] = {}
    
def register_loader(input_type: str):
    """Decorator factory that registers a loader function under a given input type key.

    Args:
        input_type (str): The key to register the loader under (e.g., ``".pdf"``,
            ``".txt"``, ``"url"``). Used to look up the correct loader at runtime
            inside ``_LOADER_REGISTRY``.

    Returns:
        Callable: A decorator that inserts the wrapped function into
        ``_LOADER_REGISTRY`` keyed by ``input_type`` and returns it unchanged.
    """
    def decorator(func: Callable):
        _LOADER_REGISTRY[input_type] = func
        return func
    return decorator


@register_loader(".txt")
async def loader_load_text(file_path: str):
    """Loads a plain text file using LangChain's ``TextLoader``.

    Args:
        file_path (str): Absolute or relative path to the ``.txt`` file on disk.

    Returns:
        list[Document]: A list of LangChain ``Document`` objects containing the
        file's content and basic metadata (e.g., ``source``).
    """
    loader = TextLoader(file_path)
    return await loader.aload()


@register_loader(".md")
async def loader_load_markdown(file_path: str):
    """Loads a Markdown file using LangChain's ``TextLoader``.

    Markdown is treated as plain text — no parsing of headers or code blocks
    is performed at load time.

    Args:
        file_path (str): Absolute or relative path to the ``.md`` file on disk.

    Returns:
        list[Document]: A list of LangChain ``Document`` objects containing the
        raw Markdown content and basic metadata (e.g., ``source``).
    """
    loader = TextLoader(file_path)
    return await loader.aload()


# --- PDFs (Dual Loaders for the Union) ---

@register_loader("pdf_primary")
async def loader_load_pdf_fast(file_path: str):
    """Primary PDF loader using ``PyMuPDFLoader`` for high-accuracy text extraction.

    Preferred for text-based PDFs where layout and formatting fidelity matter.
    Intended to run concurrently with ``loader_load_pdf_fallback``; results from
    both should be unioned downstream for maximum text coverage.

    Args:
        file_path (str): Absolute or relative path to the ``.pdf`` file on disk.

    Returns:
        list[Document]: A list of LangChain ``Document`` objects, one per page,
        with page text and PyMuPDF-sourced metadata.
    """
    loader = PyMuPDFLoader(file_path)
    return await loader.aload()


@register_loader("pdf_secondary")
async def loader_load_pdf_fallback(file_path: str):
    """Secondary PDF loader using ``PyPDFLoader`` as a fallback and complement.

    Captures text flows that ``PyMuPDFLoader`` may miss (e.g., certain column
    layouts or embedded fonts). Intended to run concurrently with
    ``loader_load_pdf_fast`` via ``asyncio.gather``; results should be unioned
    downstream.

    Args:
        file_path (str): Absolute or relative path to the ``.pdf`` file on disk.

    Returns:
        list[Document]: A list of LangChain ``Document`` objects, one per page,
        with page text and PyPDF-sourced metadata.
    """
    loader = PyPDFLoader(file_path)
    return await loader.aload()


# --- WORD DOCUMENTS ---

@register_loader(".docx")
async def load_word_docx(file_path: str):
    """Loads a modern Microsoft Word file (``.docx``) using ``Docx2txtLoader``.

    Fast and lightweight — suitable for ``.docx`` files produced by Word 2007
    and later. Does not handle the legacy ``.doc`` binary format.

    Args:
        file_path (str): Absolute or relative path to the ``.docx`` file on disk.

    Returns:
        list[Document]: A list of LangChain ``Document`` objects containing the
        extracted plain text and basic metadata.
    """
    loader = Docx2txtLoader(file_path)
    return await loader.aload()


@register_loader(".doc")
async def load_word_doc(file_path: str):
    """Loads a legacy Microsoft Word file (``.doc``) using ``UnstructuredWordDocumentLoader``.

    Uses the ``unstructured`` library under the hood to handle the older binary
    ``.doc`` format that ``Docx2txtLoader`` cannot read.

    Args:
        file_path (str): Absolute or relative path to the ``.doc`` file on disk.

    Returns:
        list[Document]: A list of LangChain ``Document`` objects containing the
        extracted text and metadata provided by the unstructured parser.
    """
    loader = UnstructuredWordDocumentLoader(file_path)
    return await loader.aload()


# --- WEB LINKS ---

@register_loader("url")
async def load_web_link(link: str):
    """Scrapes and loads visible text content from a standard HTML web page.

    Uses LangChain's ``WebBaseLoader``, which fetches the page and strips HTML
    tags to return plain text. Not suitable for JavaScript-rendered pages or
    URLs that point directly to downloadable files.

    Args:
        link (str): A fully-qualified HTTP/HTTPS URL
            (e.g., ``"https://example.com/article"``).

    Returns:
        list[Document]: A list of LangChain ``Document`` objects containing the
        scraped page text and URL metadata.
    """

    loader = WebBaseLoader(link)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, loader.load)


async def process_document(path_or_link: str):
    """Routes a file path, URL, or raw pasted text to the correct loader and returns Documents.

    Handles five cases in order:

    1. **URL pointing to a downloadable file** (``.pdf``, ``.docx``, ``.doc``,
       ``.txt``, ``.md``) — downloads content into a temp file and re-routes to
       the matching local loader.
    2. **URL pointing to a web page** (no recognised file extension) — delegates
       directly to ``load_web_link``.
    3. **Raw pasted text** (not a URL and no matching file on disk) — wraps the
       string directly into a ``Document`` object with ``source: user_pasted_text``.
    4. **Local PDF** — runs ``pdf_primary`` and ``pdf_secondary`` concurrently via
       ``asyncio.gather`` and returns both result sets for downstream unioning.
    5. **Local file** (``.docx``, ``.doc``, ``.txt``, ``.md``) — routes to the
       single registered loader for that extension.

    Args:
        path_or_link (str): A local filesystem path (e.g., ``"./resume.pdf"``),
            a fully-qualified HTTP/HTTPS URL, or a raw string of pasted text.

    Returns:
        dict[str, list[Document]]: A dictionary whose shape depends on the input:

            - ``{"standard": [...]}`` — for web pages, Word docs, text files, and
              raw pasted text.
            - ``{"primary_docs": [...], "secondary_docs": [...]}`` — for PDFs,
              containing results from both loaders ready for unioning.

    Raises:
        ValueError: If the file extension or input type has no registered loader.
        requests.HTTPError: If a remote file download returns a non-2xx HTTP status.
    """
    # --- 0. CONVERT GOOGLE DRIVE SHARE LINKS TO DIRECT DOWNLOAD ---
    if "drive.google.com/file/d/" in path_or_link:
       file_id = path_or_link.split("/file/d/")[1].split("/")[0]
       path_or_link = f"https://drive.google.com/uc?export=download&id={file_id}"
       print("Google Drive link detected, converting to direct download and then we will proceed ")
    
    response = requests.get(path_or_link)
    response.raise_for_status()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(response.content)
    temp_file.close()
    path_or_link = temp_file.name
    
    is_url = re.match(r'^https?:\/\/', path_or_link)
    working_path_for_file = path_or_link 
    
    #handle the url and download the dierect url file 
    if is_url:
        parsed_url = urlparse(path_or_link)
        url_ext = Path(parsed_url.path).suffix.lower()
        
        # If the link points directly to a file (like .pdf or .docx)
        if url_ext in [".pdf", ".docx", ".doc", ".txt", ".md"]:
            print(f"Downloading temporary file for: {url_ext}")
            
            response = requests.get(path_or_link)
            response.raise_for_status() 
            
            # Save it temporarily so our local loaders can read it and dont use temp.txt
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=url_ext)
            temp_file.write(response.content)
            temp_file.close() 
            
            working_path_for_file = temp_file.name
            
        else:
            # If it has no file extension, treat it as a standard web page
            loader_class = _LOADER_REGISTRY.get("url")
            docs = await loader_class(path_or_link)
            return {"standard": docs}

    else:
        # --- 2. HANDLE RAW PASTED TEXT ---
        
        
        # If it is not a URL and the file does not exist on your computer, 
        # we assume the user just pasted a paragraph of text directly and we will make document objects out of it .
        if not os.path.exists(working_path_for_file):
            print("Raw text and it will be converted to doc object")
            raw_doc = Document(
                page_content=working_path_for_file, 
                metadata={"source": "user_pasted_text"}
            )
            return {"standard": [raw_doc]}

    # --- 3. EXTRACT THE EXTENSION FOR LOCAL ROUTING ---
    file_extension = Path(working_path_for_file).suffix.lower()

    # --- 4. DUAL-LOADER FOR PDFs (Returns both for your custom union) ---
    if file_extension == ".pdf":
        loader1 = _LOADER_REGISTRY["pdf_primary"](working_path_for_file)   
        loader2 = _LOADER_REGISTRY["pdf_secondary"](working_path_for_file) 
        
        # Run both at the exact same time
        docs1, docs2 = await asyncio.gather(loader1, loader2)
        
        return {
            "primary_docs": docs1, 
            "secondary_docs": docs2
        }
        
    # --- 5. STANDARD SINGLE LOADERS (.docx, .doc, .txt, .md) ---
    if file_extension in [".docx", ".doc", ".txt", ".md"]:
        loader_class = _LOADER_REGISTRY.get(file_extension)
        if not loader_class:
             raise ValueError(f"Loader not found in registry for: {file_extension}")
             
        docs = await loader_class(working_path_for_file)
        return {"standard": docs}

    raise ValueError(f"Unsupported input type: {file_extension}")


def extract_words_from_docs(docs) -> list:
    """Extracts all words from a list of LangChain ``Document`` objects into a flat list.

    Joins the ``page_content`` of every document with a space (so page boundaries
    don't cause words to merge), strips commas so punctuation doesn't stick to
    adjacent words, then splits on whitespace.

    Args:
        docs (list[Document]): A list of LangChain ``Document`` objects as returned
            by any of the registered loader functions.

    Returns:
        list[str]: A flat list of individual word strings extracted from all documents.
    """
    # 1. Loop through the documents and join their text together
    # We use a space to join so the end of page 1 doesn't merge with page 2
    full_text = " ".join([doc.page_content for doc in docs])
    
    # 2. Replace commas with spaces so they don't stick to your words
    full_text = full_text.replace(",", " ")
    
    # 3. .split() automatically breaks it into words by any whitespace
    word_list = full_text.split()
    
    return word_list


def perform_final_union(processing_result: dict) -> str:
    """Merges loader output into a single deduplicated string of words.

    Handles both result shapes returned by ``process_document``:

    - **PDF (dual-loader)** — extracts words from both ``primary_docs`` and
      ``secondary_docs``, concatenates them, and removes duplicates while
      preserving the original order (ordered union).
    - **Standard (single loader)** — extracts words from ``standard`` docs and
      joins them as-is.

    Args:
        processing_result (dict[str, list[Document]]): The dictionary returned by
            ``process_document``. Expected keys are either
            ``{"primary_docs", "secondary_docs"}`` for PDFs or ``{"standard"}``
            for all other input types.

    Returns:
        str: A single whitespace-separated string of words. Returns an empty
        string if ``processing_result`` contains neither expected key.
    """
    # --- SCENARIO 1: It's a PDF (Dual Loaders) ---
    if "primary_docs" in processing_result:
        words1 = extract_words_from_docs(processing_result["primary_docs"])
        words2 = extract_words_from_docs(processing_result["secondary_docs"])
        
        # Ordered Union: Combine lists, remove duplicates, keep order
        unionated_words = list(dict.fromkeys(words1 + words2))
        
        # Turn it back into a single string
        return " ".join(unionated_words)
        
    # --- SCENARIO 2: Standard Single Loader ---
    elif "standard" in processing_result:
        words = extract_words_from_docs(processing_result["standard"])
        return " ".join(words)
        
    return ""


async def main():
    """Entry point — prompts for input, processes the document, and saves output to ``sample.txt``.

    Calls ``process_document`` with the user-supplied path, URL, or raw text,
    runs the result through ``perform_final_union``, and writes the final merged
    string to ``sample.txt`` in the current working directory.

    Raises:
        Exception: Any exception raised by ``process_document`` or file I/O is
        caught and printed; the program exits cleanly without re-raising.
    """
    # Prompt the user for a dynamic path or link
    user_input = input("Enter your link or path here: ")
    
    try:
        # 1. Fetch the document objects using the appropriate loader
        document_objects_loaders = await process_document(user_input)
        
        # 2. Perform the ordered union to get the final text
        finaltext = perform_final_union(document_objects_loaders)
        
        # 3. Save the results to sample.txt
        with open("sample.txt", "w", encoding="utf-8") as st:
            st.write(finaltext)
            
        print("Success: Output saved to sample.txt")
        
    except Exception as e:
        print(f"Error processing document: {e}")

if __name__ == "__main__":
    asyncio.run(main())
