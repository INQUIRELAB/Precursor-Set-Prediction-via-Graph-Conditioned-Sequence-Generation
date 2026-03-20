# Pseudocode: Retrieval Priors Fusion (Conceptual)

This illustrates the conceptual role of retrieval priors as *conditioning context*.

```text
Input:
  query_representation
  retrieval_index

Procedure:
  neighbors = RetrieveSimilarContexts(query_representation, top_M)
  retrieval_context_embedding = EncodeNeighbors(neighbors)

  conditioning_context = Fuse(query_representation, retrieval_context_embedding)
  output = Generator(conditioning_context)
```

Notes:
- Retrieval is intended to improve plausibility via historical priors.
- The method is not limited to outputting only combinations observed verbatim in the training corpus.

