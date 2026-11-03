# Simulation coverage of IIIT-D's courses (generated)

Made by `python scripts/sims.py coverage`: every weekly topic of the 471 courses in our course data (9,784 topic lines) labelled with a simulation type (docs/09 §3) or "none" (better taught another way).

**How far to trust it:**
- **Model:** sentence-transformers/all-MiniLM-L6-v2 on the CPU, with no AI calls. Settings: course name used, top-3 prototypes, threshold 0.20, margin -0.09.
- **Accuracy:** checked against 165 hand-labelled topics (`simulations/classifier/labels.tsv`, labelled by Claude, to be reviewed by Amit). It was right on **75%** of them, and **73% cross-validated** (calibrated on 4/5 of the labels, scored on the rest).
- **Topics that should get no simulation:** it said "none" for 18 of 20.
- **Topics that should get a simulation:** it gave one that fits for 50 of 81.
- **Use:** treat the shares below as estimates that rank the work, not exact counts.

## Per department

| Department | Topics | With a simulation type | Most common types (share of the department's topics) |
|---|---|---|---|
| CSE | 2657 | 65% | 5 networks 22%, 1 step-through process 12%, 6 machines inside 7%, 9 3d 5%, 8 data explorer 4%, 7 live code 4%, 11 experiments on yourself 3%, 4 chance 3%, 2 parameter explorer 2%, 10 decisions 2%, 12 maps 0%, 3 systems over time 0% |
| ECE | 1701 | 60% | 6 machines inside 13%, 2 parameter explorer 10%, 5 networks 8%, 9 3d 7%, 3 systems over time 6%, 11 experiments on yourself 5%, 4 chance 4%, 1 step-through process 3%, 8 data explorer 2%, 7 live code 1%, 10 decisions 1% |
| MTH | 1665 | 48% | 2 parameter explorer 12%, 3 systems over time 7%, 9 3d 7%, 4 chance 7%, 8 data explorer 5%, 6 machines inside 3%, 5 networks 3%, 11 experiments on yourself 2%, 1 step-through process 2%, 7 live code 2%, 10 decisions 0%, 12 maps 0% |
| DES | 1053 | 25% | 9 3d 14%, 11 experiments on yourself 5%, 10 decisions 3%, 4 chance 1%, 5 networks 1%, 7 live code 0%, 1 step-through process 0%, 6 machines inside 0%, 8 data explorer 0%, 2 parameter explorer 0% |
| SSH | 644 | 27% | 12 maps 17%, 10 decisions 6%, 5 networks 2%, 11 experiments on yourself 1%, 8 data explorer 1%, 7 live code 0%, 9 3d 0%, 4 chance 0% |
| BIO | 526 | 74% | 8 data explorer 22%, 3 systems over time 17%, 5 networks 15%, 9 3d 9%, 1 step-through process 3%, 4 chance 3%, 7 live code 2%, 11 experiments on yourself 2%, 10 decisions 1%, 2 parameter explorer 0%, 6 machines inside 0% |
| SOC | 420 | 24% | 12 maps 17%, 5 networks 3%, 9 3d 2%, 10 decisions 1%, 11 experiments on yourself 1% |
| ENT | 365 | 18% | 10 decisions 14%, 4 chance 2%, 5 networks 1%, 2 parameter explorer 1%, 8 data explorer 0% |
| ECO | 286 | 80% | 10 decisions 31%, 8 data explorer 19%, 2 parameter explorer 14%, 4 chance 5%, 3 systems over time 4%, 11 experiments on yourself 3%, 12 maps 1%, 6 machines inside 1%, 1 step-through process 1%, 5 networks 0%, 9 3d 0% |
| PSY | 160 | 52% | 11 experiments on yourself 46%, 10 decisions 2%, 4 chance 1%, 9 3d 1%, 2 parameter explorer 1%, 12 maps 1%, 8 data explorer 1%, 5 networks 1% |
| AI | 154 | 58% | 8 data explorer 27%, 2 parameter explorer 16%, 5 networks 5%, 11 experiments on yourself 4%, 4 chance 3%, 9 3d 3%, 1 step-through process 1%, 10 decisions 1% |
| MGT | 87 | 10% | 10 decisions 6%, 5 networks 5% |
| COM | 36 | 3% | 10 decisions 3% |
| ESC | 19 | 0% |  |
| ENG | 11 | 0% |  |
| **All** | **9784** | **51%** | |

## Per type, all departments

| Type | Topics | Example topics |
|---|---|---|
| Step-through process | 424 | Batchsize, Stepsize, Learning Rate Scheduler, Custom Callbacks (AI502); DNA Technology and Genomics (BIO101); DNA Structure and Replication (BIO102); tranferable elements in eukaryotic genome (BIO214) |
| Parameter explorer | 518 | Linear Regression: closed-form solution and gradient-based training (AI201); Loss functions, Gradient Descent (AI501); Parametric/Non-Parametric Learning (AI501); Lagrange Multiplier & Primal/Dual Problem (AI501) |
| Systems over time | 320 | Cellular Respiration: Harvesting Chemical Energy (BIO101); Enzymes and Metabolism (BIO102); Calculus and Thermodynamics/Statistical physics (BIO211); Enzyme kinetics and Allostery, Glucose metabolism (BIO211) |
| Chance and crowds | 315 | Bias-Variance Trade-off (AI501); Overflow (AI501); Expectation-Maximization (AI501); Autoregression (AR) and Normalizing Flows (AI502) |
| Networks and graphs | 890 | Complexity of Machine Learning Alogirthms (AI501); From Multi-layer to Multi-block Models (AI502); Dynamic neural networks (AI502); Regulation of Gene Expression (BIO102) |
| Machines inside | 454 | bang-bang switching (BIO525); Big –Oh notation (CSE102); Stacks, Queues using linked lists (CSE102); Refreshing sequential circuits (CSE112) |
| Live code and query sandbox | 174 | recursive techniques (BIO522); application of dynamic programming (BIO522); Denovo assembly (BIO541); Introduction to Python and R (BIO551A) |
| Data explorer | 447 | Unsupervised Learning (AI201); Supervised Learning - I (AI501); Linear and Logistic Regression (AI501); ML Model Evaluation (AI501) |
| 3D and spatial models | 562 | 1D/2D/3D CNNs (AI502); Model Compression: Structural vs Non-structural Compression (AI502); 1D/2D/3D CNNs (AI203); The Structure aud Function of Macromolecules (BIO101) |
| Decisions, games and role-play | 291 | Ethics, Safety, Bias & Robustness in DL Models (AI502); Biomedical Decision Making - Cognitive Models (BIO222); Biomedical Decision Making - AI Augmented Clinical Decision Support (BIO222); Entrepreneurship (BIO544) |
| Experiments on yourself | 376 | Margin Perceptron Algorithm and its link to SVM (AI501); Time and Space complexity (AI501); Receptive field, Padding, Stride, and Dilation (AI502); Wasserstein and Conditional GANs (AI502) |
| Maps, timelines and arguments | 186 | MAP (CSE558); Schema Matching and Mapping Algorithms (CSE656); Spatial Dependence and Spatial Heterogeneity (ECO324); Map between varieties (MTH561) |
| none: better taught another way | 4827 | Examples may include MSE, BCE, and gradient-based optimization (AI201); FAT Aspects of ML and Industry Lecture (AI201); Introduction to Machine Learning (ML) (AI501); Learning Problems and Application (AI501) |
