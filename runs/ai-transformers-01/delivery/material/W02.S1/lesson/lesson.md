# Scaled dot-product self-attention and masking — taught in 3 parts

*W02.S1 · made 2026-11-05 03:59*

## Part 1: Motivation and Mathematics of Scaled Dot-Product Attention (10 min)

**Teaches:** Understand why scaling by the square root of the key dimension is required in dot-product attention to prevent vanishing gradients during softmax.

**Key ideas:** Recap of dot-product attention as a soft dictionary lookup matching Queries (Q) and Keys (K).; Mathematical issue with unscaled dot products: variance of dot products grows linearly with key dimension d_k.; Vanishing gradients in softmax when extreme score magnitudes push activations into saturation regions.; Scaling factor 1/sqrt(d_k) stabilizes the variance of scores back to unit variance.; The standard matrix form: Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V.

**Worked example:** For query vector q = [1.0, -1.0, 2.0, 0.0] and key vector k = [2.0, 0.0, 1.0, -1.0] with dimension d_k = 4, the raw dot product is (1*2) + (-1*0) + (2*1) + (0*-1) = 4.0. Dividing by sqrt(4) = 2 rescales the raw score from 4.0 down to 2.0 before feeding it to softmax.

Files: `material/W02.S1/lesson/part_1/slides.pptx`, `notes.md` (the full narration), `student.html`

## Part 2: Causal Masking and Step-by-Step Matrix Computation (10 min)

**Teaches:** Perform manual matrix calculations for scaled dot-product attention with causal masking to preserve the autoregressive property.

**Key ideas:** The autoregressive constraint in decoders: preventing attention to future token positions.; Constructing a lower-triangular causal mask matrix.; Masking illegal future positions by substituting score values with -infinity prior to softmax.; Softmax behavior on -infinity inputs resulting in exact zero attention probability weights.; Step-by-step matrix calculation of attention output from masked probabilities and Value vectors.

**Worked example:** Let Q K^T / sqrt(d_k) for a 2-token sequence produce score matrix [[2.0, 4.0], [2.0, 4.0]]. Applying a causal mask sets illegal position (1,2) to -inf, yielding [[2.0, -inf], [2.0, 4.0]]. Taking softmax per row gives attention weights [[1.0, 0.0], [0.12, 0.88]]. Multiplying by V = [[1.0, 0.0], [0.0, 1.0]] produces the final output matrix [[1.0, 0.0], [0.12, 0.88]].

Files: `material/W02.S1/lesson/part_2/slides.pptx`, `notes.md` (the full narration), `student.html`

## Part 3: Vectorized PyTorch Implementation of Scaled Dot-Product Attention (10 min)

**Teaches:** Implement vectorized batch scaled dot-product attention with causal masking efficiently using tensor operations in PyTorch.

**Key ideas:** Tensor representations and shapes for query, key, and value matrices in batched operations.; Matrix multiplication via torch.matmul and key transpositions with transpose(-2, -1).; Applying causal mask efficiently using scores.masked_fill(mask == 0, -1e9).; Normalizing attention probabilities across token dimensions using scores.softmax(dim=-1).; Multiplying attention probability weights by values tensor to get final contextual representations.

**Worked example:** Tracing PyTorch code: Given query tensor of shape (1, 3, 4) and d_k = 4, compute scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(4) yielding shape (1, 3, 3). Execute scores.masked_fill(mask == 0, -1e9) to set upper-triangular scores to -1e9. Compute p_attn = scores.softmax(dim=-1) where -1e9 entries become 0.0, and return torch.matmul(p_attn, value) of shape (1, 3, 4).

Files: `material/W02.S1/lesson/part_3/slides.pptx`, `notes.md` (the full narration), `student.html`

## References read

- [C1] Speech and Language Processing (3rd edition draft) — 3232 words
- [C2] Dive into Deep Learning, chapter 11: Attention Mechanisms and Transformers — 43845 words
- [C3] Attention Is All You Need — 6111 words
- [C4] The Annotated Transformer — 6810 words
- [C5] The Illustrated Transformer — 4154 words
