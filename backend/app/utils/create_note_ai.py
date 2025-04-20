"""
DO NOT USE THIS FILE.

USE create_note_and_quiz_ai.py instead.
"""

# Import necessary libraries
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field, Json 
from typing import List, Dict, Any
from vars import MODEL_NAME

load_dotenv()


CATEGORIES_LIST = ["AI", "HealthCare", "Life", "Travel", "Academics", "Computer Vision", "Gym"]

# User prompt
user_prompt = "create a detailed report on the impact of climate change on our planet"

# --- Pydantic Model for Categorizer (currently commented out) ---
class Categories(BaseModel):
    """Pydantic model to represent the categorized output."""
    category: List[str] = Field(description="List of category names assigned to the prompt.")
    created: bool = Field(description="True if a new category was created, False otherwise.")

# --- Output Parsers ---
parser_categorizer = JsonOutputParser(pydantic_object=Categories)
parser_writer = StrOutputParser()

# --- Retriever ---
# Initialize Tavily Search API Retriever
# Requires TAVILY_API_KEY environment variable to be set.
try:
    tavily_retriever = TavilySearchAPIRetriever(k=3) # Fetch top 3 results
except Exception as e:
    print(f"Error initializing TavilySearchAPIRetriever: {e}")
    print("Please ensure the TAVILY_API_KEY environment variable is set correctly.")
    exit()

# --- Prompt Templates ---

# Template for the categorizer (currently commented out)
template_categorizer = """
You are a helpful assistant that categorizes user prompts.
You have a list of predefined categories: {categories}.
Your task is to classify the user prompt below and assign it to one or more relevant categories from the list.
Rules:
1. If the prompt fits well into an existing category, use that category.
2. If the prompt doesn't fit any existing category well, create a *new*, suitable category name (1-2 words).
3. If the prompt fits an existing category broadly but could also have a more specific new category, include *both* the existing category and the new specific category.
4. Indicate whether a *new* category was created.
User Prompt: {user_prompt}
{format_instructions}
Return *only* the JSON object. Do not add any introductory text or explanations.
"""

# Template for the writer - **Updated to include context**
template_writer = """
You are a note-taking assistant that creates detailed notes based on user prompts, using provided context from web searches.
Use the context below to gather detailed information and create a comprehensive note with the following structure:

1.  **Introduction:** Set the context based on the user prompt.
2.  **Main Sections (3-5):** Divide the note into key aspects of the topic using clear subheadings. Use the provided context extensively.
3.  **Details:** Within each section, provide detailed explanations, facts, and examples from the context. Ensure accuracy.
4.  **Data/Analysis (if applicable):** Include relevant data or statistics from the context if the prompt asks for a report/analysis.
5.  **Conclusion:** Summarize the main takeaways from the context.
6.  **References (Optional):** Briefly mention that the information was gathered from web search results if appropriate.

NOTE : The note should be of atleast 700 words. This rule should be strictly maintained.

**Context from Web Search:**
{context}

**User Prompt:**
{user_prompt}

Begin crafting the detailed note based *only* on the provided context and user prompt:
"""

# Prompt Template Instances
prompt_categorizer = PromptTemplate(
    template=template_categorizer,
    input_variables=["categories", "user_prompt"],
    partial_variables={"format_instructions": parser_categorizer.get_format_instructions()},
)

# **Updated prompt_writer to accept 'context' and 'user_prompt'**
prompt_writer = ChatPromptTemplate.from_template(template_writer)

# --- LLM Client ---
# Initialize the ChatGroq client
# Requires GROQ_API_KEY environment variable.
try:
    # Using a generally available and capable model
    client = ChatGroq(model=MODEL_NAME, temperature=0.7)
except Exception as e:
    print(f"Error initializing ChatGroq: {e}")
    print("Please ensure the GROQ_API_KEY environment variable is set correctly.")
    exit()

# --- Chains ---

# Categorizer chain (currently commented out)
chain_categorizer = prompt_categorizer | client | parser_categorizer

# Helper function to format retrieved documents
def format_docs(docs: List[Any]) -> str:
    """Formats the retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

# Writer chain - **Corrected Structure**
# 1. Pass the input through using RunnablePassthrough.assign.
# 2. Assign "context": Run the retriever on the input ("user_prompt"), then format the docs.
# 3. The original input ("user_prompt") is passed along automatically by the passthrough.
# 4. Pipe the resulting dictionary {"context": ..., "user_prompt": ...} to the prompt template.
# 5. Pipe the formatted prompt to the LLM.
# 6. Pipe the LLM output to the string parser.
chain_writer = (
    RunnablePassthrough.assign(
        context=lambda x: format_docs(tavily_retriever.invoke(x["user_prompt"]))
    )
    | prompt_writer
    | client
    | parser_writer # Use the StrOutputParser instance
)


# --- Execution ---
def create_note(user_prompt) -> Dict[str,List[str]]:
    try:
        categorizer_result = chain_categorizer.invoke({
            "categories": ", ".join(CATEGORIES_LIST),
            "user_prompt": user_prompt
        })

        # --- Writer Execution ---
        print(f"\nGenerating note for prompt: '{user_prompt}' using Tavily search...")
        print("-" * 20)


        writer_result = chain_writer.invoke({"user_prompt": user_prompt})

        with open("output.md", 'w') as f:
            f.write(writer_result)
        return {"note_content" : writer_result, "categories" : categorizer_result}
    except Exception as e:
        print(f"\nAn error occurred during processing: {e}")
        if "TAVILY_API_KEY" in str(e):
            print("Please ensure your TAVILY_API_KEY environment variable is set correctly.")

result = create_note(user_prompt)

print(f"NOTE --{result["categories"]['category']}--\n\n\n{result["note_content"]}")