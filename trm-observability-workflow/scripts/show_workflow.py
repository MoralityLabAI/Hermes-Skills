from __future__ import annotations


STEPS = [
    "1. bootstrap the harness checkout",
    "2. collect teacher traces with the bounded env contract",
    "3. build TRM rows from the replay JSONL",
    "4. merge only families that clear the floor",
    "5. train retriever, critic, router, and corrector separately",
    "6. bench each component on held rows",
]


def main() -> None:
    for step in STEPS:
        print(step)


if __name__ == "__main__":
    main()
