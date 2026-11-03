from dataclasses import dataclass

SEEDS = {"Orange": 0xFF9130, "Blue": 0x3D7BFF, "Green": 0x3FA35B, "Pink": 0xE0457B}


@dataclass(frozen=True)
class Variant:
    dark: bool
    seed_name: str

    @property
    def mode(self) -> str:
        return "Dark" if self.dark else "Light"

    @property
    def name(self) -> str:
        return f"MD3-{self.mode}-{self.seed_name}"

    @property
    def seed(self) -> int:
        return SEEDS[self.seed_name]


VARIANTS = [Variant(dark, seed_name) for dark in (True, False) for seed_name in SEEDS]


def select(names: list[str] | None) -> list[Variant]:
    """Variants by name, case-insensitive, `MD3-` prefix optional. No names selects all."""
    if not names:
        return VARIANTS
    by_name = {v.name.lower(): v for v in VARIANTS}
    selected = []
    for name in names:
        key = name.lower() if name.lower().startswith("md3-") else f"md3-{name.lower()}"
        if key not in by_name:
            raise ValueError(f"unknown variant {name!r}; choose from: {', '.join(v.name for v in VARIANTS)}")
        selected.append(by_name[key])
    return selected
