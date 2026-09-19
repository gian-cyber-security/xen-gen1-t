# XEN-GEN1-T

Standalone repository for the XEN-GEN1-T text model.

## Purpose
XEN-GEN1-T is the text intelligence family for conversation, coding, reasoning, mathematics, and general text generation. It uses a byte-level UTF-8 tokenizer and a decoder-only Transformer trained from scratch.

## Supported platforms

- Windows
- Linux
- macOS

## Install

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If your system uses `python` for Python 3, you can use `python` instead of `python3`.

## Dataset

Create `datasets/train.jsonl`:

```json
{"instruction":"What is 2 + 2?","response":"4"}
{"instruction":"Explain what a variable is in programming.","response":"A variable stores a value that a program can read or change."}
```

## Train

```bash
python training/train.py --data datasets/train.jsonl --output outputs/xen --steps 1000
```

The default configuration targets the RTX 4060 8GB + 32GB RAM development machine. More training data and steps are needed for better capability.

## Generate locally

```bash
python inference/generate.py --model-dir outputs/xen --prompt "Explain recursion simply" --max-new-tokens 128
```

CUDA is used automatically when available; CPU fallback is supported.

## Model files

- `model/` — architecture, tokenizer, and loader.
- `training/` — training code.
- `inference/` — local text generation.
- `configs/system_prompt_t.txt` — GEN1-T system behavior and prompt-injection rules.

XEN-GEN1-T is a research/development model trained from scratch, not a pretrained commercial LLM.

## License

MIT
