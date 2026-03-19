KNOWN_CATEGORIES = {
    "dining",
    "groceries",
    "travel",
    "gas",
    "online_shopping",
    "entertainment",
    "utilities",
    "drugstores",
    "other",
}

MCC_MAPPINGS = [
    ((4511, 4511), "travel"),
    ((4722, 4722), "travel"),
    ((4900, 4900), "utilities"),
    ((5411, 5411), "groceries"),
    ((5541, 5542), "gas"),
    ((5732, 5732), "online_shopping"),
    ((5812, 5814), "dining"),
    ((5912, 5912), "drugstores"),
    ((5942, 5942), "online_shopping"),
    ((7832, 7833), "entertainment"),
]


def map_mcc_to_category(mcc_code):
    try:
        code = int(str(mcc_code).strip())
    except (TypeError, ValueError):
        return "other"

    for (start, end), category in MCC_MAPPINGS:
        if start <= code <= end:
            return category
    return "other"


def normalize_category(category):
    normalized = (category or "").strip().lower()
    return normalized if normalized in KNOWN_CATEGORIES else "other"

