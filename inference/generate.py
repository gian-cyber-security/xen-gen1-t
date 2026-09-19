import argparse
import torch
from pathlib import Path
from model.config import XENConfig
from model.model import XENModel
from model.tokenizer import XENTokenizer
from tools.web_search import should_search, search_web, format_results

@torch.no_grad()
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-dir", default="outputs/xen")
    p.add_argument("--prompt", required=True)
    p.add_argument("--max-new-tokens", type=int, default=128)
    p.add_argument("--web-search", action="store_true")
    p.add_argument("--no-web-search", action="store_true")
    a = p.parse_args()

    d = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    z = torch.load(Path(a.model_dir) / "model.pt", map_location=d, weights_only=False)
    cfg = XENConfig(**z["config"])
    m = XENModel(cfg).to(d)
    m.load_state_dict(z["model"])
    m.eval()
    t = XENTokenizer.load(Path(a.model_dir) / "tokenizer.json")

    use_search = a.web_search or (should_search(a.prompt) and not a.no_web_search)
    prompt = a.prompt.strip()

    if use_search:
        context = format_results(search_web(prompt))
        if context:
            prompt = (
                "### User:\n" + prompt +
                "\n\n### Web Context:\n" + context +
                "\n\n### Assistant:\n"
            )
        else:
            prompt = "### User:\n" + prompt + "\n\n### Assistant:\n"
    else:
        prompt = "### User:\n" + prompt + "\n\n### Assistant:\n"

    ids_list = t.encode(prompt, cfg.max_seq_len)
    if ids_list and ids_list[-1] == 2:
        ids_list = ids_list[:-1]
    ids = torch.tensor([ids_list], device=d)

    for _ in range(a.max_new_tokens):
        logits, _ = m(ids[:, -cfg.max_seq_len:])
        nxt = logits[:, -1].argmax(-1, keepdim=True)
        ids = torch.cat([ids, nxt], 1)
        if nxt.item() == 2:
            break

    print(t.decode(ids[0].tolist()[len(ids_list):]))

if __name__ == "__main__":
    main()
