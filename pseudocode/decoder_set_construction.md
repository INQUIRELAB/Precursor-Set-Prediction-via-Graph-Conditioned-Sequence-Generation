# Pseudocode: Decoder-to-Set Construction (Conceptual)

This illustrates the *concept* of converting autoregressive token generation into an unordered set prediction.

```text
Input:
  target_conditioning  = {composition_features, optional_structure_embedding, optional_retrieval_contexts}

Procedure:
  initialize token_sequence = [<SOS>]
  while last_token != <EOS> and length < max_length:
     next_token = GeneratorStep(token_sequence, target_conditioning)
     append next_token to token_sequence

  Convert sequence to set:
     discard <SOS> and <EOS>
     apply normalization to token strings (e.g., canonical precursor formatting)
     remove duplicates
     optionally apply light plausibility filters

Output:
  predicted_precursor_set
```

