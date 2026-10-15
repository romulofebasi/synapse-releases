# Semantic search & models

Synapse can combine keyword, graph and semantic retrieval. Semantic search depends on a compatible installed release, selected model and available local resources. Models are downloaded with consent; local inference and explicitly configured hosted providers have different privacy boundaries.

## What you get

- **Hybrid retrieval:** combines supported keyword, vector and graph signals. A related concept can match without an exact word overlap; the result is not guaranteed.
- **Meaning-only or keyword-oriented retrieval:** discover `syn search --semantic` and `syn search --no-vector` in the installed command help.
- **Entity discovery:** supported enrichment can suggest entities for explicit proposal/review. A model suggestion is not an accepted fact or an authorization grant.

A compatible executable can support keyword and graph queries without selected semantic models. Missing vectors and a binary that cannot load on the operating system are different failures.

## The models

Historical default profiles use CPU ONNX models:

| Job/profile | Model | Approximate download footprint |
| :-- | :-- | :-- |
| Multilingual embedding, quality | BGE-M3 fp32 | 2.2 GB |
| Multilingual entity discovery | GLiNER-multi | 350 MB |
| Multilingual embedding, lighter profile | BGE-M3 int8 | 560 MB |
| English embedding, lighter option | BGE-small-en-v1.5 quantized | 65 MB |
| English entity discovery, lighter option | GLiNER-base-en | 260 MB |

The default multilingual pair is approximately 2.5 GB; the lighter multilingual pair is approximately 900 MB. These are model/profile estimates, not a universal installation size or a latency benchmark. Cache, index, runtime and retained workspace data require additional storage. Check the selected release's profiles and exact download list.

Quantization can change retrieval behavior. Equal dimensionality alone does not establish embedding-space compatibility; use the supported profile-switch/re-embedding procedure. Do not mix vectors from incompatible model versions or assume a quality/speed tradeoff has been measured for your corpus.

## Downloading, on your consent, never silently

Where supported:

```bash
syn embed --check
syn embed --all
```

Inspect command help before use. The readiness check does not request a download. The embed operation can download missing selected models and build vectors, so review the source, footprint and consent first. Interactive setup can offer the same choice; a missing model is not permission for an agent to download it unasked.

Historical caches use `~/Library/Caches/synapse/models/` on macOS or `~/.cache/synapse/models/` on Linux. `SYNAPSE_MODEL_CACHE` can override the supported cache location. Confirm behavior in your installed release before moving or pruning files.

## Privacy

| Configuration | Content boundary |
| :-- | :-- |
| Local models already present | Embedding and model-backed search process locally. |
| Model download | Network requests retrieve the selected artifacts; the host still exposes ordinary connection metadata to the download service. |
| Explicit hosted embeddings | Configured entity text or other selected inputs are sent to that provider under its service policy. |
| Remote integrations or connected MCP clients | Each connection has its own access, network and content policy. |

The npm launcher not downloading a binary at execution time does not make all `syn` commands network-free. Review the selected release, configuration, model sources and integrations before processing sensitive knowledge. Local processing is not an assurance of filesystem encryption or organizational access control.

## Compatibility

Published companion targets include Apple Silicon macOS, Linux x86_64/ARM64 and Windows x86_64. Intel macOS is not distributed in the current target matrix. Check the [selected release assets](https://github.com/romulofebasi/synapse-releases/releases) for exact availability.

Historical Linux semantic builds require a compatible glibc runtime, documented as glibc 2.38 or later. Check the artifact and runtime before installing. Disabling vectors cannot repair a binary or shared library that the operating system cannot load; do not assume older distributions will run every other command.

Download, initial indexing and subsequent queries have different resource costs. No fixed first-run duration, throughput or guaranteed recall is asserted here.

## Managing the cache

Inspect `syn embed --help` for the selected release's readiness, reset and re-embedding operations. A reset affects derived vectors; it is not permission to remove the entire `.synapse/` operational directory. Back up required source, policy, key, proposal and history state before recovery work.
