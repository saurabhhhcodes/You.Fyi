from typing import List, Tuple
from app.services import LLMService


class RAGService:
    """Retrieval-Augmented Generation service"""
    
    @staticmethod
    def retrieve_and_answer(
        query: str,
        assets: List,
        use_llm: bool = True,
        model: str = "gpt-3.5-turbo"
    ) -> Tuple[str, List[str]]:
        """
        Retrieve relevant assets and generate answer using LLM
        
        Args:
            query: User question
            assets: List of Asset objects
            use_llm: Whether to use real LLM or return raw content
            model: LLM model to use
            
        Returns:
            Tuple of (answer, source_asset_ids)
        """
        if not assets:
            return "No assets found in kit to answer query.", []
        
        assets_content = [asset.content for asset in assets]
        asset_ids = [asset.id for asset in assets]
        
        # Use LLM for semantic search
        if use_llm:
            try:
                relevant_indices = LLMService.semantic_search(query, assets_content)
                if not relevant_indices:
                    relevant_indices = [0]  # Default to first asset
            except Exception:
                relevant_indices = list(range(len(assets_content)))
        else:
            relevant_indices = list(range(len(assets_content)))
        
        # Get context from relevant assets
        context = "\n---\n".join([
            assets_content[i] for i in relevant_indices if i < len(assets_content)
        ])
        
        # Get answer from LLM
        if use_llm:
            answer = LLMService.query_with_context(query, context, model)
        else:
            answer = f"Retrieved {len(relevant_indices)} relevant documents. Content preview: {context[:200]}..."
        
        sources = [asset_ids[i] for i in relevant_indices if i < len(asset_ids)]
        return answer, sources
