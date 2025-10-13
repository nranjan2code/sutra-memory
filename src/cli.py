import argparse
import asyncio
from typing import List

from .biological_trainer import BiologicalTrainer


def cmd_train(args: argparse.Namespace) -> None:
    async def run():
        t = BiologicalTrainer(base_path=args.base, workspace_id=args.workspace)
        await t.train_from_stream(args.text)
        if args.save:
            t.save_memory(args.save)
        stats = t._get_memory_stats()
        print(stats)
    asyncio.run(run())


def cmd_query(args: argparse.Namespace) -> None:
    t = BiologicalTrainer(base_path=args.base, workspace_id=args.workspace)
    if args.load:
        t.load_memory(args.load)
    res = t.query_knowledge(" ".join(args.terms), max_results=args.top)
    for r in res:
        print(f"{r['relevance']:.3f}\t{r['memory_type']}\t{r['content']}")


def cmd_save(args: argparse.Namespace) -> None:
    t = BiologicalTrainer(base_path=args.base, workspace_id=args.workspace)
    t.load_memory(args.base)
    t.save_memory(args.base)
    print(f"Saved to {args.base}")


def cmd_load(args: argparse.Namespace) -> None:
    t = BiologicalTrainer(base_path=args.base, workspace_id=args.workspace)
    t.load_memory(args.base)
    print(t._get_memory_stats())


def main():
    p = argparse.ArgumentParser(prog="sutra-models")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_train = sub.add_parser("train", help="Train from text inputs")
    p_train.add_argument("text", nargs="+", help="Input text strings")
    p_train.add_argument("--save", help="Base path to save memory after training")
    p_train.add_argument("--base", default="knowledge_store", help="Base path for PBSS store")
    p_train.add_argument("--workspace", default="core", help="Workspace ID")
    p_train.set_defaults(func=cmd_train)

    p_query = sub.add_parser("query", help="Query knowledge store")
    p_query.add_argument("terms", nargs="+", help="Query terms")
    p_query.add_argument("--load", help="Base path to load memory before querying")
    p_query.add_argument("--top", type=int, default=10, help="Top results to show")
    p_query.add_argument("--base", default="knowledge_store", help="Base path for PBSS store")
    p_query.add_argument("--workspace", default="core", help="Workspace ID")
    p_query.set_defaults(func=cmd_query)

    p_save = sub.add_parser("save", help="Save current memory (after load)")
    p_save.add_argument("base", help="Base path of the knowledge store")
    p_save.add_argument("--workspace", default="core", help="Workspace ID")
    p_save.set_defaults(func=cmd_save)

    p_load = sub.add_parser("load", help="Load and print memory stats")
    p_load.add_argument("base", help="Base path of the knowledge store")
    p_load.add_argument("--workspace", default="core", help="Workspace ID")
    p_load.set_defaults(func=cmd_load)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()