# marketing-brain — System Architecture & Agent Team

**Version 0.1 · An autonomous, human-approved AI content engine**

This is the blueprint for the engine that sits between your **TheEleFant.ai operating model**
(Ideator → Creator → Calendar → Engager → Analyzer) and your **Airtable "Content Generation"
base**. The spreadsheet describes *what* should happen; the Airtable base *holds the records*;
this system is the *brain* that thinks and generates in between.

---

## 1. Design principles

1. **Lean team, deep toolbelt.** One orchestrator plus a roster of specialist agents that stay dormant until their stage fires. We get the range of a "massive team" without the cost and chaos of dozens of always-on agents.
2. **The control plane is the boss, not the bot.** Airtable (or Google Sheets) holds all state, and it is also the UI. A human reads, edits, and approves there. The agents are stateless workers that read jobs and write results back.
3. **Nothing publishes without a human.** Approval is a status transition only a person can make. The agents are *structurally forbidden* from approving their own work (`state.py`).
4. **Serverless and cheap.** Compute is GitHub Actions — cron + manual dispatch. There is no server to run, patch, or pay for when idle.
5. **Runs with zero keys.** Every external provider has a mock mode, so the entire loop works end-to-end in CI and on a laptop before a single API key exists. You wire providers in one at a time.
6. **Provider-agnostic.** Image, video, voice, and design are behind adapters. Swap Flux for Higgsfield, HeyGen for Kling, etc., without touching agent logic.

---

## 2. The operating model (your sheet → this engine)

| TheEleFant.ai stage | What it does | Agents that run it |
|---|---|---|
| **Ideator** | Scan platforms/news, build an idea bank | Trend Scout, Idea Miner, SEO Analyst |
| **Creator** | Pick format × media, generate copy + assets, v1/v2/v3 | Strategist, Copywriter, Designer, Video Producer, Voice Artist, Editor, Brand Guardian |
| **Calendar** | Slot content per platform | Scheduler |
| (gate) | **Human approves** | *you, in Airtable* |
| **Publish** | Push live | Publisher |
| **Engager** | Auto-comment, respond, prospect | Community Manager |
| **Analyzer** | Rank format × media × channel, feed strategy | Analyst |

The loop is closed: the Analyst's performance scores feed back into the Strategist's next
format/media decisions.

---

## 3. System architecture

```
                ┌──────────────────────────────────────────────┐
                │            CONTROL PLANE  (state + UI)         │
                │   Airtable  ⇄  (or Google Sheets)              │
                │   Ideas · Content · Assets · Jobs · Calendar   │
                │   Performance · Engagements · Brand            │
                └───────────────▲───────────────▲───────────────┘
                                │ read/write     │ human approves
                                │                │ (Status = Approved)
   ┌────────────────────────────┴────────────────┴───────────────┐
   │              COMPUTE  (GitHub Actions, serverless)            │
   │   cron + workflow_dispatch  →  python -m scripts.run_stage X  │
   │                                                              │
   │   Orchestrator ──▶ stage agents ──▶ provider adapters        │
   └───────────────────────────────▲──────────────────────────────┘
                                    │ API calls (live) / mock (no key)
        ┌───────────────┬──────────┴────────┬───────────────┐
     Anthropic       Flux / Higgsfield     HeyGen         ElevenLabs
      (copy)          (image / video)    (avatar video)     (voice)   + Canva (design)
```

- **Compute:** each stage is one GitHub Actions workflow. They run on a schedule and can be triggered by hand. The job checks out the repo, installs deps, and runs `scripts/run_stage.py <stage>`.
- **Control plane:** chosen automatically by `settings.control_plane` — Airtable if its keys are set, else Google Sheets, else a local JSON file (for dev/CI).
- **Brain:** the `marketing_brain` Python package — orchestrator, agents, providers.

---

## 4. The agent team

Fourteen roles. Each is a small class with one `run()` method; the orchestrator invokes the
agents for a stage in order. Defined in code under `marketing_brain/agents/` and described in
`config/agents.yaml`.

| # | Agent | Stage | Reads → Writes | Job |
|---|---|---|---|---|
| 0 | **Orchestrator** (Conductor) | all | — | Route stages, enforce budget + approval gate, retry |
| 1 | **Trend Scout** | discover | Brand → Ideas | Find rising topics + engagement signals |
| 2 | **Idea Miner** | discover | Ideas → Ideas | Dedupe, shortlist on-brand ideas |
| 3 | **SEO Analyst** | discover | Ideas → Ideas | Attach keyword, cluster, intent |
| 4 | **Strategist** | strategy | Ideas, Performance → Content | Pick format × media × platform from past wins |
| 5 | **Copywriter** | create | Content, Brand → Content | Hook, caption, CTA, hashtags (v1/v2/v3) |
| 6 | **Designer** | create | Content → Assets, Jobs | Image prompts + image/carousel render |
| 7 | **Video Producer** | create | Content → Assets, Jobs | Short-form + avatar video scripts & render |
| 8 | **Voice Artist** | create | Content → Assets | Voiceover / audio |
| 9 | **Editor** | create | Content, Assets → Content | Assemble assets, fit platform, mark Needs Review |
| 10 | **Brand Guardian** | create | Content, Brand → Content | Voice/safety gate; can reject |
| 11 | **Scheduler** | schedule | Content, Calendar → Calendar | Slot Approved content per platform |
| 12 | **Publisher** | publish | Content → Content | Publish **only Approved** records |
| 13 | **Community Manager** | engage | Content → Engagements | Draft comments/replies (await approval) |
| 14 | **Analyst** | analyze | Content, Performance → Performance | Score format × media × channel, feed Strategist |

To add a specialist: drop a class in `agents/`, list it in `agents.yaml`, and add it to the
relevant stage in `orchestrator.py`.

---

## 5. Data model (control-plane tables)

Defined in `schema/airtable_schema.json`; `scripts/setup_airtable.py` creates any that are
missing. These extend (do not replace) your existing Content Generation tables.

- **Ideas** — Topic, Angle, Source, Signal Score, Keyword, Cluster, Intent, Status
- **Content** — the master record (mirrors your Table 1 + Hook/Caption/CTA/Script/Asset URLs), Status
- **Assets** — one row per generated media file: Type, Provider, URL, Prompt, Job ID, Cost
- **Jobs** — generation queue: Agent, Type, Provider, Status, Cost, Retries, Error
- **Calendar** — Content ID, Platform, Publish Date, Slot, Status
- **Performance** — Impressions, Likes, Comments, Shares, CTA Clicks, Score
- **Engagements** — drafted comments/replies awaiting approval
- **Brand** — voice, audience, power words, forbidden words (from `config/brand.yaml`)

---

## 6. Lifecycle & the human-approval gate

```
Draft ─▶ Generating ─▶ Needs Review ──(HUMAN)──▶ Approved ─▶ Scheduled ─▶ Published
                            │                                                  
                            └────────────▶ Rejected ◀──── Brand Guardian
```

The state machine lives in `state.py`. The transition `Needs Review → Approved` is **not** in
the bot-allowed set — only an `actor="human"` may make it. The Publisher only ever reads records
in `Scheduled` (which can only be reached *after* a human approval), so there is no code path in
which a bot publishes unreviewed content. This is the structural guarantee behind your
"human approval before publish" choice.

In practice: you open Airtable, read the draft + assets, and flip **Status → Approved**. The next
Scheduler run picks it up. (For demos/CI, `scripts/simulate_approval.py` stands in for the human.)

---

## 7. Media generation & provider adapters

All six media types you selected are covered. Each adapter lives in `marketing_brain/providers/`
and extends `MediaProvider`. With no API key (or `DRY_RUN=true`) it returns a deterministic mock
URL; with a key it calls the real service. The agent code never changes.

| Capability | Adapter | Default provider | Swap-ins |
|---|---|---|---|
| Copy / text | `llm_anthropic` | Claude | any LLM |
| Images | `image_flux` | Flux / Higgsfield | DALL·E, SDXL |
| Carousels / design | `design_canva` | Canva Autofill | Bannerbear, Placid |
| Avatar video | `video_heygen` | HeyGen | D-ID, Synthesia |
| Short-form video | `video_shortform` | Higgsfield | Kling, Runway, Luma |
| Voice / audio | `voice_elevenlabs` | ElevenLabs | PlayHT, OpenAI TTS |

Wiring a provider = filling in the `_live()` method (each has a `# TODO` with the exact call
shape) and adding the API key to GitHub Secrets.

---

## 8. Automation (GitHub Actions)

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | every push / PR | compile, unit tests, full mock-mode smoke run |
| `discover.yml` | daily 06:00 + manual | find + shortlist + tag ideas |
| `create.yml` | every 6h + manual | strategy + generate + assemble → Needs Review |
| `publish.yml` | every 2h + manual | schedule + publish **Approved** only |
| `engage.yml` | every 4h + manual | draft engagement |
| `analyze.yml` | weekly Mon 07:00 + manual | score performance, feed strategy |

Secrets come from **GitHub → Settings → Secrets and variables → Actions**. Set repo *variable*
`DRY_RUN=false` only when you are ready to go live.

---

## 9. Security & secrets

- **No secret ever lives in code.** Keys are read from environment variables, populated by
  GitHub Actions Secrets in CI and by a local `.env` (git-ignored) in dev.
- **Rotate any exposed token immediately.** If a token is ever pasted into chat, an issue, or a
  commit, treat it as compromised and revoke it at <https://github.com/settings/tokens>. Prefer
  **fine-grained** tokens scoped to this single repo, or a GitHub App.
- **Least privilege.** The Airtable token only needs access to this one base. Each media key is
  optional and isolated.
- **Human gate = safety net.** Because nothing publishes without approval, a bad generation or a
  prompt-injected idea cannot reach an audience on its own.

---

## 10. Cost controls

- `budget.py` enforces a daily USD ceiling (`DAILY_USD_BUDGET`); each provider call is charged and
  the run aborts before overspending.
- Media is the expensive part — generation only happens for shortlisted ideas that became Content,
  and only once per record.
- Mock mode costs nothing, so testing and CI are free.

---

## 11. How it maps to your existing Airtable base

Your `appvpMfpbNQDkUGeF` base already has **Table 1** (social/content generation), the
**SEO pipeline** (Primary Keywords, Clusters, SERP, Article Writer…), **Brand Guidelines**,
**Video Generation**, and **AI Avatar**. marketing-brain treats those as the production tables and
adds the orchestration tables (Ideas, Assets, Jobs, Calendar, Performance, Engagements). The
Strategist writes into a Content table shaped like your Table 1; the SEO Analyst can read/write
your existing keyword tables. Nothing is thrown away — the brain plugs into what you have.

---

## 12. Roadmap

**Built now (v0.1)**
- Full agent team + orchestrator, runs end-to-end in mock mode
- Control-plane abstraction: Airtable / Google Sheets / local JSON
- Human-approval state machine + structural publish gate
- Provider adapter layer for all six media types (mock + `_live` stubs)
- GitHub Actions for every stage + green CI
- Airtable table provisioner

**Next (v0.2 — wire reality)**
1. Implement one `_live()` provider end-to-end (suggest: Copy + Image first).
2. Point the control plane at your real base (`setup_airtable.py`).
3. Replace Trend Scout's seed list with real platform/news search.
4. Implement one real Publisher target (e.g. LinkedIn or a buffer/queue API).

**Later (v0.3+)**
- Real engagement APIs, A/B testing on v1/v2/v3, learned format/media weighting in the Strategist,
  Slack/email approval notifications, per-client multi-brand support.

---

## 13. Repo map

```
marketing-brain/
├─ config/        agents.yaml · brand.yaml · providers.yaml
├─ schema/        airtable_schema.json
├─ marketing_brain/
│  ├─ orchestrator.py · settings.py · state.py · budget.py
│  ├─ control_plane/  base · airtable · sheets · local
│  ├─ agents/         discover · strategy · create · distribute · engage · analyze
│  ├─ providers/      llm + 5 media adapters (mock + _live)
│  └─ pipelines/
├─ scripts/       run_stage · setup_airtable · simulate_approval
├─ .github/workflows/  ci · discover · create · publish · engage · analyze
└─ tests/         control-plane + full-loop-with-human-gate
```
