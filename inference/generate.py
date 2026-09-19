import argparse,torch
from pathlib import Path
from model.config import XENConfig
from model.model import XENModel
from model.tokenizer import XENTokenizer
@torch.no_grad()
def main():
 p=argparse.ArgumentParser(); p.add_argument('--model-dir',default='outputs/xen'); p.add_argument('--prompt',required=True); p.add_argument('--max-new-tokens',type=int,default=128); a=p.parse_args(); d=torch.device('cuda' if torch.cuda.is_available() else 'cpu'); z=torch.load(Path(a.model_dir)/'model.pt',map_location=d,weights_only=False); cfg=XENConfig(**z['config']); m=XENModel(cfg).to(d); m.load_state_dict(z['model']); m.eval(); t=XENTokenizer.load(Path(a.model_dir)/'tokenizer.json'); ids=torch.tensor([t.encode(a.prompt,cfg.max_seq_len)],device=d)
 for _ in range(a.max_new_tokens):
  logits,_=m(ids[:,-cfg.max_seq_len:]); nxt=logits[:,-1].argmax(-1,keepdim=True); ids=torch.cat([ids,nxt],1)
  if nxt.item()==2: break
 print(t.decode(ids[0].tolist()))
if __name__=='__main__': main()
