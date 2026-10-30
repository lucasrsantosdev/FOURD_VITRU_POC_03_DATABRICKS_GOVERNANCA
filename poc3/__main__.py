from pathlib import Path
import argparse
import json
from .pipeline import run_pipeline

def main() -> None:
    parser=argparse.ArgumentParser(description='POC 03 FourD / Vitru - simula lakehouse financeiro')
    repo=Path(__file__).resolve().parents[1]
    parser.add_argument('--entrada',type=Path,default=repo/'dados_ficticios')
    parser.add_argument('--saida',type=Path,default=repo/'saida_demo')
    args=parser.parse_args()
    print(json.dumps(run_pipeline(args.entrada,args.saida),ensure_ascii=False,indent=2))
    print(f'\nRelatorio visual: {args.saida.resolve() / "RELATORIO_VISUAL.html"}')

if __name__=='__main__':
    main()
