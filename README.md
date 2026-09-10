# AI Student Assistant

An AI-powered student assistant that uses Retrieval-Augmented Generation (RAG), FAISS, MCP, and an OpenAI language model to answer questions about student information and PDF documents.

## Project Overview

This project combines document-based question answering with a student database to create an AI assistant.

The system uses RAG to retrieve relevant information from a PDF document and FAISS for similarity search. MCP (Model Context Protocol) is used to connect the AI agent with a student database.

The application also includes input and output guardrails to prevent sensitive information from being handled and to provide a fallback when sufficient information is not available.

## Features

- PDF-based question answering using RAG
- FAISS vector database for document retrieval
- MCP integration for student database access
- AI agent for handling student-related queries
- Input guardrails for sensitive information
- Output validation
- Chat history
- Streamlit web interface

## Technologies Used

- Python
- LangChain
- LangGraph / LangChain Agents
- OpenAI
- FAISS
- MCP
- SQLite
- Streamlit
- PyPDF
- Python-dotenv

## Project Structure

```text
AI-Student-Assistant/
│
├── documents/
│   └── students.pdf
│
├── templates/
│
├── app.py
├── database.py
├── mcp_server.py
├── requirements.txt
├── README.md
└── .env.example

## RAG Workflow

```text
PDF Document
     ↓
PDF Loading
     ↓
Text Chunking
     ↓
OpenAI Embeddings
     ↓
FAISS Vector Database
     ↓
Similarity Search
     ↓
Relevant Context
     ↓
AI Agent
     ↓
Answer
