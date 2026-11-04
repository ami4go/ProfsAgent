# Part 2 of 3: Causal Masking and Step-by-Step Matrix Computation

*Introduction to Transformer Architecture · Scaled dot-product self-attention and masking · Part 2 of 3 · about 10 min*

> Teaching video drafted by ProfsAgent from the course's references: check before sharing.

## Learning outcomes

- Perform manual matrix calculations for scaled dot-product attention with causal masking to preserve the autoregressive property.
- The autoregressive constraint in decoders: preventing attention to future token positions.
- Constructing a lower-triangular causal mask matrix.
- Masking illegal future positions by substituting score values with -infinity prior to softmax.
- Softmax behavior on -infinity inputs resulting in exact zero attention probability weights.
- Step-by-step matrix calculation of attention output from masked probabilities and Value vectors.

## 3. Why Decoders Require Causal Masking

- Autoregressive generation generates tokens sequentially
- Preventing leftward information flow
- Unmasked self-attention leaks future context

Token t Query → Attend to tokens 1 to t → Block tokens t+1 to T → Next-token prediction

**Notes** (1 min · outcomes CO2.LO1 · sources [C3] [C4]): In part one, we mastered the core mathematics of scaled dot-product attention, seeing how queries and keys interact across an entire sequence simultaneously. But that poses an immediate dilemma when we build an autoregressive decoder. In language generation, text unfolds one token at a time from left to right. When the model predicts the token at position two, it cannot be allowed to peek at position three or four. If we simply compute standard bidirectional self-attention as we did earlier, every position will look ahead into the future representations, trivializing training and breaking the autoregressive contract. We call this unwanted leak leftward information flow. To fix this while retaining parallel GPU computation during training, we must enforce a causal constraint. Each position in the decoder should only be allowed to attend to positions up to and including itself. Let us explore the mechanism that enforces this boundary: the causal mask.

## 4. Constructing the Pre-Softmax Causal Mask (Example)

- Lower-triangular structure
- Valid positions retained
- Illegal future positions set to -infinity
- Applied directly to raw scaled scores

| Pos 1 | Keep score | Set to -inf |
|---|---|---|
| Pos 2 | Keep score | Keep score |

**Notes** (1.1 min · outcomes CO2.LO1 · sources [C2] [C3] [C4]): How do we structurally prohibit attention to future tokens without throwing away matrix parallelism? We construct a causal mask matrix matching the shape of our query-key dot products. Consider a sequence of length T. The allowed interactions form a lower-triangular matrix, including the main diagonal. For row index i and column index j, if j is less than or equal to i, the token is attending to past positions or itself, which is entirely legal. However, whenever j exceeds i, that represents an illegal query into the future. Instead of dropping rows or running sequential loops, we intercept the raw attention scores right after dividing query times key transpose by the square root of d k, but strictly before evaluating softmax. At every illegal position where j is greater than i, we overwrite the score with negative infinity. As you will see next, setting these values to negative infinity before exponentiation is mathematically crucial for preserving valid probability distributions.

## 5. Softmax Behavior with Negative Infinity

- Exponentiation of -infinity approaches zero
- Zero numerator yields zero weight
- Remaining probabilities renormalize cleanly
- Preserves strict probability distribution

**Notes** (1 min · outcomes CO2.LO1 · sources [C2] [C3] [C4]): Let us examine why negative infinity is the exact tool we need. Recall that the softmax function operates row by row. For a given score, softmax takes e raised to that score and divides it by the sum of e raised to each score across the row. When we substitute negative infinity into an illegal future entry, e raised to negative infinity evaluates strictly to zero. Consequently, that illegal connection contributes zero to the row's denominator sum, and its numerator is zero, driving the resulting attention probability weight exactly to zero. Meanwhile, the legal positions with finite real scores compute their usual exponential values. Because the denominator now sums exclusively over the legal positions, the surviving entries automatically renormalize so that their attention probabilities sum precisely to one. This guarantees that future tokens exert absolutely zero influence on the current token, cleanly preserving autoregression without altering the core attention architecture.

## 6. Worked Example: Calculating Masked Attention Weights (Example)

- Raw scaled scores: [[2.0, 4.0], [2.0, 4.0]]
- Masked scores: [[2.0, -inf], [2.0, 4.0]]
- Row 1 softmax: [1.0, 0.0]
- Row 2 softmax: [0.12, 0.88]

| Scaled QK^T | [2.0, 4.0] | [2.0, 4.0] |
|---|---|---|
| Apply Mask | [2.0, -inf] | [2.0, 4.0] |
| Softmax Weights | [1.0, 0.0] | [0.12, 0.88] |

**Notes** (1.3 min · outcomes CO2.LO1 · sources [C3] [C5]): Now let us work through our example step by step using real numbers. Suppose we process a two-token sequence where the query-key dot products divided by the square root of d k give a two-by-two matrix with row one having scores two point zero and four point zero, and row two also having two point zero and four point zero. Position one cannot look at position two. So we apply our causal mask to entry row one, column two, turning four point zero into negative infinity. Row two is completely legal, so it stays two point zero and four point zero. Now we compute the row-wise softmax. For row one, e to the second power divided by e to the second power plus e to negative infinity simplifies to e squared over e squared plus zero, which equals exactly one point zero for token one, and zero point zero for token two. For row two, both positions are valid: e squared is approximately seven point three nine, and e to the fourth is approximately fifty-four point six. Normalizing gives twelve hundredths for position one and eighty-eight hundredths for position two.

## 7. Worked Example: Output from Value Vectors (Example)

- Value matrix V: [[1.0, 0.0], [0.0, 1.0]]
- Row 1: 1.0 * v1 + 0.0 * v2
- Row 2: 0.12 * v1 + 0.88 * v2
- Attention output: [[1.0, 0.0], [0.12, 0.88]]

**Notes** (1 min · outcomes CO2.LO1 · sources [C2] [C3]): With the attention weight matrix established as row one having one point zero and zero point zero, and row two having twelve hundredths and eighty-eight hundredths, the final step is multiplying this matrix by our Value matrix V. Let V have row one as one point zero, zero point zero, and row two as zero point zero, one point zero. For the first token's output representation, we take one point zero times vector one plus zero point zero times vector two. That yields the vector one point zero, zero point zero. Notice that position one's output contains absolutely no information from the second token's value vector. For the second token, the output is twelve hundredths times vector one plus eighty-eight hundredths times vector two, producing the vector twelve hundredths, eighty-eight hundredths. Position two blends both tokens according to its learned attention scores. We have successfully maintained the autoregressive constraint through straightforward matrix arithmetic.

## 8. A Fatal Misconception: Post-Softmax Zeroing (Example)

- Pre-softmax mask: injects -infinity
- Post-softmax zeroing: zeros raw probabilities
- Violation: row sum falls below 1.0
- Distorts output vector scale

| Pre-Softmax (-inf) | [1.0, 0.0] | 1.0 (Valid) |
|---|---|---|
| Post-Softmax Zero | [0.12, 0.0] | 0.12 (Invalid) |

**Notes** (1 min · outcomes CO2.LO1 · sources [C2] [C3]): A common mistake when students implement causal attention is trying to zero out illegal positions after computing the softmax rather than before. Let us see why that breaks the model. In our example, if you took the unmasked softmax of row one with scores two point zero and four point zero, the resulting weights would be roughly twelve hundredths and eighty-eight hundredths. If you then manually zeroed position two to prevent cheating, row one would be twelve hundredths and zero point zero. The probabilities now sum to only twelve hundredths, not one point zero. When multiplied by the values, the output vector's magnitude collapses to twelve percent of its expected norm. Softmax represents a convex combination of value vectors. By setting pre-softmax logits to negative infinity instead, the remaining legal weights properly expand and renormalize to sum to one point zero, preserving both gradient stability and numerical fidelity.

## 9. What you learned (Summary)

- In this part, we saw how causal masking enforces the autoregressive constraint in decoders by substituting negative infinity into future score positions before softmax.
- This guarantees that illegal connections evaluate to zero probability while surviving tokens properly renormalize to sum to one.
- Multiplying these masked weights by the Value matrix yields causal output representations in parallel.

**Notes** (0.5 min · outcomes CO2.LO1): In this part, we saw how causal masking enforces the autoregressive constraint in decoders by substituting negative infinity into future score positions before softmax. This guarantees that illegal connections evaluate to zero probability while surviving tokens properly renormalize to sum to one. Multiplying these masked weights by the Value matrix yields causal output representations in parallel.

## 10. Quiz 1 of 3 (Check)


**Why is the causal mask applied to the attention scores prior to the softmax operation rather than afterward?**

A. To enable matrix multiplication with Value vectors of differing inner dimensions.
B. To ensure illegal connections become zero while remaining legal positions renormalize to sum to 1.0.
C. To convert the attention score matrix into a symmetric positive-definite matrix.
D. To avoid computing dot products between query vectors and future key vectors.

*Answer: B. To ensure illegal connections become zero while remaining legal positions renormalize to sum to 1.0.. Injecting negative infinity before softmax ensures e^(-inf) = 0, which makes future weights zero and renormalizes the remaining legal positions so their sum equals 1.0. Zeroing weights post-softmax leaves a row sum strictly less than 1.0, distorting representation magnitudes.*

**Notes** (0.7 min · outcomes CO2.LO1): Quiz question 1. Why is the causal mask applied to the attention scores prior to the softmax operation rather than afterward? Pause the video and choose your answer.

## 11. Answer 1: B (Answer)

- B. To ensure illegal connections become zero while remaining legal positions renormalize to sum to 1.0.
- Injecting negative infinity before softmax ensures e^(-inf) = 0, which makes future weights zero and renormalizes the remaining legal positions so their sum equals 1.0.
- Zeroing weights post-softmax leaves a row sum strictly less than 1.0, distorting representation magnitudes.

**Notes** (0.7 min · outcomes CO2.LO1): The answer is B: To ensure illegal connections become zero while remaining legal positions renormalize to sum to 1.0.. Injecting negative infinity before softmax ensures e^(-inf) = 0, which makes future weights zero and renormalizes the remaining legal positions so their sum equals 1.0. Zeroing weights post-softmax leaves a row sum strictly less than 1.0, distorting representation magnitudes.

## 12. Quiz 2 of 3 (Check)


**For a 3-token sequence, after scaling Q K^T, the first row of scores is [3.0, 5.0, 1.0]. What are the masked attention weights for token 1?**

A. [0.33, 0.33, 0.33]
B. [0.12, 0.0, 0.0]
C. [1.0, 0.0, 0.0]
D. [0.0, 0.88, 0.12]

*Answer: C. [1.0, 0.0, 0.0]. Token 1 at position 1 can only attend to position 1. Positions 2 and 3 are set to -infinity, resulting in masked scores [3.0, -inf, -inf]. Softmax yields e^3 / (e^3 + 0 + 0) = 1.0 for position 1 and 0.0 for positions 2 and 3.*

**Notes** (0.7 min · outcomes CO2.LO1): Quiz question 2. For a 3-token sequence, after scaling Q K^T, the first row of scores is [3.0, 5.0, 1.0]. What are the masked attention weights for token 1? Pause the video and choose your answer.

## 13. Answer 2: C (Answer)

- C. [1.0, 0.0, 0.0]
- Token 1 at position 1 can only attend to position 1.
- Positions 2 and 3 are set to -infinity, resulting in masked scores [3.0, -inf, -inf].
- Softmax yields e^3 / (e^3 + 0 + 0) = 1.0 for position 1 and 0.0 for positions 2 and 3.

**Notes** (0.7 min · outcomes CO2.LO1): The answer is C: [1.0, 0.0, 0.0]. Token 1 at position 1 can only attend to position 1. Positions 2 and 3 are set to -infinity, resulting in masked scores [3.0, -inf, -inf]. Softmax yields e^3 / (e^3 + 0 + 0) = 1.0 for position 1 and 0.0 for positions 2 and 3.

## 14. Quiz 3 of 3 (Check)


**What happens to the output representation if a developer sets illegal future weights to 0.0 after running standard softmax?**

A. The model crashes due to a division by zero error in the dot-product computation.
B. The attention weights fail to sum to 1.0, causing an unintended shrinkage of the output vector norm.
C. The causal mask is inverted, causing tokens to only attend to future positions.
D. The Value matrix becomes singular and cannot be inverted during backpropagation.

*Answer: B. The attention weights fail to sum to 1.0, causing an unintended shrinkage of the output vector norm.. If probabilities are zeroed after softmax without renormalization, the row sum equals only the probability assigned to past tokens, which is strictly less than 1.0. This artificially dampens the scale of the resulting output vector.*

**Notes** (0.7 min · outcomes CO2.LO1): Quiz question 3. What happens to the output representation if a developer sets illegal future weights to 0.0 after running standard softmax? Pause the video and choose your answer.

## 15. Answer 3: B (Answer)

- B. The attention weights fail to sum to 1.0, causing an unintended shrinkage of the output vector norm.
- If probabilities are zeroed after softmax without renormalization, the row sum equals only the probability assigned to past tokens, which is strictly less than 1.0.
- This artificially dampens the scale of the resulting output vector.

**Notes** (0.7 min · outcomes CO2.LO1): The answer is B: The attention weights fail to sum to 1.0, causing an unintended shrinkage of the output vector norm.. If probabilities are zeroed after softmax without renormalization, the row sum equals only the probability assigned to past tokens, which is strictly less than 1.0. This artificially dampens the scale of the resulting output vector.

## References

- [C2] Dive into Deep Learning, chapter 11: Attention Mechanisms and Transformers (2023). https://d2l.ai/chapter_attention-mechanisms-and-transformers/index.html
- [C3] Attention Is All You Need (2017). https://arxiv.org/abs/1706.03762
- [C4] The Annotated Transformer (2022). https://nlp.seas.harvard.edu/annotated-transformer/
- [C5] The Illustrated Transformer (2018). https://jalammar.github.io/illustrated-transformer/
