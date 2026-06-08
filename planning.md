## Domain

CS Internship and Early Career Advice, specifically the unofficial, experience-based knowledge that CS students share with each other about landing internships, preparing for technical interviews, surviving the first weeks on the job, and converting internships to full-time offers. Unlike official career center websites give generic advice; this system surfaces what students and early-career engineers actually learned through trial and error.

## Documents

| # | Source | Description | URL |
|---|--------|-------------|-----|
| 1 | r/cscareerquestions | What to expect from a behavioral interview | https://www.reddit.com/r/cscareerquestions/comments/17fofv/ |
| 2 | r/datascience | Help choosing between two job offers | https://www.reddit.com/r/datascience/comments/1gxm6nh/ |
| 3 | r/cscareerquestions | Failed a medium/easy coding question and feel terrible | https://www.reddit.com/r/cscareerquestions/comments/pjgf10/ |
| 4 | r/college | How do you get internships with no work experience? | https://old.reddit.com/r/college/comments/1hs4h5p/ |
| 5 | r/jobsearch | Best way to get a job referral to tech companies? | https://www.reddit.com/r/jobsearch/comments/1sf0sk4/ |
| 6 | r/cscareerquestions | Extreme Imposter Syndrome at new internship | https://www.reddit.com/r/cscareerquestions/comments/8w0dxx/ |
| 7 | r/csMajors | How to get a return offer? | https://www.reddit.com/r/csMajors/comments/1cszspb/ |
| 8 | r/UXDesign | Best advice for requesting job referrals from strangers | https://www.reddit.com/r/UXDesign/comments/1avz31e/ |
| 9 | r/leetcode | How I cracked FAANG+ with just 30 minutes of studying per day | https://www.reddit.com/r/leetcode/comments/1kmt5le/ |
| 10 | r/cscareerquestions | Negotiating return offer or learning to accept | https://old.reddit.com/r/cscareerquestions/comments/9dd0yb/ |
| 11 | r/cscareerquestions | Good side projects for junior developers with no SWE experience | https://www.reddit.com/r/cscareerquestions/comments/14qyteg/ |
| 12 | r/ExperiencedDevs | How to prepare for a real-world coding interview vs LeetCode | https://old.reddit.com/r/ExperiencedDevs/comments/1p2ew23/ |
| 13 | r/resumes | What do I put on a resume with absolutely no experience | https://www.reddit.com/r/resumes/comments/1gl1dem/ |
| 14 | r/internships | When did you start applying for summer and how did you track it? | https://www.reddit.com/r/internships/comments/1ddq1st/ |
| 15 | r/cscareerquestions | What do you wish you knew before you started your internship? | https://www.reddit.com/r/cscareerquestions/comments/btei0w/ |

## Chunking Strategy

**Chunk size: 400 characters. Overlap: 80 characters (20%).** Fixed-size character chunking.

My documents are Reddit threads: a short original post followed by dozens of comments. The atomic unit of advice is a single comment, which is usually one to three paragraphs — roughly 300–600 characters for the focused ones, much longer for the occasional "novel" reply. A single piece of actionable advice ("ask a question every time you hear something you don't know") almost always lives inside one comment.

I chose 400 characters because it is large enough to hold one complete thought or tip with its surrounding justification, but small enough that a chunk stays on a single topic. If I went much larger (e.g. 1,000+ characters), one chunk would blend several unrelated tips from different commenters and dilute the embedding — a query about "imposter syndrome" could pull a chunk that's 80% about resume formatting. If I went much smaller (e.g. 150 characters), advice would get sliced mid-sentence and individual chunks would lose the context needed to be useful on their own.

The 80-character overlap exists because fixed-size cuts fall in arbitrary places — often mid-sentence. Overlap means a thought split across a chunk boundary still appears intact in one of the two neighboring chunks, so it stays retrievable. Twenty percent is a common default that buys boundary safety without inflating the index with too much duplicated text.

Chunks shorter than 50 characters are dropped (they're usually fragments like "Good luck!" that add noise without adding retrievable meaning).

## Retrieval Approach

**Embedding model: `all-MiniLM-L6-v2` via `sentence-transformers`. Vector store: ChromaDB (persisted locally). Top-k: 5.**

`all-MiniLM-L6-v2` produces 384-dimensional embeddings, runs locally on CPU with no API cost, and is fast enough to embed the whole corpus in ~30 seconds and a single query in milliseconds. For short, opinion-based English text it captures meaning well, which is exactly what this corpus is.

Semantic search works here because it matches on *meaning*, not keywords. A user asking "I'm scared I'll be exposed as a fraud at my new job" never uses the words "imposter syndrome," yet the embedding for that query lands near comments that discuss "feeling like you don't belong and that someone will figure you out for the fraud that you are." Keyword search would miss that connection entirely.

I retrieve **top-k = 5** chunks per query. This corpus is opinionated and repetitive — many commenters give variations of the same advice — so pulling 5 chunks lets the LLM see a *consensus* (e.g. several people independently saying "ask questions early") rather than one person's hot take. Retrieving too few (k=1–2) risks missing the best chunk if the single closest match happens to be tangential; retrieving too many (k=15+) floods the prompt with low-relevance chunks, raises token cost, and can dilute the answer or push the model toward off-topic tangents.

**If cost weren't a constraint**, I'd evaluate a larger model such as OpenAI `text-embedding-3-large` or a domain-tuned model. The tradeoffs I'd weigh: (1) **accuracy on domain-specific text** — bigger models distinguish near-synonyms better, which matters when "return offer," "full-time conversion," and "FTE offer" should all cluster together; (2) **context length** — MiniLM truncates at 256 tokens, so the longest "novel" comments get clipped before chunking even matters; a longer-context model embeds more of each chunk faithfully; (3) **latency and hosting** — an API model adds a network round-trip per query and a per-token bill, versus MiniLM running free and offline; (4) **multilingual support** — not needed here since the corpus is English-only, so I wouldn't pay for it.

## Evaluation Plan

Five test questions, each with an expected answer grounded in a specific source document so a grader can verify the system's response.

1. **Q: According to the internship advice, what is the single most repeated thing interns should do when they don't understand something?**
   *Expected:* Ask questions — ask every time you hear something you don't know, no matter how dumb it seems — but don't make people repeat the same answer twice. (Source: `wish_knew_before_internship.txt`)

2. **Q: How does the "30 minutes a day" LeetCode poster say you should study to retain problems long-term?**
   *Expected:* Consistency over cramming — study a little every day and use spaced repetition / revisiting problems rather than marathon sessions. (Source: `leetcode_prep_strategy.txt`)

3. **Q: What do people say is the best way to get an interview in a bad job market, and what's the catch about asking strangers for referrals?**
   *Expected:* Referrals are one of the best ways to get an interview, but strangers generally won't refer you because a referral means vouching for you — so you need a real connection (former colleagues, second-degree connections, or an intro) rather than cold-messaging strangers. (Source: `job-referral.txt`)

4. **Q: If I'm a student with no work experience, what should I put on my resume?**
   *Expected:* School/group projects, volunteering, clubs, sports, leadership roles, side hustles (babysitting, tutoring, mowing lawns), relevant coursework, and skills — framed in terms of transferable skills like teamwork, reliability, and communication. Keep it to one page. (Source: `resume_tips_cs_students.txt`)

5. **Q: How should I phrase a question to my mentor so I get good help during my internship?**
   *Expected:* Give lots of detail — say what you already tried ("I tried X, Y, Z and still get this error in this component") instead of just "I can't build it" — so the mentor can get into the right headspace and see you put in effort. (Source: `wish_knew_before_internship.txt`)

A correct response should surface the expected advice and cite the matching source document under "Sources:". A wrong response would invent advice not in the corpus, cite the wrong document, or refuse a question the corpus clearly covers.

## Anticipated Challenges

1. **Noisy source documents leaking into answers.** These are copy-pasted Reddit threads, so the raw text is full of UI chrome — vote counts, usernames, timestamps, "load more comments," and bot/AutoModerator stickies (e.g. the Reddit-API-protest message and the resume-wiki bot reply). If that noise survives cleaning, it gets embedded as chunks and can be retrieved as if it were advice, producing answers that quote a bot or a nav element. *Mitigation:* I cleaned all 15 files into a strict `SOURCE / TITLE / URL / --- POST --- / --- COMMENTS ---` structure and strip residual chrome at ingest time.

2. **Advice split across chunk boundaries.** A long comment that builds an argument across several sentences can get cut so that the conclusion lands in one chunk and the reasoning in the next; either chunk alone is then less retrievable for a query that uses the *other* half's vocabulary. *Mitigation:* the 80-character overlap keeps boundary-spanning thoughts intact in at least one chunk.

3. **Off-topic / cross-thread retrieval.** Because the corpus is repetitive and opinionated, a query about one subtopic (e.g. negotiating a return offer) can pull a high-similarity chunk from an adjacent subtopic (e.g. a general job offer comparison from the data-science thread). *Mitigation:* top-k=5 plus a strict system prompt that tells the LLM to answer only from the provided context and to say so when the context doesn't cover the question.

4. **Weak source attribution.** Each chunk carries only source/title/filename metadata; if a chunk's metadata is wrong, the cited source is wrong even when the advice is right. *Mitigation:* metadata is read from the structured document header, and the app falls back to appending the retrieved filenames under "Sources:" if the model omits them.

## AI Tool Plan

I'll use Claude (via Claude Code) on specific, well-scoped pieces of the pipeline, feeding it the relevant planning.md section as the spec:

- **Document cleaning (Ingestion):** Input — a raw Reddit paste plus the target `SOURCE/TITLE/URL/--- POST ---/--- COMMENTS ---` format. Expected output — a cleaning routine that detects old- vs. new-Reddit paste formats and strips UI noise. *(Done — though this exposed a real bug: the first cleaning pass wasn't idempotent and corrupted files on a second run, which I had to patch.)*
- **Chunking:** Input — my Chunking Strategy section (400-char chunks, 80-char overlap, drop <50 chars). Expected output — the chunking and text-cleaning logic.
- **Embedding + Vector Store:** Input — my Retrieval Approach section (all-MiniLM-L6-v2, ChromaDB persistent client, drop-and-recreate on rebuild). Expected output — the index-building and query functions.
- **Generation / UI:** Input — the requirement that the LLM answer *only* from retrieved context, cite sources, and refuse gracefully when context is missing. Expected output — the system prompt, answer-generation logic, and Streamlit front-end wired to Groq's `llama-3.3-70b-versatile`.
- **Evaluation:** Input — my five test questions and their expected answers. Expected output — I'll run each question through the app and ask Claude to compare the response against the expected answer and flag hallucinations or wrong citations.

I will **not** ask AI to invent domain content or test answers — those come from the actual documents so the evaluation stays honest. And the `.env` holding `GROQ_API_KEY` is never shared with any tool or committed.

## Architecture

The five-stage RAG pipeline, with the tool/library used at each stage:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          BUILD-TIME (run once)                           │
└──────────────────────────────────────────────────────────────────────────┘

   ┌─────────────────────┐
   │ 1. DOCUMENT         │   15 cleaned Reddit threads (documents/*.txt)
   │    INGESTION        │   SOURCE / TITLE / URL / --- POST --- / --- COMMENTS ---
   │  (Python)           │   strips residual UI noise
   └──────────┬──────────┘
              │ raw cleaned text
              ▼
   ┌─────────────────────┐
   │ 2. CHUNKING         │   400-char chunks, 80-char overlap,
   │  (Python)           │   drop chunks < 50 chars
   └──────────┬──────────┘
              │ list of text chunks (+ source/title/filename metadata)
              ▼
   ┌─────────────────────┐
   │ 3. EMBEDDING +      │   all-MiniLM-L6-v2 (sentence-transformers)
   │    VECTOR STORE     │   → 384-dim vectors
   │                     │   stored in ChromaDB (persisted ./chroma_db)
   └─────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                          QUERY-TIME (per question)                       │
└──────────────────────────────────────────────────────────────────────────┘

   User question (Streamlit text box)
              │
              ▼
   ┌─────────────────────┐
   │ 4. RETRIEVAL        │   embed query with all-MiniLM-L6-v2,
   │                     │   ChromaDB similarity search → top-k = 5 chunks
   └──────────┬──────────┘
              │ 5 relevant chunks + filenames
              ▼
   ┌─────────────────────┐
   │ 5. GENERATION       │   Groq  llama-3.3-70b-versatile  (temp 0.3)
   │                     │   context-only system prompt, appends "Sources:"
   └──────────┬──────────┘
              │
              ▼
   Answer + cited source documents  →  rendered in Streamlit
```

**Stage → tool summary:** Ingestion = Python · Chunking = fixed-size + overlap · Embedding = `all-MiniLM-L6-v2` (sentence-transformers) · Vector Store = ChromaDB · Retrieval = ChromaDB top-k search · Generation = Groq `llama-3.3-70b-versatile` · UI = Streamlit.