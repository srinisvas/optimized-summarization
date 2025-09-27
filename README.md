# LLM-Based Summarization for Technical Documents

## Motivation

LLM-based summarization increases productivity and enables people to understand the key insights from documents. Light-weight LLMs (sub-10B parameters) struggle with summarizing complex technical documents like research publications due to technical jargon, lengthy citations, and mathematical notations, often leading to hallucinations that reduce reliability and accuracy. Our aim is to make light-weight LLMs behave more like large-scale LLMs in summarization.

## Project Description

This project aims to design a summarization workflow tailored for small-scale LLMs to minimize hallucinations and maximize factual accuracy. The pipeline will include:

1. **Preprocessing**: Clean and segment full articles into sections, text normalization—removing references, citations, and formulas.
2. **Sparse Input Activation**: Perform salient sentence extraction and keyphrase extraction.
3. **Adaptive Prompt Optimization**: Apply multiple prompting strategies (instructional, few-shot, context-rich).
4. **Summarization**: Apply lightweight LLMs with self-check loops to refine outputs.
5. **Evaluation**: Benchmark results against outputs from large LLMs and manual evaluation.

---

For more details, see the source code and documentation in this repository.