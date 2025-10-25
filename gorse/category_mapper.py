"""
Category Mapper - Maps user interests and post labels to master categories
using semantic similarity matching.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from master_categories import MASTER_CATEGORIES, CATEGORY_KEYWORDS, get_category_display_name


class CategoryMapper:
    """Maps arbitrary labels to standardized master categories"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2', top_k=4):
        """
        Args:
            model_name: Sentence transformer model to use
            top_k: Number of master categories to assign (default: 4)
        """
        print(f"[CategoryMapper] Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.top_k = top_k
        
        # Pre-compute embeddings for all master categories and their keywords
        print(f"[CategoryMapper] Computing embeddings for {len(MASTER_CATEGORIES)} master categories...")
        self._compute_category_embeddings()
        print(f"[CategoryMapper] Ready! Will map to top {top_k} categories.")
    
    def _compute_category_embeddings(self):
        """Pre-compute embeddings for master categories using their keywords"""
        self.category_embeddings = {}
        
        for category in MASTER_CATEGORIES:
            keywords = CATEGORY_KEYWORDS.get(category, [])
            
            # Combine category name and keywords for richer representation
            category_display = get_category_display_name(category)
            all_text = [category_display] + keywords
            
            # Get embeddings for all texts
            embeddings = self.model.encode(all_text)
            
            # Average the embeddings to get a single representation
            avg_embedding = np.mean(embeddings, axis=0)
            
            self.category_embeddings[category] = avg_embedding
    
    def map_labels_to_categories(self, labels, verbose=False):
        """
        Map a list of user/item labels to top-k master categories
        
        Args:
            labels: List of label strings (e.g., ["nutrition", "healthy eating", "cooking"])
            verbose: Print mapping details
            
        Returns:
            List of top-k master category IDs
        """
        if not labels:
            return []
        
        # Combine all user labels into one text for better context
        combined_text = " ".join(labels)
        
        # Get embedding for the combined labels
        label_embedding = self.model.encode([combined_text])[0]
        
        # Calculate similarity to each master category
        similarities = {}
        for category, cat_embedding in self.category_embeddings.items():
            similarity = np.dot(label_embedding, cat_embedding) / (
                np.linalg.norm(label_embedding) * np.linalg.norm(cat_embedding)
            )
            similarities[category] = similarity
        
        # Sort by similarity and get top-k
        sorted_categories = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        top_categories = [cat for cat, sim in sorted_categories[:self.top_k]]
        
        if verbose:
            print(f"\n  Original labels: {labels}")
            print(f"  Mapped to categories:")
            for i, (cat, sim) in enumerate(sorted_categories[:self.top_k], 1):
                print(f"    {i}. {get_category_display_name(cat)} ({sim:.3f})")
        
        return top_categories
    
    def map_single_label_to_categories(self, label, verbose=False):
        """Convenience method for mapping a single label"""
        return self.map_labels_to_categories([label], verbose=verbose)


# Test function
def test_category_mapper():
    """Test the category mapper with some examples"""
    print("\n" + "="*70)
    print("TESTING CATEGORY MAPPER")
    print("="*70)
    
    mapper = CategoryMapper(top_k=4)
    
    test_cases = [
        ["nutrition", "healthy eating", "cooking"],
        ["gaming", "video games", "esports"],
        ["mental health", "anxiety", "meditation"],
        ["travel", "adventure", "exploring"],
        ["memes", "funny", "viral content"],
        ["bullying", "cyberbullying", "online safety"],
    ]
    
    for labels in test_cases:
        categories = mapper.map_labels_to_categories(labels, verbose=True)
        print()


if __name__ == "__main__":
    test_category_mapper()
