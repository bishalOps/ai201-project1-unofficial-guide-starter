# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

CS Internship and Early Career Advice, specifically the unofficial, experience-based knowledge that CS students share with each other about landing internships, preparing for technical interviews, surviving the first weeks on the job, and converting internships to full-time offers. Unlike official career center websites give generic advice; this system surfaces what students and early-career engineers actually learned through trial and error.

---

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

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
