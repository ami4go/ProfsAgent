# ML1: Machine Learning (CSE1007)

App course "ML-1: Machine Learning", run `app-machine-learning-01`. Made by the ProfsAgent pipeline calling Gemini 3.6 Flash, with automatic fallbacks when Gemini timed out or ran out of quota (listed below).
Both courses started from the same 14-field form. Saved 12 Nov 2026.

## Files

| File | What it is |
|---|---|
| `ML1_course_description.pdf` | Course description in the official IIIT-D CSE course template (same as the app's PDF download) |
| `ML1_course_design.pdf` | The full course design: assumptions, COs and LOs, weekly plan, assessment, references, CO–PO matrix, validation report, rationales |
| `slides/` | Slides for the backpropagation topic (.pptx with speaker notes, and a PDF copy) |

## Backpropagation lectures

| Lecture | Topic | Minutes | Slides | Files |
|---|---|---|---|---|
| W06.L3 | Matrix Vectorization and Backpropagation Calculus | 30 | 10 | `slides/ML1_W06.L3_slides.pptx`, `slides/ML1_W06.L3_slides.pdf` |
| W07.L1 | Matrix Vectorization and Backpropagation Calculus | 60 | 14 | `slides/ML1_W07.L1_slides.pptx`, `slides/ML1_W07.L1_slides.pdf` |

## Models that did the work (count of AI calls)

| Stage | Model | Calls |
|---|---|---|
| Course design | Gemini 3.6 Flash | 17 |
| Course design | MiniMax M3.1 Flash (NVIDIA) | 4 |
| Lecture delivery (plan, resources, guests) | Gemini 3.6 Flash | 16 |
| Lecture delivery (plan, resources, guests) | MiniMax M3.1 Flash (NVIDIA) | 8 |
| Lecture delivery (plan, resources, guests) | Nemotron 3 Ultra 550B (NVIDIA) | 4 |
| Lecture delivery (plan, resources, guests) | GPT-OSS 120B (Groq) | 3 |
| Slides | Gemini 3.6 Flash | 1 |
| Slides | Gemini 3.8 Flash | 1 |

Gemini timed out or hit its quota on some calls; the pipeline then moved to the next provider on its list, which is why other models appear.
