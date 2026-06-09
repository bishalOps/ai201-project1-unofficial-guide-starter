# The Unofficial Guide — Project 1

A retrieval-augmented question-answering system over real Reddit threads about CS
internships and early-career advice. Ask a question, the system retrieves the most
relevant snippets of community advice, and a grounded LLM answers using only those
snippets — with the source documents cited.

**Run it:**

```bash
pip install -r requirements.txt          # in a venv
# add your Groq key to .env:  GROQ_API_KEY=...
python embed.py                          # build the ChromaDB index (one-time)
streamlit run app.py                     # open http://localhost:8501
```

---

## Domain

**CS internship and early-career advice** — the unofficial, experience-based knowledge
that CS students and junior engineers share with each other about landing internships,
preparing for technical and behavioral interviews, writing a resume with little
experience, surviving the first weeks on the job, and converting an internship into a
full-time return offer.

This knowledge is valuable and hard to find through official channels because university
career centers and company career pages give generic, sanitized advice ("tailor your
resume," "practice coding problems"). They don't tell you what people actually learned
through trial and error: that interviewers can tell when you're bluffing a behavioral
answer, that a stranger won't refer you because a referral means vouching for you, or
that the highest-leverage thing an intern can do is ask detailed questions instead of
silently struggling. This system surfaces that lived experience.

---

## Document Sources

15 cleaned Reddit threads, chosen to cover different subtopics (interviews, referrals,
resumes, imposter syndrome, return offers, side projects) and different communities.
Each file was manually cleaned into a `SOURCE / TITLE / URL / --- POST --- / --- COMMENTS ---`
structure before ingestion.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | r/cscareerquestions | Reddit thread | https://www.reddit.com/r/cscareerquestions/comments/17fofv/ |
| 2 | r/datascience | Reddit thread | https://www.reddit.com/r/datascience/comments/1gxm6nh/ |
| 3 | r/cscareerquestions | Reddit thread | https://www.reddit.com/r/cscareerquestions/comments/pjgf10/ |
| 4 | r/college | Reddit thread | https://old.reddit.com/r/college/comments/1hs4h5p/ |
| 5 | r/jobsearch | Reddit thread | https://www.reddit.com/r/jobsearch/comments/1sf0sk4/ |
| 6 | r/cscareerquestions | Reddit thread | https://www.reddit.com/r/cscareerquestions/comments/8w0dxx/ |
| 7 | r/csMajors | Reddit thread | https://www.reddit.com/r/csMajors/comments/1cszspb/ |
| 8 | r/UXDesign | Reddit thread | https://www.reddit.com/r/UXDesign/comments/1avz31e/ |
| 9 | r/leetcode | Reddit thread | https://www.reddit.com/r/leetcode/comments/1kmt5le/ |
| 10 | r/cscareerquestions | Reddit thread | https://old.reddit.com/r/cscareerquestions/comments/9dd0yb/ |
| 11 | r/cscareerquestions | Reddit thread | https://www.reddit.com/r/cscareerquestions/comments/14qyteg/ |
| 12 | r/ExperiencedDevs | Reddit thread | https://old.reddit.com/r/ExperiencedDevs/comments/1p2ew23/ |
| 13 | r/resumes | Reddit thread | https://www.reddit.com/r/resumes/comments/1gl1dem/ |
| 14 | r/internships | Reddit thread | https://www.reddit.com/r/internships/comments/1ddq1st/ |
| 15 | r/cscareerquestions | Reddit thread | https://www.reddit.com/r/cscareerquestions/comments/btei0w/ |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 80 characters (20%)

**Why these choices fit your documents:**
These documents are Reddit threads — a short original post followed by dozens of
comments. The atomic unit of advice is a single comment, typically one to three
paragraphs (~300–600 characters). 400 characters is large enough to hold one complete
tip with its justification, but small enough that a chunk stays on a single topic. Much
larger (1,000+) would blend several unrelated commenters' tips into one embedding and
dilute it; much smaller (~150) would slice advice mid-sentence so individual chunks lose
standalone meaning. The 80-character overlap exists because fixed-size cuts land in
arbitrary places (often mid-sentence), so a thought split across a boundary still appears
intact in one of the two neighboring chunks.

**Preprocessing before chunking:** Documents were first manually cleaned of Reddit UI
noise (vote counts, usernames, timestamps, "load more comments" links, bot/AutoModerator
stickies, and one ad block). At ingest time, `parse_document()` separates the
`SOURCE/TITLE/URL` header into metadata (so it is never embedded as content), the
`--- POST ---` / `--- COMMENTS ---` structural markers are stripped, and chunks under 50
characters are dropped as fragments.

**Final chunk count:** 721 chunks across all 15 documents (min length 105 chars, max 400,
avg 396).

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (384-dimensional
embeddings), with chunks stored in a local **ChromaDB** persistent collection configured
for **cosine** distance. Retrieval returns **top-k = 5**. It runs locally on CPU with no
API key or rate limits, embeds the full corpus in ~2 seconds, and captures meaning well
for short, opinion-based English text — exactly this corpus.

**Production tradeoff reflection:**
If I were deploying this for real users and cost weren't a constraint, I'd evaluate a
larger model such as OpenAI `text-embedding-3-large` or a domain-tuned model, weighing:
(1) **accuracy on domain-specific text** — bigger models distinguish near-synonyms better,
which matters when "return offer," "full-time conversion," and "FTE offer" should cluster
together; (2) **context length** — MiniLM truncates at 256 tokens, so the longest "novel"
comments are clipped before they're even chunked, and a longer-context model would embed
more of each chunk faithfully; (3) **latency and hosting** — an API model adds a network
round-trip and a per-token bill per query, versus MiniLM running free and offline; and
(4) **multilingual support** — not needed here since the corpus is English-only, so I
wouldn't pay for it.

---

## Grounded Generation

LLM: Groq `llama-3.3-70b-versatile`, temperature 0.2, max 700 tokens.

**System prompt grounding instruction:** The model is instructed to answer using **only**
the numbered context passages, with explicit rules: "Use only facts stated in the context
passages. Do NOT use outside knowledge, and do NOT guess or infer beyond what the passages
actually say." If the passages don't contain enough information, it must reply with one
exact sentence — *"I don't have enough information on that in my documents."* — and nothing
else. The retrieved chunks are formatted into a numbered, source-tagged context block
(`[1] (from: filename) ...`) so the model sees provenance inline, and the user message is
structured as `Context:\n{context}\n\nQuestion: {question}`. Lowering the temperature to
0.2 further reduces the chance of the model drifting into its training knowledge.

**How source attribution is surfaced in the response:** Attribution is **programmatic, not
LLM-generated.** The model is explicitly told *not* to write its own "Sources" section.
Instead, after generation, the code attaches the actual filenames of the retrieved chunks
(deduplicated, in retrieval order). If the model declines for lack of grounding, the source
list is empty. This guarantees the cited sources are the documents actually retrieved — the
LLM cannot hallucinate, omit, or invent a citation.

---

## Evaluation Report

All 5 questions are the test questions from `planning.md`, run through the live system.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Most repeated thing interns should do when they don't understand something? | Ask questions (but don't make people repeat the same answer twice) | "The single most repeated thing is to ask questions." | Relevant (wish_knew #2/#10, 0.32) | **Accurate** |
| 2 | How does the "30 min/day" LeetCode poster say to study to retain long-term? | Consistency over cramming; spaced repetition / revisiting problems | "Alternate daily between LeetCode and System Design; study slowly, consistently, intentionally, and patiently." | Partially relevant (top chunk from failed_coding_interview, 0.33; leetcode chunks follow) | **Partially accurate** — captures consistency, but doesn't state the spaced-repetition/revisiting mechanism |
| 3 | Best way to get an interview in a bad market, and the catch about asking strangers for referrals? | Referrals are a top way in; catch is strangers won't refer you because a referral means vouching — you need a real connection | "The best way is through referrals. The catch when asking strangers is to reframe the request — instead of asking for a referral, ask for a 15-minute conversation about their experience; a referral may come naturally if it goes well." | Relevant (how_to_get_referral + job-referral, 0.32) | **Partially accurate** — got "referrals = best" and a grounded, useful tactic, but labels the *mitigation* as "the catch"; never states the real obstacle (a stranger won't vouch for someone they don't know) |
| 4 | Student with no work experience — what goes on a resume? | School/group projects, volunteering, clubs, skills, relevant coursework; framed as transferable skills; one page | "School projects, education, school/life experience, hard skills (Word/Excel), soft skills (responsibility, communication)." | Relevant (resume_tips #0, 0.27) | **Accurate** |
| 5 | How should I phrase a question to my mentor to get good help with my resume? | Give lots of detail — say what you tried ("I tried x, y, z but still get this error") instead of "I can't build it" | "I don't have enough information on that in my documents." | Off-target for top-k (relevant chunks ranked #7–#8, just outside k=5) | **Inaccurate** (see Failure Case) |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

Summary: 2 accurate, 2 partially accurate, 1 inaccurate. Across all five, the system never
hallucinated content outside the documents — its one wrong answer was a *refusal*, not a
fabrication.

---

## Failure Case Analysis

**Question that failed:** "How should I phrase a question to my mentor so I get good help
during my internship?"

**What the system returned:** *"I don't have enough information on that in my documents."*
— even though the documents **do** contain this exact advice.

**Root cause (tied to a specific pipeline stage):** This is a **retrieval recall** failure
caused by the interaction of two pipeline stages — chunking and top-k selection.

The relevant advice lives in `wish_knew_before_internship.txt`: *"when you ask for help or
have a question give a lot of details. There is a big difference in 'I can't build' vs 'I
tried x, y and z but am still getting <whatever> error...'"* When I traced the query, that
advice falls in chunks **#21 and #22**, which rank **#7 (distance 0.500) and #8 (0.501)**
for this query — just past the `k = 5` cutoff (the 5th result was at 0.481). So the LLM
never received them.

Two compounding causes:
1. **Chunk boundary split the key thought.** The 400-character window cut the sentence so
   that "...give a lot of details." opens chunk #22 mid-thought, and the framing sentence
   ("when you ask for help give a lot of details") straddles the #21/#22 boundary. Each
   half-chunk is a weaker semantic match for "how to phrase a question to my mentor" than
   the intact thought would have been, pushing both chunks' distances up to ~0.50.
2. **Top-k cutoff excluded the weakened chunks.** Because the query's vocabulary ("phrase a
   question," "mentor") doesn't lexically overlap the chunk's vocabulary ("give a lot of
   details," "headspace"), generic "ask questions" chunks from `imposter_syndrome_tech.txt`
   and `wish_knew #17` scored slightly better and filled the top 5, bumping the truly
   relevant chunks to #7–#8.

Notably, the grounding logic worked **correctly**: with only generic chunks in context, the
model declined rather than fabricating an answer. The system *failed safe* — a recall miss,
not a hallucination.

**What you would change to fix it:** Two options, in order of preference. (a) Raise `k`
from 5 to ~8 — the relevant chunks at rank #7–#8 would then be retrieved (cheap, but adds
some lower-relevance context to every query). (b) Better: reduce boundary damage by chunking
on sentence/paragraph boundaries (or increasing overlap) so the "give a lot of details / I
tried x, y, z" advice stays intact in one chunk and embeds as a stronger match — fixing the
root cause rather than masking it with a larger k.

### Second failure mode — generation over-refusal

A different and instructive failure: *"Is Leetcode enough to prepare for FAANG interviews?"*
also returns *"I don't have enough information on that in my documents."* — but here
**retrieval is excellent.** The top chunks score 0.34–0.42 and are squarely on-topic
(`leetcode_prep_strategy.txt`, and `real_world_coding_interview_prep.txt` saying *"my
interviews haven't looked much like classic LeetCode puzzles"*). The relevant context *was*
in the prompt.

The failure is in **generation, not retrieval.** No passage states verbatim that Leetcode
is or isn't "enough," and the strict grounding prompt ("do not infer beyond what the
passages say," temperature 0.2) made the model decline rather than synthesize the clear
implication from on-topic context. This is the deliberate trade-off of the grounding design:
it errs toward refusal over hallucination, and the cost is occasional over-refusal on
questions that require light synthesis. Loosening the prompt to allow synthesis would fix
this but raise hallucination risk — a tuning dial, not a bug. Together the two cases show the
two ways this pipeline can fail: a **retrieval recall miss** (mentor question) and a
**generation over-refusal** (this one).

---

## Spec Reflection

**One way the spec helped you during implementation:**
The Chunking Strategy and Retrieval Approach sections of `planning.md` pinned down concrete
numbers *before* I wrote any code — 400-character chunks, 80-character overlap, drop chunks
under 50 characters, `all-MiniLM-L6-v2`, top-k = 5. That meant implementing `chunk_text()`
and the retrieval function was a direct translation of the spec rather than a series of
in-the-moment guesses, and when retrieval misbehaved I had documented baseline values to
compare against instead of wondering whether I'd picked the wrong size. Writing the 5
evaluation questions up front also gave me a fixed target to test against at the end, so
"is it working?" had a concrete, pre-committed definition.

**One way your implementation diverged from the spec, and why:**
`planning.md` described source attribution as the LLM citing its sources in the answer.
During implementation I diverged to **programmatic** attribution: the model is told *not* to
write a sources section, and the code appends the actual retrieved filenames instead. I made
this change because an LLM-written citation can list the wrong document, omit one, or invent
a filename — none of which the original plan guarded against. Computing attribution from the
retrieval results makes it impossible for the cited sources to disagree with what was
actually retrieved. A second, smaller divergence: the spec didn't specify a distance metric,
and ChromaDB's default (L2) produced scores of 0.6–1.0 that were hard to interpret against
the project's 0.5 relevance threshold, so I explicitly configured the collection for cosine
distance, which dropped good-match scores into the 0.27–0.45 range.

---

## AI Usage

**Instance 1 — Fixing the retrieval distance metric**

- *What I gave the AI:* The Retrieval Approach section of `planning.md` (all-MiniLM-L6-v2,
  ChromaDB, top-k = 5) and a request to implement the embedding/retrieval code, then the
  observation that my first test queries were returning distance scores of 0.6–1.0 even for
  obviously on-topic results.
- *What it produced:* An `embed.py` that created the ChromaDB collection with
  `client.create_collection(name)` — using Chroma's **default L2 distance**, which is what
  produced the inflated, hard-to-interpret scores.
- *What I changed or overrode:* I directed it to configure the collection for cosine
  distance (`metadata={"hnsw:space": "cosine"}`) — the standard metric for sentence-
  transformer embeddings — and rebuilt the index. Top results dropped from ~0.69 to ~0.34,
  bringing every test query under the project's 0.5 relevance threshold. The content
  relevance hadn't changed; the metric had been the problem.

**Instance 2 — Overriding LLM-generated source citations**

- *What I gave the AI:* The grounding requirement (answer only from retrieved context, with
  source attribution) and the existing `app.py`, asking it to wire generation to Groq.
- *What it produced:* A system prompt that instructed the LLM to "list the source documents
  you drew from under the heading 'Sources:'", with a programmatic fallback that only
  appended sources *if* the model forgot to.
- *What I changed or overrode:* I rejected the LLM-cites-itself approach because if the model
  wrote a "Sources:" line listing the *wrong* documents, the fallback would never trigger and
  the citation would be silently wrong. I refactored the logic into a separate `rag.py` with
  an `ask()` function that tells the model **not** to write a sources section and instead
  always appends the real retrieved filenames in code (and suppresses them entirely when the
  model declines). This made attribution impossible to hallucinate. I also extracted this
  logic out of the Streamlit file so it could be unit-tested without launching the UI.
