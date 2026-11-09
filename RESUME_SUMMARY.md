# Project Summary (for resume)

Context: built inside a bioreagent company in 2026, as product owner working with AI coding agents. Details and trade-offs: see each project's README in this repository.

## 1. Sales Copilot — AI sales & product-support assistant
- Launched an LLM assistant inside the company messenger to **60+ sellers**, letting them ask about accounts, recommendations, competitors and product knowledge in plain language.
- Chose a "hosted LLM orchestrates, we ship MCP tools" architecture with signed-identity, territory-based permissions (details in-territory, counts only outside); grew the tool layer from **~40 to 50+ tools** and split it into independently releasable servers after one-server releases forced repeated full re-acceptances.
- Defined the release gate: a **~25-question regression** plus a strict judge that fails any answer leaking internal tool names (last release **>90%** on the original rubric, **~85%** strict); every deploy shipped with check-only runs, independent audit and a one-line rollback.

## 2. Key-account recommendation engine
- Owned a transparent rule engine that maps each key account's drug pipeline (targets, modality, stage) to ranked Top/Optional product lists — **~2k rows, ~30k recommendation items** in the current frozen snapshot — with a per-item rule log so sellers can see why.
- Introduced impact-first rule changes: e.g. a "simple" species-rule change was shown to touch four code paths and **~11k items / ~1.5k rows**, turning a vague request into five concrete decisions.
- Instituted frozen, hash-pinned snapshot hand-offs after an early direct deploy broke **~500** alias links; open questions now arrive as structured decision cards with units, options and rollback.

## 3. All-account cross-sell & competitor catalog
- Extended recommendations from key accounts to the full account base (~**500k-row** merged table), delivered as versioned, hash-pinned releases.
- Replaced an "AI agent browses every site each refresh" design with **scout once → scripted crawl → local LLM normalizes → human spot-check**; latest batch parsed **100% of pages by template** with zero LLM calls.
- Built a **~10k-row** competitor catalog with append-only versioning (0 changed / 0 deleted rows per increment, 0 duplicate keys, 100% of prices verified against source text) and explicit NOT FOUND instead of guessed targets.

## 4. RAG knowledge base with evidence boundaries
- Designed a product-knowledge RAG over **~450** internal notes plus training decks that returns source, page, date and known conflicts — and a typed `do_not_guess` (not in snapshot / no evidence / below threshold) instead of a blended answer.
- Set the evaluation policy: golden questions written against held-out sources excluded from training, human-verified "gold" vs model-drafted "silver", leak tests, and dev/test split by source.
- Negotiated a versioned interface between two projects with budgets (≤300-char snippets, top-k ≤8, p95 ≤1.5 s keyword / ≤3 s with embeddings) and a degraded-first mode for a host without ML runtimes.

## 5. Multi-agent coordination system
- Designed and run a team of **about seven AI coding-agent sessions** (dispatcher, five builders, read-only auditor) plus a second coding agent, coordinated through file inboxes, a path-ownership table and structured decision cards.
- Enforced safety with a pre-tool-use guard hook that hard-blocks deletes, production deploys, remote shell, `git push` and raw-data reads; only the human runs irreversible actions, each with command + expected output + rollback.
- Added an independent two-model audit (findings "confirmed" only with a repro or line number; PASS / PASS_WITH_FIXES / BLOCK); migrated the whole team to a new agent tool in **one day** via handover files.

## 6. Local LLM batch processing
- Stood up a local **27B open-weight model** for bulk normalization and classification so sensitive rows never leave the machine; set the model-routing policy across local model, cloud coding agent and frontier model.
- Standardized "rules first, LLM as fallback, every field grounded in the input or NOT FOUND", and a file-lock protocol that lets two projects share one workstation with a full hold/release history.
