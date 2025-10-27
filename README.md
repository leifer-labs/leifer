# Leifer Framework (Meta Repository)

This repository provides the **shared infrastructure and orchestration layer** for the Leifer ecosystem — a distributed, AI-powered data platform built from modular components.

It does **not** contain application source code. Those live in private repositories (`leifer-core`, `leifer-repl`, `leifer-ai`, etc.) and may be open-sourced gradually as time permits (or not — no promises!).

This meta-repo exists to:
- Document the **overall architecture**
- Share common **docker-compose environments** and dev tools
- Host **demo assets** (e.g., walkthrough video, screen shots, etc.)
- Provide a **launch point** for anyone collaborating on Leifer

Stay tuned — pieces may surface here over time.

---

## Purpose
  
- Store shared configuration (scripts, workspace settings)
- Manage infrastructure level stuff (Docker compose, scripts, etc)
- Act as the root workspace for local development in VS Code
- Provide whatever other high level tools that are useful for leifer

> Before you do anything, [install uv](https://docs.astral.sh/uv/getting-started/installation)


## Demos

### REPL Walkthrough

For a quick tour of Leifer’s memory-driven AI agent system, check out the REPL runthrough video:

▶️ [ReplRunthrough](https://leifer-labs.github.io/leifer)

This demo shows how Leifer agents reason over datasets, and some of the tools for interacting with the environment. It’s the best starting point if you want to understand how the system actually thinks.

### Web UI Snapshots

Screenshots of the accompanying web interface can be found under [demos/web/](demos/web/). These illustrate some of the supporting tools (dashboard, dataset browser, etc.) used to interact with the system in a more visual way. 

## Activity

Since all the source in this project is still private, we've generated our own activity log based on the commit logs of each of the `leifer` modules.

![Activity](docs/activity.svg)

## Usage

Clone this repository and each `leifer-*` project can be cloned inside of it.  

You'll end up with something like
```text
leifer/
├── compose/              # docker compose files
├── scripts/              # Utility and setup scripts
├── docs/                 # Framework-level notes
├── .vscode/              # THIS Workspace configuration
├── workspaces/           # workspaces for different bits
├── leifer-core/          # External repo clone (ignored)
├── leifer-ai/            # External repo clone (ignored)
...other leifer-* clones
```
There are two "starter" workspaces - one for the main leifer development projects and another for the web interface and api.  You should make your own copies of those and adjust to however you like.  

> Note: if you open one of the workspaces prior to cloning the repos in it, you're going to have some errors.

The main reason things are laid out the way they are is so that each of the individual projects can be worked on independently.  So you can clone this repo if you will be working on things that will benefit or be needed by the project as a whole (like docker infrastructure, deployment scripts, docs, etc) or you can clone an individual repo and work on it in isolation (Add Folder to Workspace).

## Dev Stack

The `docker-compose` file defines the core backing services used by the Leifer ecosystem for data orchestration, AI workflows, and memory systems.

### Services

**redis-stack**
A full Redis stack with vector support.
Used as a fast in-memory store for:
- Short-term memory in LangGraph workflows (semantically searchable).
- Pub/sub messaging for background task coordination.
- Checkpointing and caching during agent runs (hitl).

**mongodb**
MongoDB 7.0, used as the primary metadata store.
Stores:
- Dataset/Inventory metadata


**PostgreSQL**
Used for structured datasets that require relational querying. 
Stores:
- sample data.

**weaviate**
A vector-native database used for long-term memory.  This is where we store
conceptual memories.
Stores:
- Canonical concepts and synonyms
- Embedding-based memory

**AI**
There are a couple of more parts of the stack: mainstream LLMs and LM Studio.

The mainstream LLMs are used for the actual agents and LM Studio for embeddings. You can configure whatever models you want but, at least so far in the development effort, `gpt-4.1-mini` has been the goto for the planner (reasoning) agent AND for execution agent. We have tried a lot of different things for the embedder and will likely try a bunch more still.  Currently, we are using the (very high dimension) `text-embedding-jina-embeddings-v4-text-retrieval`.

For the other agents (e.g., analysis and concept extraction) we have tried a variety of things...some LM Studio ones did ok but just in the interest of keeping things consistent during dev, we are currently using `gpt-4.1-mini` for those as well (`temperatures` on all of these are low).
