# Quickstart

Install:
- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

Demo:
- python3 -c "from src.biological_trainer import demonstrate_biological_training; import asyncio; asyncio.run(demonstrate_biological_training())"

Basic use:
- Train batch:
  - Use BiologicalTrainer().train_from_stream([...])
- Query:
  - trainer.query_knowledge("terms", max_results=10, hops=1)
- Save/Load:
  - trainer.save_memory("knowledge_store")
  - trainer.load_memory("knowledge_store")
