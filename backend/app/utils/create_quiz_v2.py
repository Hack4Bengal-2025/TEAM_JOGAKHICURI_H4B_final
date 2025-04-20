"""
DO NOT USE THIS FILE.

USE create_note_and_quiz_ai.py instead.
"""

import os
import json
from typing import List, Optional, Dict, Any, Type
import traceback

# --- CrewAI ---
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool  # Use BaseTool for custom tool definition
from crewai.llm import LLM
# --- LLM, Embeddings, VectorStore ---
from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.retrievers import BaseRetriever  # To type hint retriever

# --- Pydantic Models ---
# CrewAI often uses Pydantic v1 internally
from pydantic.v1 import BaseModel, Field

# --- Environment and Variables ---
from dotenv import load_dotenv
try:
    from vars import *  # Assumes CHROMA_DB_PATH, CHROMA_COLLECTION_NAME, MODEL_NAME are here
    # Ensure TAVILY_API_KEY is set
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
except ImportError:
    print("Warning: vars.py not found. Using environment variables or defaults.")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db_store")
    CHROMA_COLLECTION_NAME = os.getenv(
        "CHROMA_COLLECTION_NAME", "pdf_documents_collection")
    # Ensure GROQ_API_KEY is set
    MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama3-70b-8192")

load_dotenv()

# --- Pydantic Models for Structured Output (Same as before) ---


class QuizQuestion(BaseModel):
    """Represents a single question in the quiz."""
    question: str = Field(description="The text of the question.")
    options: Optional[List[str]] = Field(
        default=None,
        description="List of options for Multiple Choice (MCQ) or Multiple Select (MSQ) questions. Should be null for Short Answer (SAQ) and Long Answer (LAQ) questions."
    )
    answer: str = Field(
        description="The correct answer to the question. For MSQ, this might be a comma-separated string or similar representation of multiple correct options.")
    question_type: str = Field(
        description="Type of the question (e.g., MCQ, MSQ, SAQ, LAQ)")


class Quiz(BaseModel):
    """Represents the entire quiz consisting of multiple questions."""
    questions: List[QuizQuestion] = Field(
        description="List of quiz questions.")


# --- Configuration & Initialization ---

# --- LLM and Embeddings ---
try:
    # llm = ChatGroq(
    #     model=MODEL_NAME,
    #     temperature=0.2,
    #     # Consider adding json_mode if Groq/model supports reliable JSON output enforcement
    #     # model_kwargs={"response_format": {"type": "json_object"}} # Example syntax, check ChatGroq docs
    # )
    llm = LLM(
        model=f"groq/{MODEL_NAME}",
        temperature=0.2,
        # Consider adding json_mode if Groq/model supports reliable JSON output enforcement
        # model_kwargs={"response_format": {"type": "json_object"}} # Example syntax, check ChatGroq docs
    )
    print(f"Using Groq model: {MODEL_NAME}")
except Exception as e:
    print(
        f"Error initializing ChatGroq: {e}. Ensure GROQ_API_KEY is set and model name is valid.")
    raise

try:
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    embeddings.embed_query("test connection")  # Check connection
    print("Using Ollama embeddings: nomic-embed-text")
except Exception as e:
    print(
        f"Error initializing or connecting to OllamaEmbeddings: {e}. Ensure the Ollama service is running.")
    raise

# --- ChromaDB Vector Store ---
if not os.path.exists(CHROMA_DB_PATH) or not os.path.isdir(CHROMA_DB_PATH):
    raise FileNotFoundError(
        f"ChromaDB path not found or is not a directory: {CHROMA_DB_PATH}.")

print(
    f"Connecting to existing ChromaDB at: {CHROMA_DB_PATH} with collection: {CHROMA_COLLECTION_NAME}")
try:
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=CHROMA_COLLECTION_NAME
    )
    chroma_retriever: BaseRetriever = vectorstore.as_retriever(
        search_kwargs={'k': 10})  # Adjust k as needed
    # Test retriever
    chroma_retriever.invoke("test query")
    print("Successfully connected to ChromaDB and created retriever.")
except Exception as e:
    print(
        f"Error connecting to or accessing ChromaDB collection '{CHROMA_COLLECTION_NAME}': {e}")
    raise

# --- Tavily Search Tool ---
tavily_search_tool_instance = None
if TAVILY_API_KEY:
    try:
        tavily_search_tool_instance = TavilySearchResults(max_results=3)
        # Test Tavily
        # tavily_search_tool_instance.invoke("test query")
        print("Tavily search tool created.")
    except Exception as e:
        print(
            f"Warning: Error initializing TavilySearchResults: {e}. Tavily tool will not be available.")
        tavily_search_tool_instance = None
else:
    print("Warning: TAVILY_API_KEY not set. Tavily search tool will not be available.")


# --- CrewAI Tool Definitions ---

# Tool 1: ChromaDB Document Search
class DocumentSearchTool(BaseTool):
    name: str = "Search Local Documents"
    description: str = ("Searches and returns relevant excerpts from the uploaded PDF documents "
                        "based on the user's query or topic. Use this first for context.")
    retriever: BaseRetriever  # Store the retriever instance

    def _run(self, argument: str) -> str:
        print(f"---> DocumentSearchTool running with argument: {argument}")
        try:
            results = self.retriever.invoke(argument)
            # Format results into a single string context
            context = "\n\n".join([doc.page_content for doc in results])
            return context if context else "No relevant documents found."
        except Exception as e:
            print(f"Error during document search: {e}")
            return f"Error searching documents: {e}"

# Tool 2: Tavily Web Search (Optional)


class WebSearchTool(BaseTool):
    name: str = "Search Web"
    description: str = ("Performs a web search using Tavily to find information "
                        "if the local documents are insufficient or if specifically asked. "
                        "Use this as a secondary option.")
    tavily: Optional[TavilySearchResults]  # Store the Tavily instance

    def _run(self, argument: str) -> str:
        if not self.tavily:
            return "Web search tool is not configured or available."
        print(f"---> WebSearchTool running with argument: {argument}")
        try:
            results = self.tavily.invoke(argument)
            # Tavily results might be dicts or strings depending on version/config
            if isinstance(results, list) and results and isinstance(results[0], dict) and 'content' in results[0]:
                return "\n\n".join([r['content'] for r in results])
            elif isinstance(results, str):
                return results
            else:
                return "No relevant web results found or unexpected format."

except Exception as e:
            print(f"Error during web search: {e}")
            return f"Error searching web: {e}"


# Instantiate the tools
document_search_tool = DocumentSearchTool(retriever=chroma_retriever)
web_search_tool = WebSearchTool(tavily=tavily_search_tool_instance)


# --- CrewAI Agent Definitions ---

# Agent 1: Researches context based on the user request
context_researcher = Agent(
    role='Context Research Specialist',
    goal=('Find the most relevant information to answer the user\'s quiz request. '
          'Prioritize searching local documents using the "Search Local Documents" tool. '
          'Only use the "Search Web" tool if local documents are insufficient or explicitly requested.'),
    backstory=('You are an expert in information retrieval. Your primary task is to consult '
               'a specialized knowledge base (local documents). You can consult the broader web, '
               'but only as a last resort or when asked, ensuring the retrieved context is focused '
               'on the user\'s topic.'),
    # Conditionally add web tool
    tools=[document_search_tool] +
    ([web_search_tool] if tavily_search_tool_instance else []),
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=3  # Limit iterations for research
)

# Agent 2: Generates the quiz based on research and instructions
# We embed the core instructions from the original system prompt here.
quiz_generator = Agent(
    role='Expert Quiz Generator',
    goal=(f'Create a comprehensive and accurate quiz based *only* on the provided context and user request. '
          f'Strictly adhere to the user\'s specifications for number and types of questions '
          f'(defaulting to 5 questions: 2 MCQ, 1 MSQ, 1 SAQ, 1 LAQ if not specified). '
          f'Format the output *only* as a JSON object matching the Quiz Pydantic model structure below. '
          f'Ensure `options` is a list for MCQ/MSQ and `null` for SAQ/LAQ. '
          f'Do not include any introductory text, explanations, or apologies outside the final JSON object.\n'
          f'Required JSON Structure:\n'
          f'```json\n'
          f'{{"questions": [\n'
          f'  {{"question": "...", "question_type": "MCQ", "options": ["A", "B", "C", "D"], "answer": "..."}},\n'
          f'  {{"question": "...", "question_type": "SAQ", "options": null, "answer": "..."}}\n'
          f']}}\n'
          f'```'
          ),
    backstory=('You are a meticulous AI specializing in educational content creation. '
               'You receive context and user requirements, and your sole purpose is to generate '
               'a high-quality quiz conforming precisely to the requested format and content constraints. '
               'Accuracy and adherence to the JSON output format are paramount.'),
    # No tools needed for generation itself, relies on context from the task
    llm=llm,
    verbose=True,
    allow_delegation=False,
)


# --- CrewAI Task Definitions ---

research_task = Task(
    description=(
        '1. Understand the user\'s quiz request: "{user_request}".\n'
        '2. Use the available tools (prioritizing "Search Local Documents") to find the most relevant context '
        'needed to create a quiz on the specified topic.\n'
        '3. Compile the retrieved information into a comprehensive context passage.'
    ),
    expected_output=(
        'A text block containing all the relevant information gathered from the '
        'document search (and potentially web search) to be used for quiz generation.'
    ),
    agent=context_researcher,
    # inputs are implicitly handled by crew definition and placeholders like {user_request}
)

quiz_generation_task = Task(
    description=(
        '1. Review the user\'s original request: "{user_request}".\n'
        '2. Review the research context provided by the Context Research Specialist.\n'
        '3. Generate the quiz questions based *strictly* on the provided context and adhering '
        'to the user\'s specifications (or defaults) for number and types of questions '
        '(MCQ, MSQ, SAQ, LAQ).\n'
        '4. Format the entire output *only* as a JSON object matching the specified Quiz Pydantic model structure. '
        'Pay close attention to the `options` field (list or null) and `question_type` field.'
    ),
    expected_output=(
        'A single, valid JSON object representing the generated quiz, conforming to the Quiz Pydantic model. '
        'No other text, explanations, or formatting should be present.'
    ),
    agent=quiz_generator,
    # This task depends on the output of the research_task
    context=[research_task],
    # CrewAI's attempt to force JSON output matching the Pydantic model:
    # output_json=Quiz
)


# --- Crew Definition ---

quiz_crew = Crew(
    agents=[context_researcher, quiz_generator],
    tasks=[research_task, quiz_generation_task],
    process=Process.sequential,  # Run research first, then generation
    verbose=True # Use 1 or 2 for different levels of log detail
    # memory=True # Optional: Enable memory if conversations need to be recalled across multiple runs
)

# --- Function to Run the Quiz Generation using CrewAI ---


def generate_quiz_crewai(user_request: str) -> Optional[Dict[str, Any]]:
    """
    Generates a quiz using CrewAI based on the user request.

    Args:
        user_request: The user's prompt specifying the topic, etc.

    Returns:
        A dictionary representing the generated Quiz JSON, or None if an error occurs.
    """
    print(
        f"\n--- Generating Quiz with CrewAI for Request: '{user_request}' ---")
    inputs = {'user_request': user_request}
    quiz_result = None
    try:
        # Kick off the crew
        result = quiz_crew.kickoff(inputs=inputs)

        print("\n--- CrewAI Kickoff Result ---")
        print(type(result))
        print(result)
        print("--- End CrewAI Kickoff Result ---")

        # CrewAI with output_json *should* return the parsed object or dict
        if isinstance(result, Quiz):
            print("CrewAI returned a validated Quiz Pydantic object.")
            quiz_result = result.dict()  # Use .dict() for pydantic v1
        elif isinstance(result, dict) and 'questions' in result:
            print("CrewAI returned a dictionary matching Quiz structure.")
            # Optional: Validate again just to be sure
            try:
                validated_quiz = Quiz.model_validate(result)
                quiz_result = validated_quiz.dict()  # Use .dict()
                print("Dictionary result successfully validated against Pydantic model.")
            except Exception as e:
                print(
                    f"Validation Error: CrewAI dictionary output does not match Quiz model: {e}")
                print("Received Dictionary:", json.dumps(result, indent=2))
                quiz_result = None  # Discard invalid dict
        elif isinstance(result, str):
            # Fallback: If CrewAI returns a string, try parsing it
            print("CrewAI returned a string. Attempting JSON parsing and validation...")
            try:
                # It's possible the string contains explanations around the JSON
                # Try to extract JSON block if possible (simple example below)
                json_match = re.search(
                    r'```json\s*(\{.*?\})\s*```', result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Assume the whole string is JSON, or try finding the first '{'
                    json_str = result[result.find('{'):result.rfind('}')+1]

                parsed_json = json.loads(json_str)
                validated_quiz = Quiz.model_validate(parsed_json)
                quiz_result = validated_quiz.dict()  # Use .dict()
                print("Successfully parsed and validated JSON string from fallback.")
            except json.JSONDecodeError as e:
                print(
                    f"JSON Decode Error: Failed to parse string result as JSON: {e}")
                print("Received String:", result)
            except Exception as e:  # Catches Pydantic validation errors too
                print(
                    f"Validation Error: Parsed JSON string does not match Quiz model: {e}")
                if 'parsed_json' in locals():
                    print("Parsed JSON:", json.dumps(parsed_json, indent=2))
                else:
                    print("Received String:", result)
        else:
            print("CrewAI returned an unexpected result type.")

        return quiz_result

    except Exception as e:
        print(f"An error occurred during CrewAI quiz generation: {e}")
        traceback.print_exc()
        return None

# --- Example Usage ---


if __name__ == "__main__":
    import re  # Import re for fallback JSON extraction

    example_user_query = "Generate a 5 question quiz about the history of Harappan Civilisation as described in the documents. Include 2 MCQs, 1 MSQ, 1 SAQ, and 1 LAQ."
    # Ensure your ChromaDB has relevant content!

    generated_quiz_json = generate_quiz_crewai(example_user_query)

    if generated_quiz_json:
        print("\n✅ --- Generated Quiz (JSON Output) --- ✅")
        print(json.dumps(generated_quiz_json, indent=2))

        # Optional: Save to file
        # try:
        #     with open("generated_quiz_crewai.json", "w") as f:
        #         json.dump(generated_quiz_json, f, indent=2)
        #     print("\nQuiz saved to generated_quiz_crewai.json")
        # except Exception as e:
        #     print(f"Error saving quiz to file: {e}")
    else:
        print("\n❌ --- Quiz Generation Failed --- ❌")
