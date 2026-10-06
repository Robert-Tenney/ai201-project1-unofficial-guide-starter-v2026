# The Unofficial Guide

Robert Tenney — corpus: `advice_threads`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

This project is a small question-answering system built on the `advice_threads`
corpus. It indexes the documents, splits them into chunks, and answers a
question by retrieving the closest chunks and passing only those to the model.
It answers practical newcomer questions such as "Which meal plan tier is
right?" and "When should I start looking for a summer internship?". A relevance gate refuses to answer when nothing retrieved is
close enough, returning "I don't have enough information about that," and every
answer names the source files it came from.

## Chunking Strategy

**Chunk size:** up to 1000 characters (`MAX_CHARS`), built from whole paragraphs; a final chunk under 150 characters (`MIN_CHARS`) is merged into the one before it
**Overlap:** none (0). Chunks break at paragraph boundaries; a paragraph over 1000 characters is split at line breaks, then sentence ends, so nothing is cut mid-sentence

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

The starter's fixed 800-character windows cut documents at arbitrary points
and, on `advice_threads`, produced a 2-character chunk from the tail of a
document that didn't divide evenly. My chunker (`chunker.py::chunk_documents`)
splits on blank lines and packs whole paragraphs together, so chunks start and
end at paragraph boundaries (or, for an oversized paragraph, at a line or
sentence boundary), and the merge rule means no fragment is left behind.

Reading the `advice_threads` files, each thread opens with a `THREAD:` title and
every reply sits under its own `--- reply N (X votes) ---` marker, separated by
blank lines. The threads I sampled run well under 1000 characters, so each one
comes out as a single chunk (every sample chunk below is `#0` of its file).
Keeping a thread whole keeps the replies that disagree with each other in the
same chunk, which is where the answer lives in this corpus. [CONFIRM this matches
what you saw when you read the files, and say so here if you changed 1000/150.]

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `thread_bike_commute.txt` — produced by: `chunker.py::chunk_documents`

```
THREAD: Is a bike worth it for a 20 minute walk commute?

--- reply 1 (14 votes) ---
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.

--- reply 2 (9 votes) ---
Counterpoint, I sold mine. Between November and March the paths are either icy or salted and salt destroys a drivetrain in one season.

--- reply 3 (22 votes) ---
Both true. I keep a cheap bike for September to November and walk the rest of the year. Total cost was about $120 for the bike and I don't care what happens to it.

--- reply 4 (5 votes) ---
If you do get one, the campus does free registration and it's the only reason I got mine back after it was taken.
```

**Chunk 2** — source: `thread_first_gen.txt` — produced by: `chunker.py::chunk_documents`

```
THREAD: Anything specific for first-generation students?

--- reply 1 (33 votes) ---
The advising office has a specific programme and it is genuinely good, but it is opt-in and badly publicised. Ask for it by name.

--- reply 2 (41 votes) ---
The thing I'd say: the unwritten rules are the hard part, not the coursework. Ask about the unwritten rules explicitly. People are happy to explain them and nobody volunteers them.

--- reply 3 (16 votes) ---
Emergency fund for textbooks and travel exists and is not means-tested beyond a short form.
```

**Chunk 3** — source: `thread_laptop_specs.txt` — produced by: `chunker.py::chunk_documents`

```
THREAD: How much laptop do I actually need for CS courses?

--- reply 1 (31 votes) ---
Less than the recommended spec page says. 16GB of RAM is the one number worth paying for; everything else you'll never notice.

--- reply 2 (18 votes) ---
Adding: the lab machines exist and are better than anything you'll buy. For the heavy assignments people just use those.

--- reply 3 (12 votes) ---
I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.
```

**Chunk 4** — source: `thread_office_hours_etiquette.txt` — produced by: `chunker.py::chunk_documents`

```
THREAD: Is it weird to go to office hours with no specific question?

--- reply 1 (44 votes) ---
No, and this is the single most common thing first years get wrong. 'I'm following the lectures but I don't feel like I understand the shape of it' is a completely normal thing to say.

--- reply 2 (29 votes) ---
They're usually empty. You are doing the instructor a favour by turning up.

--- reply 3 (18 votes) ---
If it helps, treat it as a standing appointment. Go every week for a month and it stops feeling like a thing.
```

**Chunk 5** — source: `thread_professor_email.txt` — produced by: `chunker.py::chunk_documents`

```
THREAD: Do professors actually answer email?

--- reply 1 (21 votes) ---
Varies enormously. General rule I've found: if the syllabus states a response window, it's honoured. If it doesn't, assume 48 hours and don't panic before then.

--- reply 2 (33 votes) ---
Office hours are dramatically more effective than email for anything that takes more than two sentences to answer. They're also usually empty.

--- reply 3 (15 votes) ---
Empty office hours is the biggest unused resource here and I say that having wasted a year not going.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** Which meal plan tier is right

**Answer:**

```
The right meal plan tier depends entirely on whether your building has a kitchen; people in Fenwick can go down a tier and cook two or three nights, while everyone else should get the middle tier (thread_meal_plan_tier.txt). The highest tier only makes sense if you eat three meals a day in the halls every single day (thread_meal_plan_tier.txt).

Sources retrieved: thread_clubs.txt, thread_first_year_regret.txt, thread_meal_plan_tier.txt, thread_pass_fail.txt, thread_transfer_credits.txt
```

**My relevance cutoff:** [YOUR NUMBER, e.g. 0.6 — the value you set in config.py]

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
| Which meal plan tier is right | Yes | [0.000] |
| First winter here — what do I need? | Yes | [0.000] |
| When should I start looking for a summer internship? | Yes | [0.000] |
| Is the printing quota enough? | Yes | [0.000] |
| Do transfer credits actually count toward the major? | Yes | [0.000] |
| What is the capital of Mongolia? | No | [0.000] |
| How do I change the oil in a diesel engine? | No | [0.000] |
| Who won the 1994 World Cup? | No | [0.000] |
| What is the recommended dosage of ibuprofen for a headache? | No | [0.000] |
| How do I write a for loop in Rust? | No | [0.000] |

The in-corpus group's best distances ran from [LOW] to [HIGH], and the out-of-scope group's from [LOW] to [HIGH], so the gap sat between [X] and [Y]. I put the cutoff at [YOUR NUMBER] because [WHY THAT POINT IN THE GAP]. At that number the risk is [WHAT IT WOULD GET WRONG, e.g. refusing an in-corpus question that sits near the line].

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I asked Claude where my replacement chunker should go in `chunker.py`. It first gave me a function that took one string of text, which didn't match the starter, where `split_documents` takes a list of `Document` objects and returns `Chunk` objects. After I uploaded `chunker.py`, it rewrote the function to loop over the documents and build `Chunk` objects with `produced_by="chunker.py::split_documents"`. I kept the original docstring and the rest of the file and replaced only the function body. [ADD WHAT YOU CHANGED YOURSELF, e.g. your own MAX_CHARS/MIN_CHARS values.]

**2.** I asked Claude to rename `split_documents` to `chunk_documents` in `app.py`. It changed the four places the name appears (the import and call in `cmd_index` and in `cmd_chunks`) and warned me that `chunker.py` had to be renamed too or the imports would fail. I made the matching rename in `chunker.py`, including the `produced_by` string, so this README names the right function. [EDIT TO MATCH WHAT YOU ACTUALLY DID.]

**Unit 2 additions.** I asked Claude for a working `scorer.py`. It returned a judge that passes a question when any retrieved chunk contains the `expects` phrase (with a word-overlap fallback), plus a helper that checks whether an answer names a source file. [WHAT YOU CHECKED OR CHANGED — e.g. WORD_OVERLAP, or cases where it disagreed with your own grading.] [ADD ONE ENTRY FOR THE IMPROVEMENT YOU MADE: what you asked for, what came back, what you changed.]

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

Unit 2
Run Log — Before

Produced by python run_eval.py --label before, written to results/run_2026-10-06_1410_before.md. Corpus advice_threads, top-k 5, relevance cutoff 0.62, hybrid search off, chunks from chunker.py::chunk_documents.

Criterion	Target	Run 1	Run 2	Run 3	Verdict
1. Retrieved chunk contains the answer	4 of 5	3/5	3/5	3/5	MISSED
2. Every answer names a source	5 of 5	5/5	4/5	5/5	MISSED
3. Gate stops out-of-corpus questions	4 of 5	5/5	5/5	5/5	MET
4. Chunks stand alone (10 sampled)	8 of 10	9/10	9/10	9/10	MET
5. Answers are 3 sentences or fewer	5 of 5	5/5	5/5	5/5	MET

Criterion 1 — real output. File: results/run_2026-10-06_1410_before.md. Produced by run_eval.py::main, which calls store.py::search for retrieval. Question: "Is the printing quota enough?" Sources retrieved and best distance:

### Is the printing quota enough? — run 1

- Best distance: 0.5812 (passed the gate)
- Sources retrieved: thread_clubs.txt, thread_first_year_regret.txt, thread_laptop_specs.txt, thread_meal_plan_tier.txt, thread_pass_fail.txt

I don't have enough information about the printing quota in the documents provided.

Criterion 2 — real output. File: results/run_2026-10-06_1410_before.md. Produced by generate.py::answer_from_chunks. An answer that names a source (run 1):

Start looking earlier than feels reasonable, since many deadlines pass before the spring (thread_internships.txt).

The answer that did not (run 2, question "When should I start looking for a summer internship?"):

Start looking earlier than feels reasonable, since many deadlines pass before the spring.

Criterion 3 — real output. File: results/run_2026-10-06_1410_before.md. Produced by run_eval.py::check_out_of_scope. Cutoff 0.62; refused 5 of 5:

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.842 | refused |
| How do I change the oil in a diesel engine? | 0.871 | refused |
| Who won the 1994 World Cup? | 0.913 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.788 | refused |
| How do I write a for loop in Rust? | 0.857 | refused |

Criterion 4 — real output. Produced by chunker.py::chunk_documents, printed with python app.py chunks --indices 0,5,10,15,20,25,30,35,40,45. I read all ten by hand and asked of each whether a stranger could answer a question from it alone. Nine could. The one that could not was thread_pass_fail.txt#0, which is only a title line and one short reply:

THREAD: Pass/fail or letter grade?

--- reply 1 (6 votes) ---
Depends on the course.

Criterion 5 — real output. Produced by generate.py::answer_from_chunks. Longest answer in the run, three sentences:

The right meal plan tier depends on whether your building has a kitchen. People in Fenwick can go down a tier and cook two or three nights. The highest tier only makes sense if you eat three meals a day in the halls (thread_meal_plan_tier.txt).
Verdicts
#	Criterion	Verdict	How I decided
1	Retrieved chunks contain the answer (4 of 5)	MISSED	3 of 5 on all three runs, against a target of 4 of 5. It is identical across runs because retrieval is deterministic, so this was not a lucky or unlucky pass.
2	Every answer names a source (5 of 5)	MISSED	Runs came out 5, 4, 5. The target was 5 of 5 every time, and one answer in run 2 dropped the file name, so it did not hold.
3	Gate stops out-of-corpus questions (4 of 5)	MET	The gate refused 5 of 5 in a single deterministic pass. The closest out-of-scope question (0.788) is well over the 0.62 cutoff.
4	Chunks stand alone (8 of 10)	MET	9 of 10 on the same sampled chunks each time. The one failure was a title-plus-one-line thread, which is a corpus problem more than a chunker problem.
5	Answers are 3 sentences or fewer (5 of 5)	MET	All 15 answers across three runs were three sentences or fewer. This is probably too easy a target, since the grounding prompt already asks for brevity.
Diagnoses

Criterion 1, question "Is the printing quota enough?" Stage: retrieval. Mechanism: python app.py retrieve "Is the printing quota enough?" returned five threads about money and limits, with a best distance of 0.581, and thread_printing_quota.txt was not among them. The chunk exists and contains the expected phrase "For most people yes", so loading and chunking were fine. The embedding treats "quota enough?" as a general question about whether something is sufficient and ranked the broadly similar threads above the one that uses the exact word "quota".

Criterion 1, question "First winter here — what do I need?" Stage: retrieval. Mechanism: the retrieved chunks included thread_bike_commute.txt, which mentions winter paths, but not thread_winter_gear.txt, which holds "Layers, not a big coat". The embedding matched on the topic of cold and commuting and not on the specific thread about what to wear.

Criterion 2, run 2. Stage: generation. Mechanism: the retrieved chunks were correct and the answer text was correct, but the model left the file name off. The grounding instruction asks it to name the document, and nothing in the code enforces that, so it is wording the model usually follows and sometimes does not.

Pattern across the misses: the two criterion 1 misses are the same problem. Both questions hinge on a specific word ("quota", "winter") that appears in exactly one thread, and the embedding ranked on broad topic similarity instead. That is one retrieval problem, not two.

The Improvement

What I changed:

I turned on hybrid search by changing HYBRID in config.py to default to "1". store.py::_hybrid_search ranks every chunk twice, by cosine distance and by BM25 keyword score, merges the two rankings with reciprocal rank fusion (RRF_K = 60), and returns the top 5. Result.distance stays the cosine distance, so the relevance gate and my cutoff of 0.62 are unchanged. I changed nothing else.

Why I picked it:

Both criterion 1 misses depended on a specific word that only one thread contains, which is the case keyword matching is meant to catch.

Run Log — After

Produced by python run_eval.py --label after, written to results/run_2026-10-06_1615_after.md. Everything else is the same as the "before" run.

Criterion	Target	Run 1	Run 2	Run 3	Verdict
1. Retrieved chunk contains the answer	4 of 5	4/5	4/5	4/5	MET
2. Every answer names a source	5 of 5	5/5	5/5	4/5	MISSED
3. Gate stops out-of-corpus questions	4 of 5	5/5	5/5	5/5	MET
4. Chunks stand alone (10 sampled)	8 of 10	9/10	9/10	9/10	MET
5. Answers are 3 sentences or fewer	5 of 5	5/5	5/5	5/5	MET

Did it help?

Partly. Criterion 1 went from 3, 3, 3 to 4, 4, 4 and now meets its target. The question that changed was "Is the printing quota enough?": the word "quota" now puts thread_printing_quota.txt at rank 2 through the keyword ranking. "First winter here" is still missed, because several threads mention winter and BM25 ranked thread_bike_commute.txt above the gear thread. Criterion 2 did not improve, which is what I expected: it is a generation problem and hybrid search changes retrieval, so this time the dropped file name moved to run 3. Criterion 3 is unchanged because the best distances are still cosine distances.

What's Still Broken

Criterion 2: still missed, with a file name dropped in one run out of three. The fix I would make is to stop relying on the model to name the source and have the code append the source files after the answer, since the code already knows which chunks it used. I stopped because that is a second change, and this unit allows one.

Criterion 1, "First winter here": the one remaining retrieval miss. I would try a smaller top-k boost for exact-term matches, or add the thread title to each chunk's text so "winter" in a title outranks "winter" in a reply. I stopped because the criterion is now met and tuning for one question risks overfitting to it.

What I'd Do Differently

I would rewrite criterion 2. "Every answer names a source" depends on the model's wording and failed once in each set of runs, so a 5-of-5 target tests the model's habits more than my system. I would change it to measure whether the source line is present in every answer once the code appends it. I would also tighten criterion 5, which I met on every run without trying, to a limit of two sentences.