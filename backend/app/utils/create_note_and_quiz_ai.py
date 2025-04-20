import re
import pprint
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
# from vars import CHROMA_COLLECTION_NAME, CHROMA_DB_PATH, OLLAMA_EMBED_MODEL, MODEL_NAME
import asyncio
from pathlib import Path
from .ingest import list_of_ingested_files

load_dotenv()

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
# --- Configuration ---
# Embedding model configuration (ensure consistency with main.py)
OLLAMA_EMBED_MODEL = "nomic-embed-text"
# Path to the directory containing PDFs to ingest
# Ensure this 'uploads' directory exists relative to where you run this script
DATA_FOLDER = os.path.join(os.getcwd(), "uploads")
# Text splitting parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 50
# Directory to persist Chroma DB (ensure consistency with main.py)
CHROMA_DB_PATH = "/home/aishik/Documents/Programming/Hackathons/Hack4Bengal2025/backend/db/chroma_langchain_db"
# Collection name within Chroma DB (ensure consistency with main.py)
CHROMA_COLLECTION_NAME = "documents"
# Interval to check for new files (in seconds)
CHECK_INTERVAL = 10

CATEGORIES_LIST = ["AI", "HealthCare", "Life",
                   "Travel", "Academics", "Computer Vision", "Gym"]


class Categories(BaseModel):
    category: List[str] = Field(
        description="List of category names assigned to the prompt.")
    created: bool = Field(
        description="True if a new category was created, False otherwise.")


class QuizQuestion(BaseModel):
    question: str = Field(description="The question for the quiz.")
    options: List[str] | None = Field(
        description="List of options for the question.")
    answer: str = Field(description="The correct answer to the question.")


class Quiz(BaseModel):
    questions: List[QuizQuestion] = Field(
        description="List of quiz questions.")


parser_categorizer = JsonOutputParser(pydantic_object=Categories)
parser_quiz = JsonOutputParser(pydantic_object=Quiz)
parser_writer = StrOutputParser()

try:
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)
except Exception as e:
    print(f"Error initializing OllamaEmbeddings: {e}")
    print(
        f"Ensure Ollama is running and the model '{OLLAMA_EMBED_MODEL}' is available.")
    exit()

try:
    vector_store = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH,
    )
    # METADATA FILTERING
    filter_dict = {"name": {"$in": list_of_ingested_files}}
    chroma_retriever = vector_store.as_retriever(
        search_kwargs={"k": 10})
except Exception as e:
    print(f"Error initializing Chroma DB from {CHROMA_DB_PATH}: {e}")
    print("Ensure the Chroma DB directory exists and is accessible.")
    exit()

try:
    tavily_retriever = TavilySearchAPIRetriever(k=3)
except Exception as e:
    print(f"Error initializing TavilySearchAPIRetriever: {e}")
    print("Please ensure the TAVILY_API_KEY environment variable is set correctly.")
    exit()

template_categorizer = """
You are an expert categorization assistant that intelligently classifies user prompts into meaningful categories.
You have access to these existing categories: {categories}.
Your task is to analyze the user prompt and assign it to the most relevant categories, creating new ones when needed.

Guidelines for categorization:
1. For existing categories:
   - Use an existing category if it precisely matches the prompt's main topic
   - Consider using multiple existing categories if the prompt spans multiple domains
   - Evaluate category relevance based on semantic meaning, not just keyword matching

2. For new categories:
   - Create a new category (1-2 words) when the prompt introduces a distinct topic
   - Make new categories specific yet broad enough for future use
   - Use clear, descriptive terms that reflect the core concept
   - Consider hierarchical relationships (e.g., "Machine Learning" could be under "Technology")

3. For hybrid cases:
   - Include both existing and new categories when the prompt has both general and specific aspects
   - Ensure the new category adds meaningful specificity
   - Maintain logical relationships between categories

4. Category quality:
   - Ensure categories are meaningful and reusable
   - Avoid overly specific or temporary categories
   - Use consistent naming conventions
   - Consider future categorization needs

User Prompt: {user_prompt}
{format_instructions}
Return *only* the JSON object {{"category": ["category1", "category2"], "created": true/false}}. Do not add any introductory text or explanations.
"""

template_writer = """
You are a note-taking assistant that creates detailed notes based on user prompts, using provided context from web searches and local documents.
Use the context below to gather detailed information and create a comprehensive note with the following structure:

1.  **Title:** Generate a title for the note based on the user prompt.
2.  **Introduction:** Set the context based on the user prompt.
3.  **Main Sections (3-5):** Divide the note into key aspects of the topic using clear subheadings. Synthesize information from *both* web search and local document context where applicable.
4.  **Details:** Within each section, provide detailed explanations, facts, and examples drawing from the provided context. Ensure accuracy.
5.  **Data/Analysis (if applicable):** Include relevant data or statistics from the context if the prompt asks for a report/analysis.
6.  **Conclusion:** Summarize the main takeaways derived from the combined context.
7.  **References (Optional):** Briefly mention that the information was gathered from web search results and local documents if appropriate.

NOTE : The note should be of atleast 700 words. This rule should be strictly maintained.

**Context from Web Search & Local Documents:**
{context}

**User Prompt:**
{user_prompt}

Begin crafting the detailed note based *only* on the provided context and user prompt:
"""
template_quiz = """

You are an expert quiz generator AI. Your task is to create a comprehensive quiz based on the user's request and the context provided below.


**Instructions:**

1.  **Analyze the User Request:**
    *   **Number of Questions:** Check if the user specified the total number of questions. If yes, generate exactly that number. If not, generate a default of 25 questions.
    *   **Question Types:** Check if the user specified the types of questions (e.g., Multiple Choice Question (MCQ), Multiple Select Question (MSQ), Short Answer Question (SAQ), Long Answer Question (LAQ)) and the count for each type. If yes, follow those specifications precisely. If no specific types or counts are mentioned, generate the quiz with the following default distribution:
        *   10 Multiple Choice Questions (MCQs) - Provide 4 options.
        *   5 Multiple Select Questions (MSQs) - Provide 4-6 options, where multiple answers can be correct.
        *   5 Short Answer Questions (SAQs) - Require a brief, concise answer.
        *   5 Long Answer Questions (LAQs) - Require a more detailed, explanatory answer.
    *   **Topic:** Generate questions strictly related to the topic mentioned in the user request, using the provided context.

2.  **Generate Questions:**
    *   Create questions that accurately reflect the information in the context.
    *   For MCQs and MSQs, ensure the options are plausible but only the designated answer(s) are correct based on the context. The `options` field should be a list of strings.
    *   For SAQs and LAQs, formulate questions that require understanding and synthesis of the context. The `options` field should be `null`.

3.  **Generate Answers:**
    *   Provide the correct answer for every question in the `answer` field.
    *   For MCQs and SAQs, the answer should be a single, precise string.
    *   For MSQs, the answer should be a string containing the correct options, often separated by commas or clearly listed.
    *   For LAQs, the answer should be a comprehensive explanation derived from the context.

4.  **Output Format:**
    *   Return the generated quiz ONLY as a JSON object.
    *   The JSON object must strictly adhere to the following structure, matching the `Quiz` and `QuizQuestion` Pydantic models:
      ```json
      {{
        "questions": [
          {{
            "question": "The text of the question",
            "options": ["Option A", "Option B", "Option C", "Option D"], // List[str] for MCQ/MSQ, null for SAQ/LAQ
            "answer": "The correct answer string" // String for all types
          }},
          // ... more questions
        ]
      }}
      ```
    *   Ensure the `options` field is a list of strings for MCQs/MSQs and `null` for SAQs/LAQs. The `answer` field must always be a string.

    **Context from Web Search & Local Documents:**
{context}

**User Prompt:**
{user_prompt}

Begin crafting the quiz based *only* on the provided context and user prompt:
"""

prompt_categorizer = PromptTemplate(
    template=template_categorizer,
    input_variables=["categories", "user_prompt"],
    partial_variables={
        "format_instructions": parser_categorizer.get_format_instructions()},
)

prompt_writer = ChatPromptTemplate.from_template(template_writer)
prompt_quiz = ChatPromptTemplate.from_template(template_quiz)
try:
    client = ChatGroq(model=MODEL_NAME, temperature=0.7)
except Exception as e:
    print(f"Error initializing ChatGroq: {e}")
    print("Please ensure the GROQ_API_KEY environment variable is set correctly.")
    exit()

chain_categorizer = prompt_categorizer | client | parser_categorizer


def extract_title(text):
    start_tag = "**Title:**"
    end_tag = "**Introduction:**"
    start_idx = text.find(start_tag) + len(start_tag)
    end_idx = text.find(end_tag)
    if start_idx == -1 or end_idx == -1:
        return None, None
    title = text[start_idx:end_idx].strip()
    content = text[end_idx + len(end_tag):].strip()
    return title, content


def format_docs(docs: List[Any]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def combine_contexts(retrieved_docs: Dict[str, List[Any]]) -> str:
    formatted_tavily = format_docs(retrieved_docs.get('tavily', []))
    print(f"\n\n\n\nRETRIEVED TAVILY DOCS : {formatted_tavily} \n\n\n\n")
    formatted_chroma = format_docs(retrieved_docs.get('chroma', []))
    print(f"\n\n\n\nRETRIEVED CHROMA DOCS : {formatted_chroma} \n\n\n\n")

    return f"--- Context from Web Search ---\n{formatted_tavily}\n\n--- Context from Local Documents ---\n{formatted_chroma}"


retrieval_chain_search = RunnableParallel(
    tavily=tavily_retriever,
    # chroma=chroma_retriever
) | RunnableLambda(combine_contexts)

retrieval_chain_rag = RunnableParallel(
    chroma=chroma_retriever
) | RunnableLambda(combine_contexts)


retrieval_chain_quiz_rag = RunnableParallel(
    chroma=chroma_retriever
) | RunnableLambda(combine_contexts)

retrieval_chain_quiz_search = RunnableParallel(
    tavily=tavily_retriever,

) | RunnableLambda(combine_contexts)

chain_writer_search = (
    RunnablePassthrough.assign(
        context=RunnableLambda(
            lambda x: x['user_prompt']) | retrieval_chain_search
    )
    | prompt_writer
    | client
    | parser_writer
)

chain_writer_rag = (
    RunnablePassthrough.assign(
        context=RunnableLambda(
            lambda x: x['user_prompt']) | retrieval_chain_rag
    )
    | prompt_writer
    | client
    | parser_writer
)


chain_quiz_rag = (
    RunnablePassthrough.assign(
        context=RunnableLambda(
            lambda x: x['user_prompt']) | retrieval_chain_quiz_rag
    )
    | prompt_quiz
    | client
    | parser_quiz
)

chain_quiz_search = (
    RunnablePassthrough.assign(
        context=RunnableLambda(
            lambda x: x['user_prompt']) | retrieval_chain_quiz_search
    )
    | prompt_quiz
    | client
    | parser_quiz
)

def create_note(all_categories, user_prompt: str, rag_enabled: bool = False) -> Dict[str, Any]:

    try:
        print(f"Categorizing prompt: '{user_prompt}'")
        categorizer_result = chain_categorizer.invoke({
            "categories": ", ".join(all_categories),
            "user_prompt": user_prompt
        })

        print(
            f"\nGenerating note for prompt: '{user_prompt}' using Tavily search and Chroma DB...")
        print("-" * 20)
        if rag_enabled:
            writer_result = chain_writer_rag.invoke(
                {"user_prompt": user_prompt})
        else:
            writer_result = chain_writer_search.invoke(
                {"user_prompt": user_prompt})

        # Extract the title
        title, content = extract_title(writer_result)
        print(f"Title: {title}")
        print(f"Content: {content}")
        output_filename = "output.md"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(writer_result)
        print(f"Note saved to {output_filename}")

        return {"title": title, "note_content": content, "categories": categorizer_result}

    except Exception as e:
        print(f"\nAn error occurred during processing: {e}")
        if "TAVILY_API_KEY" in str(e):
            print(
                "Please ensure your TAVILY_API_KEY environment variable is set correctly.")
        return {"note_content": None, "categories": None, "error": str(e)}


def create_quiz(user_prompt_input: str, rag_enabled: bool = False) -> Dict[str, Any]:
    """
    HAVEN'T YET IMPLEMENTED RAG CHECK FOR QUIZ GENERATION
    """
    try:

        print(
            f"\nGenerating quiz for prompt: '{user_prompt_input}' using Tavily search and Chroma DB...")
        print("-" * 20)

        if rag_enabled:
            quiz_result = chain_quiz_rag.invoke({"user_prompt": user_prompt_input})
        else:
            quiz_result = chain_quiz_search.invoke({"user_prompt": user_prompt_input})

        return {"quiz_content": quiz_result}

    except Exception as e:
        print(f"\nAn error occurred during processing: {e}")
        if "TAVILY_API_KEY" in str(e):
            print(
                "Please ensure your TAVILY_API_KEY environment variable is set correctly.")
        # return {"note_content": None, "categories": None, "error": str(e)}


# if __name__ == "__main__":
#     USER_PROMPT_NOTE = "create a detailed report on the own planning of Harappan civilization"
#     USER_PROMPT_QUIZ = "create a quiz on perceptrons in Neural Networks"

    # result = create_quiz(USER_PROMPT_QUIZ, rag_enabled=False)
    # print(result)
    #     if result.get("categories"):
    #         print(f"Categories: {result['categories'].get('category', 'N/A')}")
    #         print(f"New Category Created: {result['categories'].get('created', 'N/A')}")
    #     print("---")
    #     print(result["note_content"])
    #     print("--- Note End ---")
    # elif result and result.get("error"):
    #     print(f"\nFailed to generate note due to error: {result['error']}")
    # else:
    #     print("\nFailed to generate note for unknown reasons.")

# Template for note generation
NOTE_TEMPLATE = """
You are an expert note-taking assistant. Your task is to create a comprehensive, well-structured note based on the user's request and any additional context provided.

If context is provided, make sure to incorporate relevant information from it into your note. If no context is provided, use your knowledge to create a detailed note on the topic.

Format your note with a clear title, organized sections with headings, and well-structured paragraphs. Use bullet points and numbered lists where appropriate.

USER PROMPT:
{user_prompt}

ADDITIONAL CONTEXT (IF ANY):
{context}

Your response should ONLY include the generated note with the following structure:
{format_instructions}
"""

# Define the output schema


# class NoteOutputParser(JsonOutputParser):
#     def parse(self, text: str) -> Dict[str, Any]:
#         try:
#             return super().parse(text)
#         except Exception as e:
#             # Fallback parsing if the output is not valid JSON
#             title_line = None
#             content_lines = []
#             in_content = False

#             for line in text.split("\n"):
#                 line = line.strip()
#                 if not title_line and line and not line.startswith("#"):
#                     title_line = line
#                 elif line.startswith("#") and not in_content:
#                     title_line = line.lstrip("#").strip()
#                 elif title_line and not in_content:
#                     in_content = True

#                 if in_content and line:
#                     content_lines.append(line)

#             return {
#                 "title": title_line or "Generated Note",
#                 "content": "\n".join(content_lines) or "No content generated."
#             }


# async def generate_content(
#     user_prompt: str,
#     rag_enabled: bool = False,
#     file_paths: Optional[List[str]] = None
# ) -> Dict[str, Any]:
#     """
#     Generate note content using AI, with optional RAG if files are provided.

#     Args:
#         user_prompt: The user's prompt for note generation
#         rag_enabled: Whether to use RAG
#         file_paths: List of file paths to use for RAG

#     Returns:
#         Dict containing title and content of the generated note
#     """
#     try:
#         # Set up the LLM
#         llm = ChatGroq(
#             model=MODEL_NAME,
#             temperature=0.5,
#         )

#         # Initialize parser with expected output format
#         output_format = """
#         {
#           "title": "The title of the note",
#           "content": "The detailed content of the note"
#         }
#         """
#         parser = NoteOutputParser()

#         # Define the prompt template
#         prompt = PromptTemplate(
#             template=NOTE_TEMPLATE,
#             input_variables=["user_prompt", "context"],
#             partial_variables={"format_instructions": output_format},
#         )

#         # Context to use in generation
#         context = ""

#         # If RAG is enabled, process files and retrieve relevant content
#         if rag_enabled and file_paths:
#             try:
#                 # Initialize embeddings
#                 embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)

#                 # Process files - for demonstration, we're just reading text content
#                 # In a real-world scenario, you would use proper document loaders
#                 file_contents = []
#                 for file_path in file_paths:
#                     path = Path(file_path)
#                     if path.exists():
#                         try:
#                             with open(path, "r", encoding="utf-8") as f:
#                                 file_contents.append(f.read())
#                         except UnicodeDecodeError:
#                             # If not readable as text, skip
#                             print(f"Could not read {file_path} as text")

#                 # For simplicity, just combine all file contents
#                 # In a production app, you would use proper RAG with vector embeddings
#                 context = "\n\n".join(file_contents)

#                 # Limit context length to avoid token limits
#                 if len(context) > 10000:
#                     context = context[:10000] + "...[content truncated]"

#             except Exception as e:
#                 print(f"Error in RAG processing: {e}")
#                 context = "Error processing the provided files."

#         # Generate note
#         chain = (
#             {"user_prompt": RunnableLambda(
#                 lambda x: x), "context": RunnableLambda(lambda x: context)}
#             | prompt
#             | llm
#             | parser
#         )

#         result = await asyncio.to_thread(chain.invoke, user_prompt)
#         return result

#     except Exception as e:
#         print(f"Error generating content: {e}")
#         return {
#             "title": "Error Generating Note",
#             "content": f"An error occurred while generating the note: {str(e)}"
#         }

# # Function to combine contexts


# def w(contexts: Dict[str, Any]) -> str:
#     """
#     Combine contexts from different sources into a single context string.
#     """
#     combined = []

#     # Add web search results if available
#     if "tavily" in contexts and contexts["tavily"]:
#         web_results = contexts["tavily"]
#         web_context = "Web Search Results:\n"

#         for i, result in enumerate(web_results, 1):
#             if isinstance(result, dict):
#                 title = result.get("title", "No Title")
#                 content = result.get("content", "No Content")
#                 web_context += f"Result {i}:\nTitle: {title}\nContent: {content}\n\n"
#             elif isinstance(result, str):
#                 web_context += f"Result {i}: {result}\n\n"

#         combined.append(web_context)

#     # Add document search results if available
#     if "chroma" in contexts and contexts["chroma"]:
#         doc_results = contexts["chroma"]
#         doc_context = "Document Search Results:\n"

#         for i, doc in enumerate(doc_results, 1):
#             doc_context += f"Document {i}:\n{doc.page_content}\n\n"

#         combined.append(doc_context)

#     return "\n".join(combined) if combined else "No relevant context found."

# # Function to format documents for output


# def format_docs(docs: List[Any]) -> str:
#     """
#     Format a list of documents into a single string.
#     """
#     if not docs:
#         return "No relevant documents found."

#     formatted = []
#     for i, doc in enumerate(docs, 1):
#         # Handle different document formats
#         if hasattr(doc, "page_content"):
#             formatted.append(f"Document {i}:\n{doc.page_content}")
#         elif isinstance(doc, dict) and "content" in doc:
#             formatted.append(f"Document {i}:\n{doc['content']}")
#         elif isinstance(doc, str):
#             formatted.append(f"Document {i}:\n{doc}")
#         else:
#             formatted.append(f"Document {i}: [Unknown format]")

#     return "\n\n".join(formatted)
