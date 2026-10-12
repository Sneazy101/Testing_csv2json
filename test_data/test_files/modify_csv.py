import random

SRC = "people-10000.csv"

rng = random.Random(42)

with open(SRC, encoding="utf-8") as f:
    lines = [line.rstrip("\n").rstrip("\r") for line in f if line.strip()]

width = max(len(line) for line in lines)    # pad every line to the same width so the new column aligns

with open(SRC, "w", encoding="utf-8", newline="") as f:
    f.write(lines[0].ljust(width) + ", HasPets\n")
    for line in lines[1:]:
        f.write(line.ljust(width) + ", " + rng.choice(["true", "false"]) + "\n")