#!/usr/bin/env python3
"""Setup knowledge base for the customer support system."""

import os
from pathlib import Path
import sys

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


def setup_knowledge_base():
    """Setup the knowledge base with sample documents."""

    # Create knowledge base directory
    kb_path = Path("./knowledge_base")
    kb_path.mkdir(exist_ok=True)

    print("🧠 Setting up knowledge base...")

    # Sample knowledge base documents
    documents = [
        Document(
            page_content="""
            Order Processing Information:
            - Orders are processed within 1-2 business days
            - Order numbers follow the format ORD followed by 6 digits
            - You can track your order using the order number
            - For order issues, please provide the order number
            """,
            metadata={"category": "order_processing", "source": "internal"},
        ),
        Document(
            page_content="""
            Technical Support:
            - Common issues include login problems, app crashes, and slow performance
            - Error code 500 indicates server issues
            - Error code 404 means the page was not found
            - For technical issues, try clearing cache and cookies first
            - If problems persist, contact technical support
            """,
            metadata={"category": "technical_support", "source": "internal"},
        ),
        Document(
            page_content="""
            Billing and Payments:
            - Payments are processed securely through our payment gateway
            - Refunds take 3-5 business days to process
            - You can view your billing history in your account
            - For billing questions, please provide your order number
            - We accept credit cards, PayPal, and bank transfers
            """,
            metadata={"category": "billing", "source": "internal"},
        ),
        Document(
            page_content="""
            Shipping Information:
            - Standard shipping takes 3-5 business days
            - Express shipping takes 1-2 business days
            - International shipping takes 7-14 business days
            - You can track your shipment using the tracking number
            - For shipping issues, please provide your order number
            """,
            metadata={"category": "shipping", "source": "internal"},
        ),
        Document(
            page_content="""
            Product Information:
            - All products come with a 30-day money-back guarantee
            - Product warranties vary by item
            - For product defects, please contact support with photos
            - Product returns must be in original packaging
            - Custom products may have different return policies
            """,
            metadata={"category": "products", "source": "internal"},
        ),
        Document(
            page_content="""
            Account Management:
            - You can update your account information anytime
            - Password reset is available through the login page
            - Two-factor authentication is recommended for security
            - Account deletion is permanent and cannot be undone
            - For account issues, please verify your identity
            """,
            metadata={"category": "account", "source": "internal"},
        ),
        Document(
            page_content="""
            General Support:
            - Our support team is available 24/7
            - Response time is typically within 2 hours
            - For urgent issues, mark your ticket as high priority
            - We support multiple languages
            - Live chat is available on our website
            """,
            metadata={"category": "general", "source": "internal"},
        ),
    ]

    # Initialize embeddings
    print("📚 Creating vector embeddings...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002", api_key=os.getenv("OPENAI_API_KEY")
    )

    # Create vector store
    vector_store = Chroma.from_documents(
        documents=documents, embedding=embeddings, persist_directory=str(kb_path)
    )

    # Persist the vector store
    vector_store.persist()

    print(f"✅ Knowledge base created successfully at {kb_path}")
    print(f"📊 Added {len(documents)} documents")
    print()
    print("Categories included:")
    for doc in documents:
        category = doc.metadata.get("category", "unknown")
        print(f"   • {category}")

    print()
    print("🎉 Knowledge base setup complete!")
    print("You can now start the customer support system.")


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    setup_knowledge_base()
