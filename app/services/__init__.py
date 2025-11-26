import os
from typing import List
from openai import OpenAI
import google.generativeai as genai
try:
    import syntheticai
except ImportError:
    syntheticai = None

# --- OpenAI Configuration ---
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if openai_api_key:
    try:
        openai_client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")

# --- Gemini Configuration ---
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_client = None
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        gemini_client = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")


class LLMService:
    """Service for interacting with LLMs (OpenAI, Gemini) for RAG functionality"""

    @staticmethod
    def query_with_context(query: str, context: str, model: str = "gpt-3.5-turbo") -> str:
        """Query LLM with provided context from documents."""
        if model.startswith("gemini"):
            return LLMService._gemini_query(query, context)
        else:
            return LLMService._openai_query(query, context, model)

    @staticmethod
    def _openai_query(query: str, context: str, model: str) -> str:
        if not openai_client:
            return f"OpenAI client not available. Context: {context[:100]}... Query: {query}"
        try:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Be extremely concise and direct. Do not be verbose."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")

    @staticmethod
    def _gemini_query(query: str, context: str) -> str:
        if not gemini_client:
            return f"Gemini client not available. Context: {context[:100]}... Query: {query}"
        try:
            prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer concisely and directly based on the context. Avoid unnecessary words."
            response = gemini_client.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")

    @staticmethod
    def _synthetic_query(query: str, context: str) -> str:
        if not synthetic_client:
            return f"Synthetic AI client not available. Context: {context[:100]}... Query: {query}"
        try:
            prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer concisely and directly based on the context. Avoid unnecessary words."
            response = synthetic_client.generate(prompt)
            return response
        except Exception as e:
            raise Exception(f"Synthetic AI API Error: {str(e)}")

    @staticmethod
    def semantic_search(query: str, assets_content: List[str], model: str = "gpt-3.5-turbo") -> List[int]:
        """Find most relevant assets using an LLM."""
        if not openai_client and not gemini_client:
             # Fallback: return first asset indices if no LLM
            return list(range(min(2, len(assets_content))))

        try:
            combined_content = "\n---DOCUMENT START---\n".join([f"ID {i}: {content[:200]}..." for i, content in enumerate(assets_content)])
            
            prompt = f"You are a document retrieval expert. Given a query and document snippets, identify which documents are most relevant. Return ONLY the document IDs as a comma-separated list (e.g., '1,3,5').\n\nQuery: {query}\n\nDocuments:\n{combined_content}"

            if model.startswith("gemini") and gemini_client:
                 response_text = gemini_client.generate_content(prompt).text
            elif openai_client:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo", # Using a reliable model for this task
                    messages=[
                        {"role": "system", "content": "You are a document retrieval expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=50,
                )
                response_text = response.choices[0].message.content
            else: # Fallback if preferred client is missing
                return list(range(min(2, len(assets_content))))

            indices = [int(x.strip()) for x in response_text.split(',') if x.strip().isdigit()]
            return indices
        except Exception as e:
            # In case of any error, fall back to returning all indices
            print(f"LLM semantic search error: {e}. Falling back to returning all documents.")
            return list(range(len(assets_content)))
