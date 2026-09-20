import argparse
import json
import random
import yaml
import torch
from pathlib import Path
from torch.utils.data import Dataset, DataLoader, random_split
from model.config import XENConfig
from model.model import XENModel
from model.tokenizer import XENTokenizer

class DS(Dataset):
    def __init__(self, rows, tokenizer, max_len):
        self.rows, self.t, self.m = rows, tokenizer, max_len
    def __len__(self):
        return len(self.rows)
    def __getitem__(self, i):
        row = self.rows[i]
        ids = self.t.encode(str(row.get("instruction","")) + "\n" + str(row.get("response","")), self.m)
        ids += [0] * (self.m - len(ids))
        x = torch.tensor(ids[:-1], dtype=torch.long)
        y = torch.tensor(ids[1:], dtype=torch.long)
        y[y == 0] = -100
        return x, y

def load_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if "instruction" not in row or "response" not in row:
                raise ValueError(f"Missing instruction/response at line {n}")
            rows.append(row)
    if not rows:
        raise ValueError("Dataset is empty")
    return rows

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="datasets/train.jsonl")
    p.add_argument("--output", default="outputs/xen")
    p.add_argument("--steps", type=int, default=1000)
    p.add_argument("--resume", default=None)
    p.add_argument("--config", default="configs/train.yaml")
    a = p.parse_args()

    with open(a.config, encoding="utf-8") as f:
        tc = yaml.safe_load(f) or {}

    seed = int(tc.get("seed", 42))
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    t = XENTokenizer()
    t.fit()
    cfg = XENConfig(
        vocab_size=int(tc.get("vocab_size",260)),
        max_seq_len=int(tc.get("max_seq_len",512)),
        d_model=int(tc.get("d_model",512)),
        n_heads=int(tc.get("n_heads",8)),
        n_layers=int(tc.get("n_layers",12)),
        ffn_mult=float(tc.get("ffn_mult",2.6666666667)),
        dropout=float(tc.get("dropout",0.0)),
        rope_theta=float(tc.get("rope_theta",10000.0)),
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = XENModel(cfg).to(device)
    rows = load_rows(a.data)

    val_fraction = float(tc.get("validation_split",0.02))
    val_size = max(1, int(len(rows) * val_fraction)) if len(rows) > 20 else 0
    if val_size:
        train_rows, val_rows = random_split(
            rows, [len(rows)-val_size, val_size],
            generator=torch.Generator().manual_seed(seed)
        )
        train_rows, val_rows = list(train_rows), list(val_rows)
    else:
        train_rows, val_rows = rows, []

    batch_size = int(tc.get("batch_size",2))
    grad_accum = max(1, int(tc.get("gradient_accumulation",1)))
    loader = DataLoader(DS(train_rows,t,cfg.max_seq_len), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(DS(val_rows,t,cfg.max_seq_len), batch_size=batch_size) if val_rows else None

    base_lr = float(tc.get("learning_rate",3e-4))
    optimizer = torch.optim.AdamW(model.parameters(), lr=base_lr, weight_decay=float(tc.get("weight_decay",0.1)))
    warmup = int(tc.get("warmup_steps",200))
    log_every = int(tc.get("log_every",20))
    save_every = int(tc.get("save_every",500))
    max_norm = float(tc.get("max_grad_norm",1.0))

    out = Path(a.output)
    out.mkdir(parents=True, exist_ok=True)
    step = 0
    data_iter = iter(loader)

    if a.resume:
        ckpt = torch.load(a.resume, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model"])
        optimizer.load_state_dict(ckpt["optimizer"])
        step = int(ckpt.get("step",0))
        print(f"Resumed from step={step}")

    model.train()
    while step < a.steps:
        optimizer.zero_grad(set_to_none=True)
        total_loss = 0.0
        for _ in range(grad_accum):
            try:
                x, y = next(data_iter)
            except StopIteration:
                data_iter = iter(loader)
                x, y = next(data_iter)
            x, y = x.to(device), y.to(device)
            _, loss = model(x,y)
            (loss / grad_accum).backward()
            total_loss += loss.item()

        if warmup > 0 and step < warmup:
            lr = base_lr * float(step+1) / warmup
            for group in optimizer.param_groups:
                group["lr"] = lr
        else:
            for group in optimizer.param_groups:
                group["lr"] = base_lr

        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
        optimizer.step()
        step += 1

        if step % log_every == 0:
            print(f"step={step} loss={total_loss/grad_accum:.5f} lr={optimizer.param_groups[0]['lr']:.2e}")

        if step % save_every == 0:
            torch.save({"config":cfg.__dict__,"model":model.state_dict(),"optimizer":optimizer.state_dict(),"step":step}, out / f"checkpoint-{step}.pt")
            print(f"checkpoint saved: step={step}")

    model.eval()
    if val_loader:
        total = 0.0
        count = 0
        with torch.no_grad():
            for x,y in val_loader:
                _, loss = model(x.to(device),y.to(device))
                total += loss.item()
                count += 1
        print(f"validation_loss={total/max(1,count):.5f}")

    torch.save({"config":cfg.__dict__,"model":model.state_dict()}, out/"model.pt")
    t.save(out/"tokenizer.json")
    print(f"model saved: {out/'model.pt'}")

if __name__ == "__main__":
    main()
