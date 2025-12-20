from rag.memory_ingest import MemoryIngestor

mi = MemoryIngestor()
mi.ingest("conv-1", "user", "I like Python for backend systems")
mi.ingest("conv-1", "assistant", "Python is great for rapid development")

print("Memory vectors ingested.")
