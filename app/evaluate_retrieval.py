def calculate_precision_at_k(retrieved_docs: list, relevant_docs: list, k: int) -> float:
    """
    Calculates Precision@K metric for RAG retrieval quality evaluation.
    """
    retrieved_k = retrieved_docs[:k]
    relevant_retrieved = [doc for doc in retrieved_k if doc in relevant_docs]
    return len(relevant_retrieved) / k

if __name__ == "__main__":
    # Dummy data to show the recruiter how evaluation works
    ground_truth = ["doc_1.pdf", "doc_3.pdf"]
    retrieved_results = ["doc_1.pdf", "doc_2.pdf", "doc_3.pdf", "doc_4.pdf"]
    
    k = 3
    precision = calculate_precision_at_k(retrieved_results, ground_truth, k=k)
    print(f"--- RAG Retrieval Evaluation ---")
    print(f"Precision@{k}: {precision:.2f}")
