def _build_spawn_schedule(total: int, minutes: int) -> list[int]:
    """
    Distributes `total` cars across `minutes` slots as evenly as possible.
    The remainder is spread across the first slots.

    Example: 95 cars over 30 minutes → 5 slots get 4 cars, 25 slots get 3 cars.
    """
    base, remainder = divmod(total, minutes)
    return [base + (1 if i < remainder else 0) for i in range(minutes)]