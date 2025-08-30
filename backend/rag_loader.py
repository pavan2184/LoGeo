import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegulationRAG:
    """
    RAG system for regulation compliance using FAISS vector search.
    Loads regulation summaries, creates embeddings, and enables semantic retrieval.
    """
    
    def __init__(self, regulations_dir: str = "regulations", model_name: str = "all-MiniLM-L6-v2"):
        self.regulations_dir = regulations_dir
        self.model_name = model_name
        self.model = None
        self.index = None
        self.documents = []
        self.metadata = []
        self.is_loaded = False
        
    def load_model(self):
        """Load the sentence transformer model"""
        if self.model is None:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        
    def load_regulations(self) -> List[Dict]:
        """Load all regulation text files from the regulations directory"""
        regulations = []
        
        if not os.path.exists(self.regulations_dir):
            logger.warning(f"Regulations directory {self.regulations_dir} not found")
            return regulations
            
        for filename in os.listdir(self.regulations_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.regulations_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        
                    # Extract regulation name from filename
                    reg_name = filename.replace('.txt', '').replace('_', ' ').title()
                    
                    regulations.append({
                        'name': reg_name,
                        'filename': filename,
                        'content': content,
                        'chunks': self._chunk_text(content, reg_name)
                    })
                    logger.info(f"Loaded regulation: {reg_name}")
                    
                except Exception as e:
                    logger.error(f"Error loading {filepath}: {e}")
                    
        return regulations
    
    def _chunk_text(self, text: str, reg_name: str, chunk_size: int = 500) -> List[Dict]:
        """Split regulation text into manageable chunks for embedding with enhanced structure"""
        # Split by sections first (looking for headers)
        sections = []
        current_section = ""
        current_header = ""
        
        lines = text.split('\n')
        for line in lines:
            # Detect headers (lines that are shorter and end with colon or are in caps)
            if (len(line.strip()) < 100 and 
                (line.strip().endswith(':') or line.strip().isupper() or 
                 line.strip().startswith('Key ') or line.strip().startswith('Relevant ') or 
                 line.strip().startswith('Compliance '))):
                # Save previous section
                if current_section.strip():
                    sections.append({
                        'header': current_header,
                        'content': current_section.strip()
                    })
                current_header = line.strip()
                current_section = ""
            else:
                current_section += line + "\n"
        
        # Add the last section
        if current_section.strip():
            sections.append({
                'header': current_header,
                'content': current_section.strip()
            })
        
        # Create chunks from sections
        chunks = []
        for section in sections:
            section_text = f"{section['header']}\n{section['content']}"
            
            # If section is small enough, keep as one chunk
            if len(section_text) <= chunk_size:
                chunks.append({
                    'text': section_text.strip(),
                    'regulation': reg_name,
                    'type': 'section',
                    'header': section['header']
                })
            else:
                # Split large sections into smaller chunks
                paragraphs = section['content'].split('\n\n')
                current_chunk = section['header'] + "\n"
                
                for para in paragraphs:
                    if len(current_chunk) + len(para) > chunk_size and current_chunk.strip():
                        chunks.append({
                            'text': current_chunk.strip(),
                            'regulation': reg_name,
                            'type': 'content',
                            'header': section['header']
                        })
                        current_chunk = para + "\n"
                    else:
                        current_chunk += para + "\n\n"
                
                # Add the last chunk
                if current_chunk.strip():
                    chunks.append({
                        'text': current_chunk.strip(),
                        'regulation': reg_name,
                        'type': 'content',
                        'header': section['header']
                    })
        
        return chunks
    
    def build_index(self, force_rebuild: bool = False):
        """Build FAISS index from regulation documents"""
        index_path = "regulation_index.faiss"
        metadata_path = "regulation_metadata.pkl"
        
        # Load existing index if available and not forcing rebuild
        if not force_rebuild and os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info("Loaded existing FAISS index")
                self.is_loaded = True
                return
            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}, rebuilding...")
        
        # Load model and regulations
        self.load_model()
        regulations = self.load_regulations()
        
        if not regulations:
            logger.error("No regulations loaded, cannot build index")
            return
        
        # Collect all text chunks
        all_chunks = []
        for reg in regulations:
            all_chunks.extend(reg['chunks'])
        
        if not all_chunks:
            logger.error("No text chunks found")
            return
        
        # Create embeddings
        logger.info(f"Creating embeddings for {len(all_chunks)} text chunks...")
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.metadata = all_chunks
        
        # Save index and metadata
        faiss.write_index(self.index, index_path)
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        logger.info(f"Built FAISS index with {len(all_chunks)} chunks")
        self.is_loaded = True
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for relevant regulation text chunks"""
        if not self.is_loaded or self.index is None:
            logger.warning("Index not loaded, building index...")
            self.build_index()
        
        if not self.is_loaded:
            return []
        
        # Encode query
        if self.model is None:
            self.load_model()
        
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['relevance_score'] = float(score)
                results.append(result)
        
        return results
    
    def get_relevant_regulations(self, feature_title: str, feature_description: str, threshold: float = 0.3) -> List[str]:
        """Get list of regulation names relevant to a feature"""
        query = f"{feature_title} {feature_description}"
        results = self.search(query, k=10)
        
        # Extract unique regulation names above threshold
        relevant_regs = set()
        for result in results:
            if result['relevance_score'] > threshold:
                relevant_regs.add(result['regulation'])
        
        return list(relevant_regs)
    
    def get_hierarchical_classification(self, feature_title: str, feature_description: str) -> Dict:
        """Get hierarchical classification of compliance requirements"""
        query = f"{feature_title} {feature_description}"
        results = self.search(query, k=15)
        
        # Categorize by compliance areas
        classification = {
            'data_protection': [],
            'age_verification': [],
            'content_moderation': [],
            'privacy_rights': [],
            'cross_border': [],
            'reporting': []
        }
        
        # Keywords for categorization
        categories = {
            'data_protection': ['personal data', 'data processing', 'data protection', 'privacy', 'data collection'],
            'age_verification': ['age', 'minor', 'child', 'parental consent', 'verification'],
            'content_moderation': ['content', 'moderation', 'harmful', 'inappropriate', 'reporting'],
            'privacy_rights': ['rights', 'access', 'deletion', 'portability', 'consent'],
            'cross_border': ['cross-border', 'international', 'transfer', 'localization'],
            'reporting': ['report', 'breach', 'incident', 'notification']
        }
        
        for result in results:
            text_lower = result['text'].lower()
            reg_name = result['regulation']
            
            for category, keywords in categories.items():
                if any(keyword in text_lower for keyword in keywords):
                    if reg_name not in classification[category]:
                        classification[category].append({
                            'regulation': reg_name,
                            'relevance_score': result['relevance_score'],
                            'context': result['text'][:200] + "..."
                        })
        
        return classification
    
    def get_regulatory_context(self, feature_title: str, feature_description: str, max_context_length: int = 3000) -> str:
        """
        Get relevant regulatory context from legitimate sources for compliance analysis.
        Returns contextual information for LLM to perform regulatory analysis.
        """
        query = f"{feature_title} {feature_description}"
        results = self.search(query, k=8)  # Get more results for comprehensive analysis
        
        if not results:
            logger.warning(f"No regulatory context found for query: {query}")
            return ""
        
        context_parts = []
        current_length = 0
        
        # Add a header to clarify the source
        header = "REGULATORY CONTEXT FROM LEGITIMATE SOURCES:\n"
        context_parts.append(header)
        current_length += len(header)
        
        for result in results:
            # Format with clear regulation source and relevance
            text = f"\n[SOURCE: {result['regulation']} | Relevance: {result['relevance_score']:.2f}]\n{result['text']}\n"
            
            if current_length + len(text) <= max_context_length:
                context_parts.append(text)
                current_length += len(text)
            else:
                # If we can't fit the whole result, add a truncated version
                remaining_space = max_context_length - current_length - 100  # Leave some buffer
                if remaining_space > 200:  # Only add if meaningful content can fit
                    truncated_text = f"\n[SOURCE: {result['regulation']} | Relevance: {result['relevance_score']:.2f}]\n{result['text'][:remaining_space]}...\n"
                    context_parts.append(truncated_text)
                break
        
        context = "".join(context_parts)
        
        if len(context.strip()) < 100:
            logger.warning(f"Insufficient regulatory context found for feature: {feature_title}")
        
        return context

# Global RAG instance
_rag_instance = None

def get_rag_instance() -> RegulationRAG:
    """Get singleton RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RegulationRAG()
        _rag_instance.build_index()
    return _rag_instance

def search_regulations(query: str, k: int = 5) -> List[Dict]:
    """Convenience function to search regulations"""
    rag = get_rag_instance()
    return rag.search(query, k)

if __name__ == "__main__":
    # Test the RAG system
    rag = RegulationRAG()
    rag.build_index(force_rebuild=True)
    
    # Test search
    test_query = "age verification for social media"
    results = rag.search(test_query)
    
    print(f"Search results for: {test_query}")
    for i, result in enumerate(results):
        print(f"\n{i+1}. {result['regulation']} (Score: {result['relevance_score']:.3f})")
        print(f"   {result['text'][:200]}...")
    
    # Test regulatory context generation
    context = rag.get_regulatory_context("user registration", "allow users to create accounts with email verification")
    print(f"\nRegulatory context:\n{context}")
