from rag.augment import augment_prompt
from infra.settings import MAX_CONTEXT_CHARS

user_q = "What is ransomware?"
chunks = [
    "Ransomware is malware that encrypts files.",
    "Attackers demand payment for decryption."
]

aug = augment_prompt(user_q, chunks)

print(aug)
assert "Context:" in aug
assert "Question:" in aug
assert len(aug) <= MAX_CONTEXT_CHARS
