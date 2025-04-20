"""
DO NOT USE THIS FILE.

USE create_note_and_quiz_ai.py instead.
"""

from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from vars import MODEL_NAME
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from backend.app.utils.create_note_and_quiz_ai import combine_contexts
from vars import *


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

**Context:**
{context}

**User Request:**
{user_prompt}

Begin crafting a quiz based *only* on the provided context and user prompt:
"""
class QuizQuestion(BaseModel):
    question: str = Field(description="The question for the quiz.")
    options: List[str] | None = Field(
        description="List of options for the question.")
    answer: str = Field(description="The correct answer to the question.")


class Quiz(BaseModel):
    questions: List[QuizQuestion] = Field(
        description="List of quiz questions.")


# client.bind_tools([Quiz])
parser_quiz = JsonOutputParser(pydantic_object=Quiz)

# prompt_quiz = ChatPromptTemplate.from_template(template_quiz)
prompt_quiz = PromptTemplate(
    template=template_quiz,
    input_variables=["context", "user_prompt"],
    partial_variables={"format_instructions": parser_quiz.get_format_instructions()},
)


client = ChatGroq(model=MODEL_NAME, temperature=0.2)





try:
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)
except Exception as e:
    print(f"Error initializing OllamaEmbeddings: {e}")
    print(
        f"Ensure Ollama is running and the model '{OLLAMA_EMBED_MODEL}' is available.")
    exit()


try:
    tavily_retriever = TavilySearchAPIRetriever(k=3)
except Exception as e:
    print(f"Error initializing TavilySearchAPIRetriever: {e}")
    print("Please ensure the TAVILY_API_KEY environment variable is set correctly.")
    exit()


try:
    vector_store = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_PATH,
    )
    print(
        f"Vector store initialized. Collection: {CHROMA_COLLECTION_NAME}. Number of documents: {vector_store._collection.count()}")
    chroma_retriever = vector_store.as_retriever(search_kwargs={"k": 3})
except Exception as e:
    print(f"Error initializing Chroma DB from {CHROMA_DB_PATH}: {e}")
    print("Ensure the Chroma DB directory exists and is accessible.")
    exit(1)

retrieval_chain = RunnableParallel(
    tavily=tavily_retriever,
    chroma=chroma_retriever
) | RunnableLambda(combine_contexts)


chain_quiz = (
    RunnablePassthrough.assign(
        context=RunnableLambda(lambda x: x['user_prompt']) | retrieval_chain
    )
    | prompt_quiz
    | client
    | parser_quiz
)


print("ANSWER : ", chain_quiz.invoke(
    {"user_prompt": "create a quiz on the history of the Harappan Civilisation"}))
