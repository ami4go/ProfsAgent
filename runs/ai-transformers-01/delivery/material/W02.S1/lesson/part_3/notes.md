# Part 3 of 3: Vectorized PyTorch Implementation of Scaled Dot-Product Attention

*Introduction to Transformer Architecture · Scaled dot-product self-attention and masking · Part 3 of 3 · about 10 min*

> Teaching video drafted by ProfsAgent from the course's references: check before sharing.

## Learning outcomes

- Implement vectorized batch scaled dot-product attention with causal masking efficiently using tensor operations in PyTorch.
- Tensor representations and shapes for query, key, and value matrices in batched operations.
- Matrix multiplication via torch.matmul and key transpositions with transpose(-2, -1).
- Applying causal mask efficiently using scores.masked_fill(mask == 0, -1e9).
- Normalizing attention probabilities across token dimensions using scores.softmax(dim=-1).
- Multiplying attention probability weights by values tensor to get final contextual representations.

## 3. Tensor Shapes for Batched Self-Attention (Example)

- Query & Key shape: (batch_size, seq_len, d_k)
- Value shape: (batch_size, seq_len, d_v)
- Batched operations across batch dimension

| Query (Q) | (batch_size, seq_len, d_k) | Token query vectors |
|---|---|---|
| Key (K) | (batch_size, seq_len, d_k) | Token key vectors |
| Value (V) | (batch_size, seq_len, d_v) | Token value vectors |
| Scores | (batch_size, seq_len, seq_len) | Pairwise compatibility matrix |

**Notes** (1.1 min · outcomes CO2.LO1 · sources [C2] [C5]): Welcome back! In our previous parts, we mastered the mathematical foundation of scaled dot-product attention and derived how causal masking prevents tokens from looking into the future. Now, in this final part, we answer a crucial engineering question: how do we implement this entire pipeline efficiently in PyTorch using vectorized tensor operations? In deep learning, we never process one sequence at a time in a loop. Instead, we bundle multiple sequences into batches. That means our query, key, and value matrices gain a batch dimension. Specifically, the query tensor has shape batch size, sequence length, and key dimension d k. The key tensor shares this exact shape of batch size, sequence length, and d k. The value tensor has shape batch size, sequence length, and value dimension d v. By structuring our data into three-dimensional tensors, PyTorch can run matrix operations for every sequence in the batch simultaneously on GPU hardware. Understanding these tensor dimensions is your key to reading and writing production-grade Transformer code without getting lost in shape errors.

## 4. Computing Scaled Attention Scores via Matrix Multiplication (Example)

- Transpose keys with key.transpose(-2, -1)
- Batch matrix multiply via torch.matmul
- Scale scores by dividing math.sqrt(d_k)

```python
d_k = query.size(-1)
# Swap last two dimensions of key tensor
key_T = key.transpose(-2, -1)
# Batched matrix multiplication & scaling
scores = torch.matmul(query, key_T) / math.sqrt(d_k)
```

**Notes** (1.2 min · outcomes CO2.LO1 · sources [C2] [C3]): Now that our tensors are shaped correctly, let's calculate the pairwise similarity scores between every query token and key token. Mathematically, we need to multiply the query matrix by the transpose of the key matrix. But in PyTorch, how do we transpose key vectors when there is a batch dimension in front? We use key dot transpose with negative two and negative one. Using negative indices targets the last two dimensions—sequence length and d k—swapping them regardless of how many batch dimensions exist before them. So a key tensor of shape batch size, sequence length, d k becomes batch size, d k, sequence length. Next, we use torch dot matmul to perform batch matrix multiplication. Multiplying shape batch size, sequence length, d k by batch size, d k, sequence length yields a scores tensor of shape batch size, sequence length, sequence length. Finally, we scale these scores by dividing by the square root of d k, which is extracted dynamically as query dot size at index negative one. This scaling prevents dot products from growing excessively large, keeping gradients stable during backpropagation.

## 5. Vectorized Causal Masking with masked_fill

- Mask shape: (1, seq_len, seq_len) lower-triangular
- Zero mask entries indicate forbidden positions
- scores.masked_fill(mask == 0, -1e9)

Raw Scaled Scores → Compare mask == 0 → Fill True with -1e9 → Causal Masked Scores

**Notes** (1.2 min · outcomes CO2.LO1 · sources [C2] [C3] [C4]): Once we have our scaled scores tensor, we must enforce causality so that token i cannot attend to any future token j where j is greater than i. In the previous part, we saw that masking conceptually sets future interaction entries to negative infinity. In PyTorch, we execute this efficiently using tensor broadcasting and the masked fill operation. We define a binary mask tensor, typically a lower-triangular matrix of ones with zeros in the upper-triangle. We then call scores dot masked fill, passing the condition mask equals zero and the fill value negative one e nine, representing negative one billion. PyTorch evaluates the boolean condition across all batch elements. Wherever the mask is zero—which corresponds to forbidden future tokens—the score value is instantly replaced with negative one billion. Why do we use negative one billion instead of actual negative infinity? Because negative one billion is a finite floating-point number that avoids numerical instability like NaN values during gradient computation, yet it is so large and negative that its exponential in the softmax function evaluates to exactly zero.

## 6. Softmax Normalization and Value Weighted Sum

- Softmax over key dimension: scores.softmax(dim=-1)
- -1e9 entries map to 0.0 attention weight
- Weighted sum output: torch.matmul(p_attn, value)

Masked Scores → Softmax(dim=-1) → Attention Weights (p_attn) → MatMul with Value Tensor

**Notes** (1.2 min · outcomes CO2.LO1 · sources [C2] [C3]): With our causal mask applied, we are ready to turn these raw, masked scores into probability distributions and compute our final contextual embeddings. First, we normalize the scores across the key tokens by calling scores dot softmax with dim equals negative one. Specifying dim equals negative one instructs PyTorch to compute softmax independently along the last dimension of the tensor. This means for each query token in every sequence of the batch, the attention weights across all key tokens sum to one. Crucially, any score that was filled with negative one billion becomes zero point zero after softmax, effectively severing any attention to future tokens. The output of this step, which we call p attn, has shape batch size, sequence length, sequence length. Finally, we multiply p attn by our value tensor using torch dot matmul. Multiplying p attn of shape batch size, sequence length, sequence length by value of shape batch size, sequence length, d v produces our final output tensor of shape batch size, sequence length, d v. Each token now holds a weighted sum of values from allowed past positions.

## 7. Step-by-Step PyTorch Code Execution Trace (Example)

- Input query shape: (1, 3, 4), d_k = 4
- MatMul & Scale yields (1, 3, 3) scores
- Masked Fill & Softmax upper triangle set to 0.0
- Output shape: (1, 3, 4) via torch.matmul

| 1. Transpose | key.transpose(-2, -1) | (1, 4, 3) | Last 2 dims swapped |
|---|---|---|---|
| 2. MatMul & Scale | torch.matmul(Q, K_T) / 2.0 | (1, 3, 3) | Unmasked scaled scores |
| 3. Masked Fill | scores.masked_fill(mask==0, -1e9) | (1, 3, 3) | Upper triangle is -1e9 |
| 4. Softmax | scores.softmax(dim=-1) | (1, 3, 3) | Upper triangle is 0.0 |
| 5. Value Product | torch.matmul(p_attn, value) | (1, 3, 4) | Final output representation |

**Notes** (1.3 min · outcomes CO2.LO1 · sources [C2] [C3]): Let's trace this entire vectorized pipeline step by step using concrete tensor dimensions from our example. Suppose our batch size is one, sequence length is three tokens, and d k is four. So our query, key, and value tensors each have shape one, three, four. First, transposing the key tensor with key dot transpose negative two, negative one changes its shape from one, three, four to one, four, three. Next, we multiply query of shape one, three, four by transposed key of shape one, four, three, and divide by the square root of four, which is two. This gives a scaled scores tensor of shape one, three, three. Then, we apply scores dot masked fill with mask equals zero setting score entries in the upper-triangular positions to negative one e nine. Applying scores dot softmax with dim equals negative one converts those negative one e nine entries into exactly zero point zero, while ensuring each row sums to one point zero. Finally, multiplying p attn of shape one, three, three by value of shape one, three, four yields our final contextual tensor of shape one, three, four. Every step cleanly preserves vectorization!

## 8. Common Pitfalls: Softmax Dimension and Transpose Indexing

- softmax(dim=-2) normalizes incorrectly across queries
- hardcoded transpose(1, 2) breaks on 4D tensors
- Use dim=-1 for key normalization
- Use transpose(-2, -1) for multi-head compatibility

**Notes** (1.2 min · outcomes CO2.LO1 · sources [C2]): Before we recap, let's highlight a subtle but critical misconception that trips up many developers when implementing attention in PyTorch. The first mistake is picking the wrong dimension for softmax, specifically using dim equals negative two instead of dim equals negative one. If you apply softmax along dim equals negative two, PyTorch normalizes down the columns across queries rather than across keys! That means the attention weights for a single query across all key tokens won't sum to one, destroying the mathematical probability distribution. The second common mistake is hardcoding transpose dimensions as transpose one, two instead of transpose negative two, negative one. While transpose one, two works for three-dimensional tensors of shape batch, seq, d k, it silently breaks when you expand to multi-head attention with four-dimensional tensors of shape batch, heads, seq, d k! Using negative indices negative two and negative one ensures your transposition always operates on the last two spatial dimensions regardless of how many leading batch or head dimensions you have. Always double-check your softmax dimension and use negative indexing for robust code.

## 9. What you learned (Summary)

- In this final part, we translated scaled dot-product attention and causal masking into efficient, batched PyTorch code using vectorized tensor operations.
- We saw how torch.matmul, transpose(-2, -1), masked_fill, and softmax(dim=-1) come together to process entire sequence batches in parallel.
- Master these PyTorch tensor patterns, and you will have the foundation to build complete multi-head Transformer architectures.

**Notes** (0.5 min · outcomes CO2.LO1): In this final part, we translated scaled dot-product attention and causal masking into efficient, batched PyTorch code using vectorized tensor operations. We saw how torch.matmul, transpose(-2, -1), masked_fill, and softmax(dim=-1) come together to process entire sequence batches in parallel. Master these PyTorch tensor patterns, and you will have the foundation to build complete multi-head Transformer architectures.

## 10. Quiz 1 of 3 (Check)


**Why is key.transpose(-2, -1) preferred over key.transpose(1, 2) when implementing attention key transposition in PyTorch?**

A. It automatically performs scaling by the square root of d_k during transposition.
B. It operates on the last two dimensions, ensuring compatibility with both 3D and 4D multi-head tensors.
C. It replaces masked future positions with negative infinity without requiring masked_fill.
D. It transposes the batch dimension with the feature dimension to speed up GPU memory access.

*Answer: B. It operates on the last two dimensions, ensuring compatibility with both 3D and 4D multi-head tensors.. Using negative indexing transpose(-2, -1) dynamically selects the last two dimensions (sequence length and d_k), making the code work seamlessly for 3D tensors (batch, seq, d_k) and 4D multi-head tensors (batch, heads, seq, d_k). Hardcoding transpose(1, 2) fails on 4D tensors because index 1 is the head dimension, not sequence length.*

**Notes** (0.7 min · outcomes CO2.LO1): Quiz question 1. Why is key.transpose(-2, -1) preferred over key.transpose(1, 2) when implementing attention key transposition in PyTorch? Pause the video and choose your answer.

## 11. Answer 1: B (Answer)

- B. It operates on the last two dimensions, ensuring compatibility with both 3D and 4D multi-head tensors.
- Using negative indexing transpose(-2, -1) dynamically selects the last two dimensions (sequence length and d_k), making the code work seamlessly for 3D tensors (batch, seq, d_k) and 4D multi-head tensors (batch, heads, seq, d_k).
- Hardcoding transpose(1, 2) fails on 4D tensors because index 1 is the head dimension, not sequence length.

**Notes** (0.7 min · outcomes CO2.LO1): The answer is B: It operates on the last two dimensions, ensuring compatibility with both 3D and 4D multi-head tensors.. Using negative indexing transpose(-2, -1) dynamically selects the last two dimensions (sequence length and d_k), making the code work seamlessly for 3D tensors (batch, seq, d_k) and 4D multi-head tensors (batch, heads, seq, d_k). Hardcoding transpose(1, 2) fails on 4D tensors because index 1 is the head dimension, not sequence length.

## 12. Quiz 2 of 3 (Check)


**In a batched attention operation, given a Query tensor of shape (1, 3, 4), Key tensor of shape (1, 3, 4), and Value tensor of shape (1, 3, 4), what are the shapes of the attention weights p_attn and the final output tensor respectively?**

A. p_attn has shape (1, 4, 4) and final output has shape (1, 3, 3).
B. p_attn has shape (1, 3, 4) and final output has shape (1, 3, 4).
C. p_attn has shape (1, 3, 3) and final output has shape (1, 3, 4).
D. p_attn has shape (1, 3, 3) and final output has shape (1, 4, 4).

*Answer: C. p_attn has shape (1, 3, 3) and final output has shape (1, 3, 4).. torch.matmul(query, key.transpose(-2, -1)) multiplies (1, 3, 4) by (1, 4, 3) yielding p_attn of shape (1, 3, 3). Then torch.matmul(p_attn, value) multiplies (1, 3, 3) by (1, 3, 4) producing a final output tensor of shape (1, 3, 4). Option 1 incorrectly assumes p_attn retains the input embedding shape.*

**Notes** (0.7 min · outcomes CO2.LO1): Quiz question 2. In a batched attention operation, given a Query tensor of shape (1, 3, 4), Key tensor of shape (1, 3, 4), and Value tensor of shape (1, 3, 4), what are the shapes of the attention weights p_attn and the final output tensor respectively? Pause the video and choose your answer.

## 13. Answer 2: C (Answer)

- C. p_attn has shape (1, 3, 3) and final output has shape (1, 3, 4).
- torch.matmul(query, key.transpose(-2, -1)) multiplies (1, 3, 4) by (1, 4, 3) yielding p_attn of shape (1, 3, 3).
- Then torch.matmul(p_attn, value) multiplies (1, 3, 3) by (1, 3, 4) producing a final output tensor of shape (1, 3, 4).
- Option 1 incorrectly assumes p_attn retains the input embedding shape.

**Notes** (0.7 min · outcomes CO2.LO1): The answer is C: p_attn has shape (1, 3, 3) and final output has shape (1, 3, 4).. torch.matmul(query, key.transpose(-2, -1)) multiplies (1, 3, 4) by (1, 4, 3) yielding p_attn of shape (1, 3, 3). Then torch.matmul(p_attn, value) multiplies (1, 3, 3) by (1, 3, 4) producing a final output tensor of shape (1, 3, 4). Option 1 incorrectly assumes p_attn retains the input embedding shape.

## 14. Quiz 3 of 3 (Check)


**What happens if scores.softmax(dim=-2) is used instead of scores.softmax(dim=-1) when computing attention weights?**

A. Future positions will retain positive values instead of becoming 0.0 after masking.
B. Attention probabilities are normalized across queries per key token instead of across key tokens per query token.
C. PyTorch raises a runtime shape mismatch error because dim=-2 is an invalid axis index.
D. The softmax values will all become negative one billion (-1e9).

*Answer: B. Attention probabilities are normalized across queries per key token instead of across key tokens per query token.. dim=-1 normalizes along the last axis (keys for each query), creating valid probability distributions across key tokens for each input query. Using dim=-2 normalizes along the query axis across queries for each key token, breaking the proper attention distribution per token.*

**Notes** (0.7 min · outcomes CO2.LO1): Quiz question 3. What happens if scores.softmax(dim=-2) is used instead of scores.softmax(dim=-1) when computing attention weights? Pause the video and choose your answer.

## 15. Answer 3: B (Answer)

- B. Attention probabilities are normalized across queries per key token instead of across key tokens per query token.
- dim=-1 normalizes along the last axis (keys for each query), creating valid probability distributions across key tokens for each input query.
- Using dim=-2 normalizes along the query axis across queries for each key token, breaking the proper attention distribution per token.

**Notes** (0.7 min · outcomes CO2.LO1): The answer is B: Attention probabilities are normalized across queries per key token instead of across key tokens per query token.. dim=-1 normalizes along the last axis (keys for each query), creating valid probability distributions across key tokens for each input query. Using dim=-2 normalizes along the query axis across queries for each key token, breaking the proper attention distribution per token.

## References

- [C2] Dive into Deep Learning, chapter 11: Attention Mechanisms and Transformers (2023). https://d2l.ai/chapter_attention-mechanisms-and-transformers/index.html
- [C3] Attention Is All You Need (2017). https://arxiv.org/abs/1706.03762
- [C4] The Annotated Transformer (2022). https://nlp.seas.harvard.edu/annotated-transformer/
- [C5] The Illustrated Transformer (2018). https://jalammar.github.io/illustrated-transformer/
