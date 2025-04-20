# """This cookbook shows how to implement Agentic RAG using Hybrid Search and Reranking.
# 1. Run: `pip install agno anthropic cohere lancedb tantivy sqlalchemy` to install the dependencies
# 2. Export your ANTHROPIC_API_KEY and CO_API_KEY
# 3. Run: `python cookbook/agent_concepts/agentic_search/agentic_rag.py` to run the agent
# """
# import os
# import shutil
# from agno.agent import Agent
# from agno.embedder.ollama import OllamaEmbedder
# from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
# from agno.models.groq import Groq
# from agno.reranker.base import Reranker
# from agno.vectordb.lancedb import LanceDb, SearchType
# from vars import MODEL_NAME
# from dotenv import load_dotenv

# load_dotenv()

# # Define embedding model - use a consistent model throughout
# EMBED_MODEL = "nomic-embed-text"

# # First, clean up any existing database to prevent dimension mismatch
# lancedb_path = "tmp/lancedb"
# if os.path.exists(lancedb_path):
#     print(f"Removing existing LanceDB at {lancedb_path}")
#     shutil.rmtree(lancedb_path)
#     print("Database removed. Will be recreated with current embedding dimensions.")

# # Create embedder with explicit dimensions
# embedder = OllamaEmbedder(id=EMBED_MODEL)

# # Create a knowledge base, loaded with documents from a URL
# knowledge_base = PDFKnowledgeBase(
#     path="../../uploads",
#     # Use LanceDB as the vector database, store embeddings in the `agno_docs` table
#     vector_db=LanceDb(
#         uri=lancedb_path,
#         table_name="agno_docs",
#         search_type=SearchType.vector,
#         embedder=embedder,
#         reranker=Reranker(model=EMBED_MODEL),
#     ),
#     reader=PDFReader(chunk=True, chunk_size=500)
# )

# agent = Agent(
#     model=Groq(id=MODEL_NAME),
#     # Agentic RAG is enabled by default when `knowledge` is provided to the Agent.
#     knowledge=knowledge_base,
#     # search_knowledge=True gives the Agent the ability to search on demand
#     # search_knowledge is True by default
#     search_knowledge=True,
#     instructions=[
#         "Include sources in your response.",
#         "Always search your knowledge before answering the question.",
#         "Only include the output in your response. No other text.",
#     ],
#     markdown=True,
# )

# if __name__ == "__main__":
#     # Always recreate the knowledge base to ensure embedding consistency
#     print("Loading knowledge base and creating embeddings...")
#     # knowledge_base.load(recreate=False)
#     print("Knowledge base loaded successfully")

#     # Test the search functionality
#     try:
#         query = "Town Planning in Harappan Civilization"
#         print(f"Testing search with query: '{query}'")
#         results = knowledge_base.search(query=query)
#         print(f"Search successful, found {len(results)} documents")

#         # Generate response
#         agent.print_response(
#             "Write a short note on the topic of Town Planning in Harappan Civilization", stream=True)
#     except Exception as e:
#         print(f"Error during execution: {e}")

import re
import pprint
text = '**Title:** Town Planning of the Harappan Civilization\n\n**Introduction:**\nThe Harappan Civilization, one of the most ancient and sophisticated civilizations in human history, is renowned for its remarkable urban organization and engineering skills. The town planning of the Harappan Civilization reflects a high degree of organization, discipline, and foresight. The cities were designed on a grid pattern, with a clear division of space, wide and well-aligned roads, and advanced civic amenities. This report aims to provide a detailed analysis of the town planning of the Harappan Civilization, highlighting its key features, achievements, and significance.\n\n**Main Sections:**\n\n### 1. **Grid Pattern and Urban Layout**\nThe Harappan cities were designed on a grid pattern, with streets laid out in straight lines intersecting at right angles. This grid pattern created a clear division of space, with different areas allocated for residential, commercial, and civic purposes. The cities were typically divided into two main areas: the Citadel and the Lower City. The Citadel, located on a raised platform, housed the administrative and civic buildings, while the Lower City was the residential area.\n\nThe grid pattern of the Harappan cities was a remarkable achievement, considering the lack of advanced technology and machinery. The streets were wide and well-aligned, with some of them measuring up to 9 meters in width. The roads were constructed using a combination of baked bricks, mud, and stone, and were often covered with a layer of smooth surface.\n\n### 2. **Civic Amenities and Infrastructure**\nThe Harappan Civilization is notable for its advanced civic amenities and infrastructure. The cities had a sophisticated drainage system, with covered drains and sewage systems that ensured the removal of waste and rainwater. The Harappans also built large public baths, known as the "Great Bath," which were used for ritual and ceremonial purposes.\n\nThe granaries discovered at sites like Harappa, Mohenjodaro, and Lothal served as storehouses for grains, indicating a well-developed system of food storage and distribution. The Harappans also built a dockyard at Lothal, which facilitated trade and commerce.\n\n### 3. **Architecture and Engineering Skills**\nThe Harappan Civilization demonstrates remarkable architecture and engineering skills. The buildings were constructed using baked bricks, which were made from a mixture of clay and water. The bricks were laid in a specific pattern, with a ratio of 2:1, to ensure the stability and durability of the structures.\n\nThe Harappans also developed a unique system of construction, known as the "kiln-fired brick technology," which involved firing bricks in a kiln to achieve a high level of hardness and durability. This technology enabled the construction of large and complex buildings, such as the Great Bath and the granaries.\n\n### 4. **Art and Craft**\nThe Harappan Civilization is also notable for its rich artistic and craft heritage. A well-known piece of art from the Harappan period is the stone sculpture of a bearded man discovered at Mohenjodaro, which is considered one of the finest examples of Harappan art.\n\nThe Harappans were also skilled craftsmen, producing a range of artifacts, including pottery, jewelry, and tools. The chalcolithic cultures, which succeeded the Harappan Civilization, are characterized by the use of tools made of copper as well as stone.\n\n**Details:**\n\n* The Harappan cities were built using a combination of baked bricks, mud, and stone.\n* The streets were wide and well-aligned, with some of them measuring up to 9 meters in width.\n* The drainage system was sophisticated, with covered drains and sewage systems.\n* The granaries were built to store grains, indicating a well-developed system of food storage and distribution.\n* The dockyard at Lothal facilitated trade and commerce.\n\n**Data/Analysis:**\nThe Harappan Civilization\'s town planning is a testament to their advanced engineering skills and urban organization. The grid pattern of the cities, the sophisticated drainage system, and the advanced civic amenities demonstrate a high level of planning and foresight.\n\nThe use of kiln-fired brick technology and the construction of large and complex buildings, such as the Great Bath and the granaries, indicate a high degree of architectural and engineering expertise.\n\n**Conclusion:**\nThe town planning of the Harappan Civilization is a remarkable achievement that reflects their advanced engineering skills, urban organization, and civic awareness. The grid pattern of the cities, the sophisticated drainage system, and the advanced civic amenities demonstrate a high level of planning and foresight.\n\nThe Harappan Civilization\'s legacy can be seen in the modern-day urban planning, with their concept of bathing pools and granaries influencing contemporary designs. The Harappan Civilization\'s achievements in town planning, architecture, and engineering continue to inspire and influence urban planning and development today.\n\n**References:**\nThe information for this report was gathered from web search results and local documents, which provided valuable insights into the town planning of the Harappan Civilization. The web search results provided information on the grid pattern of the cities, the sophisticated drainage system, and the advanced civic amenities. The local documents provided additional context on the architecture, engineering skills, and art of the Harappan Civilization.\n\n**Word Count: 743**'




if __name__ == "__main__":
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

    test_text = '**Title:** Town Planning of the Harappan Civilization\n\n**Introduction:**\nThe Harappan Civilization, one of the most ancient and sophisticated civilizations in human history, is renowned for its remarkable urban organization and engineering skills. The town planning of the Harappan Civilization reflects a high degree of organization, discipline, and foresight. The cities were designed on a grid pattern, with a clear division of space, wide and well-aligned roads, and advanced civic amenities. This report aims to provide a detailed analysis of the town planning of the Harappan Civilization, highlighting its key features, achievements, and significance.\n\n**Main Sections:**\n\n### 1. **Grid Pattern and Urban Layout**\nThe Harappan cities were designed on a grid pattern, with streets laid out in straight lines intersecting at right angles. This grid pattern created a clear division of space, with different areas allocated for residential, commercial, and civic purposes. The cities were typically divided into two main areas: the Citadel and the Lower City. The Citadel, located on a raised platform, housed the administrative and civic buildings, while the Lower City was the residential area.\n\nThe grid pattern of the Harappan cities was a remarkable achievement, considering the lack of advanced technology and machinery. The streets were wide and well-aligned, with some of them measuring up to 9 meters in width. The roads were constructed using a combination of baked bricks, mud, and stone, and were often covered with a layer of smooth surface.\n\n### 2. **Civic Amenities and Infrastructure**\nThe Harappan Civilization is notable for its advanced civic amenities and infrastructure. The cities had a sophisticated drainage system, with covered drains and sewage systems that ensured the removal of waste and rainwater. The Harappans also built large public baths, known as the "Great Bath," which were used for ritual and ceremonial purposes.\n\nThe granaries discovered at sites like Harappa, Mohenjodaro, and Lothal served as storehouses for grains, indicating a well-developed system of food storage and distribution. The Harappans also built a dockyard at Lothal, which facilitated trade and commerce.\n\n### 3. **Architecture and Engineering Skills**\nThe Harappan Civilization demonstrates remarkable architecture and engineering skills. The buildings were constructed using baked bricks, which were made from a mixture of clay and water. The bricks were laid in a specific pattern, with a ratio of 2:1, to ensure the stability and durability of the structures.\n\nThe Harappans also developed a unique system of construction, known as the "kiln-fired brick technology," which involved firing bricks in a kiln to achieve a high level of hardness and durability. This technology enabled the construction of large and complex buildings, such as the Great Bath and the granaries.\n\n### 4. **Art and Craft**\nThe Harappan Civilization is also notable for its rich artistic and craft heritage. A well-known piece of art from the Harappan period is the stone sculpture of a bearded man discovered at Mohenjodaro, which is considered one of the finest examples of Harappan art.\n\nThe Harappans were also skilled craftsmen, producing a range of artifacts, including pottery, jewelry, and tools. The chalcolithic cultures, which succeeded the Harappan Civilization, are characterized by the use of tools made of copper as well as stone.\n\n**Details:**\n\n* The Harappan cities were built using a combination of baked bricks, mud, and stone.\n* The streets were wide and well-aligned, with some of them measuring up to 9 meters in width.\n* The drainage system was sophisticated, with covered drains and sewage systems.\n* The granaries were built to store grains, indicating a well-developed system of food storage and distribution.\n* The dockyard at Lothal facilitated trade and commerce.\n\n**Data/Analysis:**\nThe Harappan Civilization\'s town planning is a testament to their advanced engineering skills and urban organization. The grid pattern of the cities, the sophisticated drainage system, and the advanced civic amenities demonstrate a high level of planning and foresight.\n\nThe use of kiln-fired brick technology and the construction of large and complex buildings, such as the Great Bath and the granaries, indicate a high degree of architectural and engineering expertise.\n\n**Conclusion:**\nThe town planning of the Harappan Civilization is a remarkable achievement that reflects their advanced engineering skills, urban organization, and civic awareness. The grid pattern of the cities, the sophisticated drainage system, and the advanced civic amenities demonstrate a high level of planning and foresight.\n\nThe Harappan Civilization\'s legacy can be seen in the modern-day urban planning, with their concept of bathing pools and granaries influencing contemporary designs. The Harappan Civilization\'s achievements in town planning, architecture, and engineering continue to inspire and influence urban planning and development today.\n\n**References:**\nThe information for this report was gathered from web search results and local documents, which provided valuable insights into the town planning of the Harappan Civilization. The web search results provided information on the grid pattern of the cities, the sophisticated drainage system, and the advanced civic amenities. The local documents provided additional context on the architecture, engineering skills, and art of the Harappan Civilization.\n\n**Word Count: 743**'

    title, content = extract_title(test_text)
    print(f"Extracted title: {title}")
    print(f"Extracted content: {content}")

