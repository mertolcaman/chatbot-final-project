from rag.retrieval_chain import get_rag_chain

query = "I would like to eat something sweet."
category = "food"  # or "castle", "city", etc.

rag_chain = get_rag_chain(category)
result = rag_chain.invoke({"input": query})
print(result["answer"])


