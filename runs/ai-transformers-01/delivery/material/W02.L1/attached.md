# Your material for W02.L1: Scaled dot-product self-attention and masking

*Read 1 attachment(s); made 2026-11-05 03:14*

- [P1] attention_lookup.pptx (pptx, 9579 characters)

## Summary

The lecture material introduces the concept of attention as an architectural solution to the recurrent neural network (RNN) information bottleneck, where a single hidden state compresses the entire sequence past. It explains the mechanics of attention using the metaphor of a soft, differentiable dictionary lookup involving query, key, and value vectors. The slides contrast scoring functions, detailing both unscaled dot-product scoring and Bahdanau additive scoring. They demonstrate how raw scores are transformed into a probability distribution over keys using softmax, and how values are subsequently aggregated into a context vector. An illustrative English-to-French toy alignment and a step-by-step numerical hand calculation walk students through the computation of attention weights and the resulting context vector. Finally, the material contrasts differentiable soft alignment with non-differentiable hard alignment, highlighting why soft attention enables end-to-end gradient-based training.

- Attention resolves the sequential RNN bottleneck by allowing direct access to all token positions.
- The attention mechanism functions as a differentiable soft lookup using queries (what is sought), keys (what is offered), and values (content retrieved).
- Compatibility scoring can be computed via dot-product ($q \cdot k$) or Bahdanau additive scoring ($v_a^T \tanh(W_a q + U_a k)$).
- Softmax normalises raw compatibility scores into non-negative attention weights that sum to 1.
- The context vector is formed as a convex combination (weighted sum) of value vectors.
- Soft alignment is smooth and differentiable, enabling backpropagation, unlike hard alignment which requires discrete selection.
- Attention heatmaps visualise token relevance, though learned weights do not guarantee true linguistic alignment.

## Gap check (outcomes of this lecture)

| Outcome | AI | Local model | What to add |
|---|---|---|---|
| CO2.LO1 | partly | covered (0.582) | The current material covers only unscaled vector dot-product attention and Bahdanau additive attention for cross-attention. It lacks: (1) the division by $\sqrt{d_k}$ in scaled dot-product attention, (2) the full matrix formulation for self-attention ($Q K^T / \sqrt{d_k}$), (3) vectorised PyTorch implementation, and (4) causal masking for autoregressive decoding. |

## Statements to check

- Mismatch between attached slide deck and syllabus lecture: The deck attached is from Week 1 (W01.S2, 'Attention as a soft lookup: queries, keys and values', tagged with CO1.LO2), whereas the scheduled lecture is W02.L1 ('Scaled dot-product self-attention and masking', mapped to CO2.LO1). As a result, core Level-4 topics like the $\sqrt{d_k}$ scaling derivation, matrix self-attention, PyTorch code, and causal masking are completely missing from the deck.

## Quiz

1. What primary limitation of recurrent neural networks (RNNs) does the attention mechanism resolve? *[[P1] slide 3]*
   - A. Compressing the entire sequence history into a single fixed-size hidden state that dilutes long-range dependencies
   - B. The inability to train on continuous vector representations using backpropagation through time
   - C. The excessive GPU memory requirement of maintaining query and key projection matrices
   - D. A strict requirement that input sequences and output sequences must have identical lengths
2. In the attention lookup framework, what role does a key vector ($k_i$) play relative to a query vector ($q$)? *[[P1] slide 4, slide 5]*
   - A. It represents the stored features of an item used to measure compatibility with what the query seeks
   - B. It specifies the information the current token actively seeks to extract from other positions
   - C. It serves as the final output representation passed directly to the subsequent transformer layer
   - D. It acts as a static, non-learnable positional mask that zeroes out future tokens
3. How is the Bahdanau additive attention score computed between a query vector $q$ and a key vector $k_i$? *[[P1] slide 6, slide 9]*
   - A. score = $v_a^T \tanh(W_a q + U_a k_i)$
   - B. score = $q^T k_i / \sqrt{d_k}$
   - C. score = $\text{softmax}(W_a q \cdot U_a k_i)$
   - D. score = $\sigma(v_a^T (q + k_i))$
4. Given query $q=[1, 0]$ and keys $k_1=[1, 1]$, $k_2=[0, 1]$, and $k_3=[-1, 0]$ with dot-product scoring, what are the raw compatibility scores prior to softmax? *[[P1] slide 11]*
   - A. 1, 0, -1
   - B. 2, 1, 0
   - C. 0.665, 0.245, 0.090
   - D. 1, 1, -1
5. Why is soft attention preferred over hard attention during neural network training? *[[P1] slide 14, slide 15]*
   - A. Soft attention yields a smooth, weighted sum that is fully differentiable for gradient descent
   - B. Soft attention uses a non-differentiable argmax function that speeds up matrix operations
   - C. Soft attention strictly constrains the model to attend to exactly one source token at a time
   - D. Soft attention guarantees that the resulting alignments match human linguistic rules

### Answers

1. A — Slide 3 explicitly notes that RNNs force all past sequence information into a single fixed-size hidden state, creating an information bottleneck and causing vanishing gradients over long distances. Inability to train with backpropagation is false because RNNs are trained via backpropagation through time.
2. A — Slides 4 and 5 define the query as what is sought, the key as the stored item offered for matching, and the value as the content retrieved. Specifying what the current token seeks describes the query, not the key.
3. A — Slides 6 and 9 present the corrected Bahdanau additive scoring formula as $v_a^T \tanh(W_a q + U_a k_i)$, where separate projection matrices $W_a$ and $U_a$ project the query and key before applying a tanh non-linearity and a dot product with $v_a$. Option 1 describes scaled dot-product attention.
4. A — Computing dot products gives: $q \cdot k_1 = 1(1) + 0(1) = 1$; $q \cdot k_2 = 1(0) + 0(1) = 0$; $q \cdot k_3 = 1(-1) + 0(0) = -1$. The values 0.665, 0.245, 0.090 are the post-softmax weights, not the raw scores.
5. A — Slides 14 and 15 emphasize that soft attention produces a differentiable convex combination of values, enabling standard backpropagation, whereas hard alignment makes a discrete choice (e.g. argmax) and is non-differentiable. Attending to exactly one token describes hard alignment.

## Ideas to enrich it

- **example** (Scaling factor explanation): Provide a mathematical justification showing that when elements of $q$ and $k$ are independent random variables with mean 0 and variance 1, their dot product has variance $d_k$, demonstrating how division by $\sqrt{d_k}$ prevents softmax saturation and vanishing gradients.
- **figure** (Causal masking): Add a visual diagram of an upper-triangular mask matrix containing $-\infty$ above the diagonal, showing how adding this mask prior to softmax sets post-softmax attention weights for future positions to 0.
- **activity** (Vectorised PyTorch implementation): Include a code snippet and student fill-in-the-blank exercise implementing `scaled_dot_product_attention(Q, K, V, mask=None)` using `torch.matmul`, `math.sqrt(d_k)`, `masked_fill`, and `torch.softmax`.
- **check question** (Masking implementation): Add a check question asking: 'Why do we fill masked positions with $-\infty$ (or $-1e9$) before softmax rather than zeroing out the attention weights after softmax?' to test understanding of probability normalization.
