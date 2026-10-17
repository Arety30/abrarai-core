# abrarai-core

`abrarai-core` is the engine package behind ABRARAI, Syed Abrar Ali's local, offline-first assistant. It solves the problem of running one assistant codebase on very different machines (a 16 GB laptop, an 8 GB desktop, a phone running Termux) without manually picking models or exposing the shell: the package profiles the host, assigns a compute tier, maps each user intent to a local model name that fits that tier, keeps a persistent JSON ledger of the session, and executes OS commands only through a whitelisted, shell-free bridge. Two thin front-ends (a terminal client and a CustomTkinter desktop window) sit on top of the same orchestrator.

## Where it is used

This package is the foundation layer for Abrar's local-assistant experiments on his Ubuntu laptop. The GUI and CLI in `dist_scripts/` are the pieces a user launches; the `core/`, `adapters/` and `pipelines/` modules are meant to be imported by other front-ends (voice, workspace ingestion) as they are built. Model inference is intended to go through a local Ollama server; at this stage of the code the orchestrator still returns a stand-in response instead of calling a model, so the package currently exercises the routing, state and sandboxing logic rather than real generation.

## How it works

Request flow for one message:

1. A front-end creates `AbrarOrchestrator` (`core/abrar_ai_1.py`).
2. On construction the orchestrator runs `DeviceProfiler`, which reads total RAM with `psutil` and assigns a tier: `EXPERT` (>= 16 GB), `BALANCED` (>= 8 GB) or `LITE` (anything less). The tier is written to the state file.
3. `execute_task(intent, prompt, arguments=None)` asks `RoutingEngine` for the model that serves `intent` in the active tier, logs the user turn to the state ledger, then:
   - if `intent == "SYSTEM_CONTROL"` and `arguments` holds `{"command": ..., "args": [...]}`, the command goes through `OSBridge.execute_sanitized_command`, which rejects anything not in the per-platform whitelist and runs the rest with `subprocess.run(list, shell=False)`;
   - otherwise it returns a mock `"[Response from <model>] Processing request: ..."` string (the hook where a real Ollama call belongs).
4. Every turn (user, assistant or system) is appended to `conversation_history` tagged with the model that handled it. History is capped at 30 entries.

Tier-to-model routing table (`core/routing_engine.py`):

| Tier | VOICE_LIVE | CODING | GENERAL |
|------|-----------|--------|---------|
| EXPERT | gemma2:2b | deepseek-r1:7b | llama3.2:3b |
| BALANCED | gemma2:2b | qwen2.5:3b | llama3.2:3b |
| LITE | gemma2:2b | deepseek-r1:1.5b | llama3.2:1b |

Unknown intents fall back to `GENERAL`; unknown tiers fall back to `LITE`.

Command whitelist (`adapters/os_bridge.py`): Ubuntu `ls pwd mkdir rmdir echo`; generic Linux/Termux `ls pwd mkdir echo`; macOS `ls pwd mkdir echo`; Windows `dir cd mkdir echo`. The platform key is `ubuntu` when `platform.version()` contains "ubuntu", otherwise `platform.system().lower()`.

| File | Role |
|------|------|
| `core/abrar_ai_1.py` | `AbrarOrchestrator`: wires profiler, state, bridge and router; `__main__` runs a three-step self-test |
| `core/routing_engine.py` | Intent x tier to model-name lookup |
| `core/state_manager.py` | JSON ledger (`core/state.json`): load/save, `update_metric`, `append_chat_history` (30-turn cap), `flush_history` |
| `adapters/device_profiler.py` | OS + RAM detection, tier assignment |
| `adapters/os_bridge.py` | Path normalisation and whitelisted, shell-free command execution |
| `pipelines/ingestion.py` | `IngestionPipeline`: walk a directory and collect text of files with allowed extensions; extract a zip bundle |
| `pipelines/voice_live.py` | `VoiceLivePipeline`: placeholder methods for mic capture, VAD, Whisper STT and streaming TTS (no real audio code yet) |
| `dist_scripts/cli_chat.py` | Terminal loop; every prompt is sent with intent `GENERAL` |
| `dist_scripts/gui_app.py` | CustomTkinter window (sidebar with tier, chat area, input). Prompts starting with `ls`, `pwd` or `mkdir` are sent as `SYSTEM_CONTROL`, everything else as `GENERAL`; work runs in a thread |
| `config/settings.json` | Intended settings (Ollama host, voice/VAD options, ingestion limits, security flags). No module reads it yet |

Storage: a single JSON file, `core/state.json`, next to the core module. No database, no network services are contacted in the current code.

## Setup

Requirements: Python 3.9+, `psutil`; `customtkinter` for the GUI (Tk must be available, e.g. `python3-tk` on Debian/Ubuntu). Ollama is not required yet.

```bash
git clone <repo-url> ~/abrarai-core
cd ~/abrarai-core
python3 -m venv .venv && source .venv/bin/activate
pip install psutil customtkinter
```

Configuration lives in `config/settings.json` (placeholders shown; the file is not consumed by code yet, so editing it has no runtime effect today):

```json
{
  "ollama_host": "http://localhost:11434",
  "voice_settings": {"vad_threshold": 0.5, "stt_model_size": "base.en", "tts_voice_engine": "piper", "barge_in_enabled": true},
  "ingestion": {"max_file_size_mb": 25, "allowed_extensions": [".txt", ".py", ".json", ".md"]},
  "security": {"strict_mode": true, "sandbox_file_access": true}
}
```

## Usage

```bash
# terminal client
python3 dist_scripts/cli_chat.py
# [You]: how do I set up a pipeline?
# [llama3.2:3b]: [Response from llama3.2:3b] Processing request: 'how do I set up a pipeline?'

# desktop window
python3 dist_scripts/gui_app.py
# typing "ls -la" runs through the OSBridge sandbox; "rm -rf /" is refused

# end-to-end self-test (general intent, allowed command, blocked command)
python3 core/abrar_ai_1.py
```

Programmatic use:

```python
from core.abrar_ai_1 import AbrarOrchestrator
o = AbrarOrchestrator()
o.execute_task("SYSTEM_CONTROL", "list files", {"command": "ls", "args": ["-la"]})
```

## Project structure

```
abrarai-core/
├── adapters/
│   ├── device_profiler.py
│   └── os_bridge.py
├── config/
│   └── settings.json
├── core/
│   ├── abrar_ai_1.py        # orchestrator + self-test
│   ├── routing_engine.py
│   ├── state_manager.py
│   └── state.json           # runtime ledger (generated)
├── dist_scripts/
│   ├── cli_chat.py
│   └── gui_app.py
└── pipelines/
    ├── ingestion.py
    └── voice_live.py
```

## Limitations and notes

- No model is actually called yet: `execute_task` returns a mock string. The routing table only decides which model *would* be used.
- `config/settings.json` is documentation of intended settings; nothing loads it.
- `core/state.json` is a runtime file that fills with conversation history and raw command output. Treat it as generated data (add it to `.gitignore`) rather than committing it.
- `VoiceLivePipeline` methods are stubs that log and return constants.
- The GUI's intent detection is a prefix check on `ls`, `pwd`, `mkdir`; the CLI sends everything as `GENERAL`.
- The GUI sidebar label "HOST: Ubuntu Linux" is hard-coded rather than read from the profiler.
- The whitelist allows `mkdir`/`rmdir`, so the sandbox prevents arbitrary commands but not all filesystem changes.
