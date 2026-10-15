# ASR + Speaker Diarization for an AGPL Medical Scribe

*Research note — 15 Oct 2026. Scope: open-weight models that can be shipped with, or used by,
an AGPL-3.0 app that records a clinician–patient consultation and produces an accurate,
speaker-attributed transcript ("who said what, when").*

> **Verification caveat.** The research sandbox could not reach huggingface.co or arxiv.org
> directly. GitHub READMEs, issue threads and the Open ASR Leaderboard CSVs were read at the
> source; Hugging Face model-card facts and arXiv numbers come from search-engine extracts and
> are marked **[via search]**. Re-check the license tag on every model card before you ship.
> Numbers are self-reported by the model authors unless stated otherwise.

---

## 1. TL;DR

| Question | Answer |
|---|---|
| Is MOSS-Transcribe-Diarize (MTD) **licence-compatible** with AGPL-3.0? | **Yes.** Apache-2.0 code; the README states the model is Apache-2.0. Apache-2.0 is compatible with (A)GPLv3. |
| Is it **technically attractive**? | **Yes, on paper.** It is a single 0.9B model that does transcription, diarization, timestamps and hotword prompting in one pass over long audio. It is small enough for a 16 GB GPU or an Apple-Silicon Mac via MLX (8-bit) or GGUF. |
| Is it **ready to be the sole engine** of a clinical scribe today? | **No.** The evidence base is Chinese-centric, with no clinical or English-consultation benchmark. Open, unfixed bugs include English prompts producing Chinese text, refusal text emitted on silence, transcripts truncated after about 40 min, and missing speaker tags. There is no streaming, and the project is only 3 months old. |
| Recommendation | Build an **engine-agnostic pipeline**. Keep MTD as a **candidate under evaluation**, not the default. Benchmark it against the two strongest licence-clean alternatives on PriMock57 and on your own (consented) audio: **(a)** VibeVoice-ASR (MIT, end-to-end, best open medical-term accuracy measured), and **(b)** a modular stack, **Nemotron-3-Diarization** (OpenMDW) + **Qwen3-ASR-1.7B** (Apache-2.0) or **Parakeet-TDT** (CC-BY-4.0). |
| Avoid | Bundling any CC-BY-**NC** or custom-restricted weights: DiariZen, Sortformer v1, original Canary-1B, CrisperWhisper, MedASR/MedGemma (HAI-DEF terms). Also avoid **raw** Whisper-large-v3 without VAD gating and verification (documented harmful hallucinations). |

---

## 2. What a medical scribe actually needs (evaluation criteria)

1. **Content accuracy on clinical vocabulary.** Drug names, doses, negations ("no chest pain"), laterality, numbers. Plain WER is a poor proxy: "WER is Unaware" (Ellis et al., IWSDS 2026) found WER correlates poorly with clinician-rated risk ([arXiv 2511.16544](https://arxiv.org/abs/2511.16544)). Medical-term WER (M-WER) and drug-name M-WER differ 3–5× between models whose overall WER is within 2–3 points ([Omi medical-STT-eval](https://github.com/Omi-Health/medical-STT-eval)).
2. **No fabrication.** Insertions of plausible but unspoken content are the most dangerous error class (see §6).
3. **Speaker attribution.** Clinician vs patient matters clinically: a symptom *reported* by the patient differs from a *hypothesis* voiced by the doctor. Consultations are usually 2 speakers but often 3–5 (relative, interpreter, student, nurse). Short back-channels ("yeah", "mm") are common, and overlap is frequent.
4. **Long-form robustness.** 5–60 min per encounter, with silences (examination, typing) that trigger hallucination in LLM-decoder models.
5. **Accents and code-switching.** Australian/British/non-native English, plus multilingual patients.
6. **Local / on-prem inference** for privacy. A practice PC with a consumer GPU or an Apple-Silicon Mac is a realistic target.
7. **Latency.** Batch after the consult is acceptable for a scribe. Streaming is a nice-to-have, for a live draft.
8. **Licence.** The weights and code must not add restrictions beyond AGPL-3.0 (AGPL §7/§10 "no further restrictions"). They must also allow commercial clinical use, since clinics are commercial entities.

---

## 3. MOSS-Transcribe-Diarize — detailed evaluation

### 3.1 Facts

| Item | Detail | Source |
|---|---|---|
| Developer | OpenMOSS / MOSI.AI (Xipeng Qiu group, Fudan/SII lineage), 24 authors | [arXiv 2601.01554](https://arxiv.org/abs/2601.01554) [via search] |
| Released | Tech report Jan 2026; **0.9B weights open-sourced 2026-07-09**; "Pro" version is playground/API-only | [GitHub README](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize) |
| Architecture | Whisper-Medium-config audio encoder → 4× temporal merge + MLP adaptor → Qwen3-0.6B-style causal decoder (audio-LLM). 16 kHz, 80-mel, 30 s feature chunks | README |
| Task | Speaker-Attributed, Time-Stamped transcription (SATS) in **one pass**; optional acoustic-event tags; hotword prompting | README |
| Output | `[start][S01]text[end]` segments, speaker tags `S01…Sxx` | README |
| Context | 128k tokens, "up to 90 minutes" claimed (but see bug #57 below) | arXiv abstract [via search] |
| Languages | "50+"; won 1st place, 2nd MLC-SLM Challenge (INTERSPEECH 2026, 14 languages, conversational 2-speaker task) | README |
| Licence | Repo `LICENSE` = **Apache-2.0** (verified). README: model "remains an OpenMOSS model under Apache-2.0". HF tag not directly verified | [LICENSE](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/main/LICENSE) |
| Training data | **Not disclosed.** One secondary summary claims ~150 h AISHELL-4 + ~200 h podcasts + ~50 h film/TV + ~100 h simulated, which is unverified and seems to describe only part of training. Issue #36 asking for data scale is unanswered. No medical data mentioned | [emergentmind](https://www.emergentmind.com/topics/moss-transcribe-diarize) [unverified], [#36](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/36) |
| Runtimes | HF Transformers 5.x (`trust_remote_code`), **SGLang-Omni** (recommended, OpenAI-compatible `/v1/audio/transcriptions`), vLLM nightly, FunASR ≥1.4.12; community **MLX** (8-bit matches bf16; 4/6-bit drift), **GGUF** via `moss-transcribe.cpp` (q5 recommended), CoreML (macOS 27+) | README; [mlx-audio](https://github.com/Blaizzy/mlx-audio); [MLX-8bit](https://huggingface.co/majentik/MOSS-Transcribe-Diarize-MLX-8bit), [GGUF](https://huggingface.co/mudler/moss-transcribe.cpp-gguf) [via search] |
| Speed | 1×H100, SGLang: long-form AISHELL-4 RTF ≈ 0.02 at concurrency 1 | README |
| VRAM | Maintainer estimate ~12 GB for 60 min audio; one user OOM on 24 GB at ~10 min with vLLM (unresolved). Eager attention is quadratic and OOMs | [#53](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/53) |
| Streaming | **None.** Maintainer (8 Oct 2026): a new streaming model will be released | [#60](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/60) |

### 3.2 Published accuracy

**Self-reported (README), CER / cpCER / Δcp, lower is better. These are mostly Chinese test sets.**

| Model | AISHELL-4 | AliMeeting | Podcast | Movies |
|---|---|---|---|---|
| ElevenLabs | 19.58 / 37.95 / 18.36 | 25.70 / 36.69 / 10.99 | 8.50 / 11.34 / 2.85 | 11.49 / 17.85 / 6.37 |
| Gemini 3 Pro | 22.75 / 27.43 / 4.68 | 26.75 / 32.84 / 6.09 | – | 8.62 / 14.73 / 6.11 |
| VibeVoice-ASR | 21.40 / 24.99 / 3.59 | 27.40 / 29.33 / 1.93 | 27.94 / 48.30 / 20.36 | 14.59 / 42.54 / 27.94 |
| **MTD 0.9B (open)** | 14.84 / 15.83 / 0.99 | 24.86 / 22.17 / −2.69 | 5.97 / 7.37 / 1.40 | 6.36 / 12.76 / 6.40 |
| MTD Pro (closed) | 13.78 / 14.02 / 0.24 | 18.22 / 13.94 / −4.27 | 4.46 / 6.97 / 2.51 | 5.86 / 11.78 / 5.92 |

**Independent (third-party), English-relevant.** These come from DiaScriber, a competing model's paper ([arXiv 2608.22796](https://arxiv.org/abs/2608.22796) [via search]), and were run on raw long-form audio without oracle segmentation:

| Test set | MTD 0.9B cpWER / DER | VibeVoice-ASR cpWER / DER | DiaScriber cpWER / DER |
|---|---|---|---|
| **AMI** (English meetings) | **17.7 / 24.0** | 71.7 / 119.6 | 10.3 / 5.5 |
| MLC-SLM-EN (English conversations) | **12.5** / – | – | 15.5 / – |
| Average over all sets | 23.3 | 28.9 | 11.8 |

Treat these with care. Microsoft reports VibeVoice AMI-IHM cpWER 20.4 / DER 11.9 itself, versus 71.7 / 119.6 in DiaScriber's runs, so prompt and setup choices swing results enormously. That alone is a reason to run our own benchmark.

**Clinical benchmarks:** **MTD has not been evaluated on any medical dataset** that I could find. It is absent from both Omi Health PriMock57 benchmarks (ASR and diarization), which are the only public clinical-consultation benchmarks covering current open models.

### 3.3 Open issues relevant to clinical safety

As of mid-Oct 2026 the repo shows 21 open issues and none closed. Several bear directly on a scribe:

| Issue | Problem | Clinical relevance |
|---|---|---|
| [#17](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/17) | Default (Chinese) prompt on English audio → **unrelated Chinese text**, no timestamps/speakers. Maintainer reproduced it and says "several similar reports". Workaround: append a strict format constraint to the prompt | Fabrication; requires a pinned, tested English prompt |
| [#59](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/59) | Digital-silence window → model emits **"I'm sorry, I can't assist with that request"** (and claims to be Qwen), committed as a 10 s segment | Classic LLM-decoder hallucination on silence; needs VAD gating |
| [#61](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/61) | Near-silence at end of audio → whole transcript collapses into one segment with no markers | Loss of speaker attribution |
| [#57](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/57), [#26](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/26) | Audio **> ~40 min stops early**, despite the 90-min claim. Also reproduced on MLX/M5. Workaround: 30-min chunks + external speaker re-linking (CAM++) | **Silent truncation** (dangerous: missing content looks like a complete note) |
| [#34](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/34) | Cut-offs and **repeated text** on long audio | Repetition loops |
| [#40](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/40) | Speaker tags sometimes missing on single-speaker audio | Parse failures |
| [#51](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/51) | Inaccurate timestamps | Hampers audio-linked verification UI |
| [#28](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/28) | English hotwords less effective than Chinese; English words come out in ALL CAPS | Weakens drug-name biasing via hotwords |
| [#60](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues/60) | In a community real-time pipeline (PR #58, external CAM++ embeddings), sub-second utterances split one speaker into four. This is not the core model, but it shows streaming is not solved | Back-channels in consultations are sub-second |

### 3.4 Assessment

**Strengths**
- Licence-clean (Apache-2.0), small (0.9B), runs locally on modest hardware, with Mac paths via MLX and GGUF.
- A true end-to-end SATS design. One model avoids the brittle "ASR words ↔ diarizer segments" alignment step that causes speaker-attribution errors at turn boundaries in cascaded pipelines.
- Best-in-class self-reported cpCER on Chinese meeting and podcast data. Good third-party English conversational numbers (MLC-SLM-EN cpWER 12.5) for its size, and a challenge win on 2-speaker conversations, which is the shape of a consultation.
- Hotword prompting could later carry a patient's medication list or a practice formulary.

**Weaknesses / risks for clinical use**
- **No clinical evidence at all**, and little English evidence from the authors; training data is undisclosed.
- **LLM-decoder failure modes are present and documented**: fabricated text on silence, refusal strings, language confusion, repetition, silent truncation. These are the same class of risk that made Whisper notorious in clinical use (§6).
- **Immaturity.** It has been open for 3 months, no issue has been closed yet, fixes are promised "in the next release", and the tooling needs nightly vLLM / SGLang-Omni (CUDA 12.9/13) builds.
- The closed "Pro" model is substantially better (AliMeeting cpCER 13.9 vs 22.2), so the open model is not the vendor's best effort.
- No streaming yet.
- Per-word confidence scores are not exposed (segment-level text only), which limits "highlight uncertain words" UX.

**Verdict:** *Suitable to integrate and benchmark; not yet suitable as the default production engine.*
Re-evaluate when (a) the next release lands with fixes for #17/#57/#59, and (b) it has been scored on
PriMock57 by us or Omi Health. If adopted, wrap it with the guards in §7.3.

---

## 4. Alternatives

### 4.1 End-to-end "who-said-what" models (single model does ASR + diarization)

| Model | Size | Licence (weights) | Native diarization | Key numbers | Notes |
|---|---|---|---|---|---|
| **MOSS-Transcribe-Diarize** | 0.9B | Apache-2.0 | Yes | See §3 | |
| **Microsoft VibeVoice-ASR** (Jan 2026) | ~7–9B (Qwen2.5 backbone) | **MIT** [via search] | Yes, 60 min/pass (64k tokens), hotwords, 50+ languages | Self: AMI-IHM DER 11.9 / cpWER 20.4. **PriMock57: WER 8.34, M-WER 1.81 (best open model), drug M-WER 4.5**; PriMock DER 8.2 with high false alarm 5.2%, speaker count right 15/15 | Needs a big GPU (H100 used by Omi, ~97 s per 7.5 min file). Streaming 1.5B/7B variants exist but streaming DER is much worse (17–18%). Microsoft: "do not recommend … commercial or real-world applications without further testing". [docs](https://github.com/microsoft/VibeVoice/blob/main/docs/vibevoice-asr.md) |
| **IBM granite-speech-4.1-2b-plus** (Apr 2026) | 2B | **Apache-2.0** | Speaker-attributed text (`[Speaker N]:`) + word timestamps | WDER 0.9% Fisher, 2.2% CallHome [via search]; base 4.1-2b Open-ASR mean WER 5.33 | Reported caps: ~9 min for speaker-attributed mode. No turn timing, no streaming. Older Granite 3.3-2B was poor on PriMock (M-WER 11.0). [repo](https://github.com/ibm-granite/granite-speech) |
| NVIDIA multitalker-parakeet-streaming-0.6b | 0.6B | NVIDIA Open Model License (custom) | Speaker-attributed streaming | **PriMock cpWER 34.2%** | Poor here; licence needs review |
| DiaScriber (Aug 2026) | Qwen3.5-Omni based | Weights not found | Yes | AMI cpWER 10.3 / DER 5.5 (self) | Research only for now; watch it |
| SpeakerLM (Alibaba, AAAI 2026) | – | No weights found | Yes | – | Research only |

### 4.2 Modular stacks (ASR model + separate diarizer + word-to-speaker alignment)

**ASR engines (English short-form Open ASR Leaderboard and PriMock57 clinical results)**

Open ASR numbers are from the [leaderboard CSV](https://github.com/huggingface/open_asr_leaderboard) (snapshot Mar 2026). PriMock numbers are from [Omi medical-STT-eval](https://github.com/Omi-Health/medical-STT-eval) (55 GP mock consults, British English).

| Model | Licence | Open-ASR avg WER | AMI WER | PriMock WER | **PriMock M-WER** | **Drug M-WER** | Notes |
|---|---|---|---|---|---|---|---|
| **Qwen3-ASR-1.7B** (+ Qwen3-ForcedAligner-0.6B) | Apache-2.0 | 5.76 | 10.56 | 9.00 | **3.14** | **7.1** | Best small open model on clinical terms; aligner gives word timestamps (≤5 min chunks); 30 languages. [repo](https://github.com/QwenLM/Qwen3-ASR) |
| Parakeet-TDT-1.1B | CC-BY-4.0 | – | – | 9.03 | 3.68 | 13.7 | Fast, runs on CPU/Metal via [parakeet.cpp](https://github.com/mudler/parakeet.cpp) |
| Parakeet-TDT-0.6B-v2 | CC-BY-4.0 | 6.05 | 11.16 | 10.75 | 4.60 | 15.7 | English; RTFx ~3400; native word timestamps; weak on African accents (Afrispeech) |
| Parakeet-TDT-0.6B-v3 | CC-BY-4.0 | 6.32 | 11.39 | 9.35 | 5.90 | **20.6** | Multilingual EU; poor on drug names |
| Cohere Transcribe 03-2026 (2B) | Apache-2.0 [secondary] | **5.42** (#1) | 8.13 | 11.81 | 4.32 | 14.8 | Leaderboard #1 but middling on drugs |
| Granite-speech-4.1-2b | Apache-2.0 | 5.33 [via search] | – | – | – | – | Not yet on PriMock |
| Voxtral-Mini-4B-Realtime-2602 | Apache-2.0 | 7.68 | 17.07 | 11.89 | 4.10 | 10.3 | Native streaming (80 ms–2.4 s delay); vLLM, ≥16 GB VRAM; no diarization |
| Whisper large-v3-turbo (MLX) | MIT | 7.83 | 16.13 | 11.65 | 4.70 | 12.2 | 99 languages; hallucination record (§6) |
| Whisper large-v3 | MIT | 7.44 | 15.95 | – | – | – | Higher hallucination rate than v2 (vendor report) |
| Kyutai STT-2.6B-en | CC-BY-4.0 | 6.40 | 12.17 | 11.20 | 5.21 | 14.0 | True streaming, MLX build |
| Canary-Qwen-2.5B | CC-BY-4.0 | 5.63 | 10.19 | 12.94 | 8.25 | 21.0 | 40 s training-audio limit, slow long-form |
| Google MedASR | **HAI-DEF terms** | – | – | **52.5** | 26.2 | 35.6 | Dictation model; fails on conversation; licence not AGPL-compatible |

API reference points on PriMock M-WER: Gemini 2.5/3 Pro 1.4–1.5, AssemblyAI medical 2.83, Deepgram Nova-3 Medical 3.17. The best open models (VibeVoice 1.81, Qwen3-ASR 3.14) are competitive with commercial medical APIs.

**Diarizers**

Clinical DER is from the [Omi clinical-diarization-benchmark](https://github.com/Omi-Health/clinical-diarization-benchmark): 15 PriMock57 consults, 2.4 h, ±250 ms collar, automatic speaker count.

| Diarizer | Weights licence | **Clinical DER** | Speaker count correct | General DER | Notes |
|---|---|---|---|---|---|
| pyannote Precision-3 | Closed API | 2.89 | 14/15 | – | Reference ceiling, not usable offline |
| **NVIDIA Nemotron-3-Diarization** (Sep 2026) | **OpenMDW-1.1** (permissive) [via search] | **4.80** | 14/15 | DIHARD3 12.7–13.6 (0.3–30 s latency) | Streaming Sortformer, **up to 8 speakers**, ~100M params; runs in parakeet.cpp (CPU/Metal/CUDA). Do **not** use the `-preview` repo (evaluation-only licence) |
| pyannote community-1 (pyannote.audio 4) | CC-BY-4.0, HF-gated | 6.62 | **9/15** | AMI-IHM 17.0, DIHARD3 20.2 | WhisperX default; under-counts speakers |
| Sortformer v1 (diar_sortformer_4spk-v1) | **CC-BY-NC-4.0** | 6.78 | 14/15 | – | **Not usable** (NC) |
| Streaming Sortformer v2.1 | NVIDIA Open Model License (reported; conflicting) | 7.97 | 3/15 | DIHARD3 20.2 | 4-speaker cap |
| VibeVoice-ASR (as diarizer) | MIT | 8.23 | 15/15 | – | High false alarm |
| DiariZen (BUT) | **CC-BY-NC-4.0** | – | – | AMI-SDM 13.9, DIHARD3 14.5 | Strong but **not usable** (NC) |
| 3D-Speaker (CAM++) | Apache-2.0 | – | – | AMI-SDM 21.8 | Mediocre; useful embeddings |

**Speaker-conditioned ASR:** DiCoW / SE-DiCoW (BUT, diarization-conditioned Whisper) has **CC-BY-4.0** weights. Its default diarizer is DiariZen (NC), so it would need pairing with Nemotron-3 or community-1. Reported AMI-SDM cpWER is 23.6 with real diarization. [repo](https://github.com/BUTSpeechFIT/DiCoW)

**Pipeline glue:** WhisperX (BSD-2; faster-whisper → wav2vec2 alignment → pyannote) is the familiar reference implementation. Its README calls its diarization "far from perfect". The per-language wav2vec2 aligner checkpoints have mixed licences.

---

## 5. Licensing for an AGPL-3.0 project

*Not legal advice; get a review before distribution.*

- AGPL-3.0 is compatible with **Apache-2.0, MIT, BSD**. The FSF lists **CC-BY-4.0** as GPLv3-compatible. Attribution must be preserved (NOTICE file).
- Weights fetched at runtime (rather than vendored in the repo or installer) are arguably separate works. Even so, **non-commercial (NC) or field-of-use licences make the app unusable for real clinics**, and conflict with AGPL §7 "further restrictions" if bundled. Keep them out of defaults entirely.
- HF "gating" (accept-terms click-through, e.g. pyannote) is an access mechanism, not a licence term. It still complicates zero-config installs, so a non-gated default is preferable.

| Status | Models |
|---|---|
| ✅ Bundle-safe | **MOSS-Transcribe-Diarize (Apache-2.0)**, Whisper/faster-whisper/whisper.cpp (MIT), WhisperX (BSD-2), VibeVoice-ASR (MIT), Qwen3-ASR + ForcedAligner (Apache), Granite Speech (Apache), Voxtral 2507 & Realtime-2602 (Apache), Cohere Transcribe (Apache, verify), Parakeet-TDT v2/v3/1.1B, Canary-1B-flash/v2, Canary-Qwen (CC-BY-4.0), Kyutai STT (CC-BY-4.0), pyannote 3.1 (MIT) & community-1 (CC-BY-4.0, gated), DiCoW (CC-BY-4.0), 3D-Speaker (Apache) |
| ⚠️ Likely OK, confirm | Nemotron-3-Diarization & Nemotron-3.5-ASR (OpenMDW-1.1, new permissive licence, OSI review pending) |
| ⚠️ Legal review required | NVIDIA Open Model License models (multitalker-parakeet, Streaming Sortformer v2.1) |
| ❌ Exclude | Canary-1B (original, NC), diar_sortformer_4spk-v1 (NC), DiariZen weights (NC), CrisperWhisper (non-commercial), MedASR / MedGemma (HAI-DEF terms: flow-down use restrictions, remote restriction rights), Nemotron-3-Diarization-preview (eval-only), any API-only model |

---

## 6. Hallucination: the key clinical hazard

- **Careless Whisper** (Koenecke et al., FAccT 2024). About **1%** of Whisper transcriptions contained entirely fabricated phrases or sentences, and **38%** of those were harmful (violence, false authority, invented medical content). The rate rose with long non-vocal pauses ([arXiv 2402.08021](https://arxiv.org/abs/2402.08021)).
- **AP investigation, Oct 2024.** Nabla's Whisper-based scribe (>30k clinicians, ~7M visits) invented content such as "hyperactivated antibiotics", and **deleted the source audio**, so errors could not be audited ([ABC/AP](https://abcnews.go.com/US/wireStory/researchers-ai-powered-transcription-tool-hospitals-invents-things-115170291)).
- **Any LLM-decoder model is at risk**: Whisper, MOSS (bugs #17/#59 above), VibeVoice, Qwen3-ASR, Granite, Voxtral. A 2026 study (HALAS) found all 7 SOTA models tested hallucinate ([arXiv 2606.23048](https://arxiv.org/abs/2606.23048)). Granite showed 49–57% repetition under 30% audio masking ([arXiv 2604.21276](https://arxiv.org/pdf/2604.21276)).
- **Transducer/CTC models are less prone to free-form invention.** They emit tokens aligned to frames, which makes them a good *cross-check* engine. The SHALLOW benchmark ranks Parakeet lowest on phonetic hallucinations ([arXiv 2510.16567](https://arxiv.org/html/2510.16567)).

---

## 7. Recommendation and plan

### 7.1 Architecture

Use one `TranscriptionEngine` interface that returns a common schema. Each segment carries `{speaker, start, end, text, words[{w, start, end, conf?}], engine, model_version}`, and engines are swappable via config. Ship with **two engine families**:

1. **End-to-end:** VibeVoice-ASR on a GPU host, or **MTD 0.9B** where hardware is modest (MLX-8bit / GGUF / 16 GB GPU).
2. **Modular:** Nemotron-3-Diarization (≤8 speakers) → Qwen3-ASR-1.7B + ForcedAligner (or Parakeet-TDT for CPU/Mac speed) → word-to-speaker assignment by timestamp overlap.

Running both and **diffing them** is cheap insurance. Regions where an LLM-decoder engine and a transducer engine disagree get highlighted for the clinician, ROVER-style.

### 7.2 Benchmark before choosing a default

- **Data:** PriMock57 (57 British GP mock consults, ~9 h; [paper](https://arxiv.org/abs/2204.00333); confirm audio licence in the Babylon repo). Reuse Omi Health's MIT-licensed harness and CC-BY-4.0 diarization labels so numbers are comparable. Add a small locally recorded, consented set of **Australian-accented** role-play consults (accents are under-represented in all public sets), including 3+ speaker and interpreter scenarios.
- **Metrics:** WER, **M-WER and drug M-WER**, **cpWER / tcpWER** (speaker-attributed), DER with speaker-count accuracy, **insertion-only hallucination rate on silence/noise segments** (inject 30–120 s silences and examination noise), **truncation check** (output end-time vs audio duration), RTF and peak memory on the target hardware (Mac M-series, RTX 4060/4090-class).
- **Clinical-risk review:** sample disagreements and score them with a clinician rubric, or an LLM-judge validated against clinicians (κ≈0.82 reported in "WER is Unaware").

### 7.3 If MOSS-Transcribe-Diarize is used: mandatory guards

1. **VAD-gate input.** Silero VAD (MIT), or the diarizer's speech mask. Never feed long non-speech spans, and drop any output that maps to non-speech audio (#59).
2. **Pin an explicit English prompt with a strict format constraint** (#17 workaround), plus a language hint. Validate every segment with a regex and re-run or flag failures (#40, #61).
3. **Chunk at ≤30 min**, with overlap and speaker re-linking via embeddings (#57/#26). Assert that transcript coverage reaches the audio end.
4. Set a generous `max_new_tokens`. Use SDPA/FlashAttention, never eager (OOM).
5. Run repetition and refusal-string detectors ("I'm sorry…", n-gram loops).
6. Pin the exact model revision hash; re-benchmark on every upgrade.

### 7.4 Product-level safeguards (any engine)

- **Retain the audio** (encrypted, retention policy configurable) with click-to-play from every transcript segment. Nabla's audio deletion is the cautionary example.
- Show low-confidence and disagreement spans. The clinician must review and sign off; the generated note is a draft.
- Run inference locally by default; no audio leaves the practice unless explicitly configured.
- Check the regulatory position (TGA / FDA / MDR) once the app moves beyond transcription into summarisation or coding suggestions.

### 7.5 Watch list

- MOSS next release (fixes to #17/#57/#59, promised streaming model).
- DiaScriber weights.
- Granite-speech-4.1-plus long-form support.
- VibeVoice-ASR smaller/quantised variants.
- PriMock results for Granite 4.1 and Cohere.
- OSI decision on OpenMDW-1.1.

---

## 8. Key sources

- MOSS-Transcribe-Diarize: [GitHub](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize) · [tech report arXiv 2601.01554](https://arxiv.org/abs/2601.01554) · [issues](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/issues) · [HF card](https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize)
- Third-party joint ASR+diarization comparison: [DiaScriber, arXiv 2608.22796](https://arxiv.org/abs/2608.22796)
- Clinical benchmarks: [Omi medical-STT-eval](https://github.com/Omi-Health/medical-STT-eval) · [Omi clinical-diarization-benchmark](https://github.com/Omi-Health/clinical-diarization-benchmark) · [PriMock57 paper](https://arxiv.org/abs/2204.00333) · [WER is Unaware](https://arxiv.org/abs/2511.16544)
- General ASR: [Open ASR Leaderboard](https://github.com/huggingface/open_asr_leaderboard)
- Models: [VibeVoice-ASR](https://github.com/microsoft/VibeVoice/blob/main/docs/vibevoice-asr.md) · [Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR) · [Granite Speech](https://github.com/ibm-granite/granite-speech) · [parakeet.cpp](https://github.com/mudler/parakeet.cpp) · [pyannote.audio](https://github.com/pyannote/pyannote-audio) · [WhisperX](https://github.com/m-bain/whisperX) · [whisper.cpp](https://github.com/ggml-org/whisper.cpp) · [Kyutai STT](https://github.com/kyutai-labs/delayed-streams-modeling) · [DiariZen](https://github.com/BUTSpeechFIT/DiariZen) · [DiCoW](https://github.com/BUTSpeechFIT/DiCoW) · [Voxtral Transcribe 2](https://mistral.ai/news/voxtral-transcribe-2) · [MedASR](https://github.com/google-health/medasr) / [HAI-DEF terms](https://developers.google.com/health-ai-developer-foundations/terms)
- Hallucination: [Careless Whisper](https://arxiv.org/abs/2402.08021) · [AP on Nabla](https://abcnews.go.com/US/wireStory/researchers-ai-powered-transcription-tool-hospitals-invents-things-115170291) · [HALAS](https://arxiv.org/abs/2606.23048) · [SHALLOW](https://arxiv.org/html/2510.16567)
