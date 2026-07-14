# Semantic search & models

Synapse's semantic layer lets `syn search` match **meaning**, not just keywords, and discover entities from your prose. It ships **in the default binary** (opt-out) but its models are **downloaded only with your consent**, and once they're local, everything runs **on-device and offline**.

---

## What you get

- **Hybrid search**: `syn search` fuses full-text (FTS), vector similarity, and graph-neighbourhood, so `syn search "the payments decision"` finds the right note even if it says "pagamentos", never "payments".
- **Meaning-only / keyword-only**: `syn search --semantic <q>` (vector only) or `syn search --no-vector <q>` (keyword + graph, no model load).
- **Entity discovery**: mentions of people/tools in what you write become *proposals* to add new entities (you accept them; nothing is created silently).

Without the models, Synapse is still a fully functional **keyword + graph** memory (`syn search`, `syn graph`, the MCP server). You only lose meaning-search and auto-discovery.

## The models

Two on-device models, run on CPU (no GPU, no Python):

| Job | Default model | Size | Languages |
|---|---|---|---|
| Embeddings | BGE-M3 (fp32) | ~2.2 GB | multilingual (en, pt, es, fr, de, …) |
| NER (entity discovery) | GLiNER-multi | ~350 MB | multilingual |

**~2.5 GB total**, downloaded **once** and shared across every workspace on the machine (measured; corrected from an earlier ~920 MB estimate).

**Quality vs speed.** The guided `syn init` asks which embedding profile you want: `bge-m3` fp32 (above, max recall, the default) or `bge-m3-int8` (~560 MB, lighter & faster, small recall cost; **~900 MB total** with the NER model). Both are 1024-dim (the same vector space) so switching is just a re-embed.

**Lighter English-only opt-downs (~325 MB total):** `bge-small-en-v1.5-q` (~65 MB) + `gliner-base-en` (~260 MB). Set them in `.synapse/config.toml` (`[enrichment]`).

## Downloading, on your consent, never silently

- **`syn init`** offers the download on a fresh, interactive setup: `Download the models now? [Y/n]`.
- **`syn embed --all`** downloads (if needed) and embeds everything, run it any time to turn semantic search on.
- **`syn embed --check`** is read-only: it reports `models_ready: true/false` without downloading anything.

Until the models are present, writes still save (without embeddings) and search falls back to keyword + graph. Nothing blocks; nothing downloads behind your back.

Cached under your OS cache dir (`~/Library/Caches/synapse/models/` on macOS, `~/.cache/synapse/models/` on Linux). Override with `SYNAPSE_MODEL_CACHE=/path`.

## Privacy

**Local-first.** The model files are fetched once over HTTPS from Hugging Face. That request sends nothing about your data, only `GET`s for the model. After that, every embedding and search runs **on your machine**. Your notes, entities, and queries never leave it. Synapse ships **no telemetry**.

(An opt-in hosted-embedding mode exists for users who prefer not to run local models; it is **off** unless you configure a provider, and it sends entity text to that third party. Local is the default.)

## Compatibility

- **CPU-only**, no GPU required.
- **Apple Silicon** Macs (Intel Macs are **not** supported, see [README](./README.md)).
- **Linux** needs **glibc ≥ 2.38** for semantic search (Ubuntu 24.04+, Debian 13+, Fedora 39+). On older distros the keyword + graph + MCP features still work.
- Windows x86_64.
- First run is dominated by the download (budget a minute or two); inference is fast thereafter.

## Managing the cache

```bash
syn embed --check          # state (read-only)
syn embed --all            # download + embed everything (idempotent)
syn embed --reset-cache    # drop vectors to force a clean re-embed
```

Switch models by editing `embedding_model` / `ner_model` in `.synapse/config.toml`, then `syn embed --all` (re-embeds only what changed).
