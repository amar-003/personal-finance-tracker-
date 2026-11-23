"""Helpers for normalizing uploaded transaction CSV columns."""

from __future__ import annotations

import re

import pandas as pd

_REQUIRED_FIELDS = ("transaction_date", "description", "amount")
_COLUMN_ALIASES = {
    "transactiondate": "transaction_date",
    "date": "transaction_date",
    "transactionday": "transaction_date",
    "day": "transaction_date",
    "transdate": "transaction_date",
    "dateoftransaction": "transaction_date",
    "posteddate": "transaction_date",
    "postingdate": "transaction_date",
    "purchasedate": "transaction_date",
    "postdate": "transaction_date",
    "effectivedate": "transaction_date",
    "transactiontimestamp": "transaction_date",
    "effectivedate": "transaction_date",
    "transactiondatetime": "transaction_date",
    "transactiondateandtime": "transaction_date",
    "activitydate": "transaction_date",
    "description": "description",
    "transactiondescription": "description",
    "details": "description",
    "transactiondetails": "description",
    "merchant": "description",
    "merchantname": "description",
    "vendor": "description",
    "vendorname": "description",
    "businessname": "description",
    "transactionname": "description",
    "transactionmemo": "description",
    "counterparty": "description",
    "payee": "description",
    "memo": "description",
    "narration": "description",
    "name": "description",
    "descriptiondetails": "description",
    "merchantdetails": "description",
    "amount": "amount",
    "amt": "amount",
    "transactionamount": "amount",
    "transactionamt": "amount",
    "transamount": "amount",
    "netamount": "amount",
    "totalamount": "amount",
    "debit": "amount",
    "debitamount": "amount",
    "withdrawal": "amount",
    "withdrawals": "amount",
    "withdrawalamount": "amount",
    "transactionvalue": "amount",
    "netdebit": "amount",
    "credit": "amount",
    "creditamount": "amount",
    "spend": "amount",
    "spendamount": "amount",
    "amountspent": "amount",
    "totalspend": "amount",
    "netspend": "amount",
    "expense": "amount",
    "expenseamount": "amount",
    "purchaseamount": "amount",
    "paymentamount": "amount",
    "chargeamount": "amount",
    "amountpaid": "amount",
    "amountout": "amount",
    "moneyout": "amount",
    "outflow": "amount",
    "cost": "amount",
    "price": "amount",
    "value": "amount",
    "total": "amount",
    "category": "category",
    "categoryname": "category",
    "transactioncategory": "category",
    "expensecategory": "category",
    "expenseclassification": "category",
    "label": "category",
    "transactiontype": "category",
}


def _normalize_column_name(column: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(column).casefold())


_FIELD_KEYWORDS = {
    "transaction_date": ("date", "posted", "purchase", "transact"),
    "description": (
        "description",
        "detail",
        "merchant",
        "vendor",
        "payee",
        "memo",
        "narration",
        "counterparty",
        "name",
    ),
    "amount": (
        "amount",
        "amt",
        "debit",
        "credit",
        "withdraw",
        "spend",
        "expense",
        "purchase",
        "payment",
        "charge",
        "moneyout",
        "outflow",
        "cost",
        "price",
        "value",
        "total",
    ),
    "category": ("category", "classification", "expensecategory", "label", "type", "class"),
}


def _detect_column_field(column: object) -> tuple[str, int] | None:
    normalized = _normalize_column_name(column)
    direct = _COLUMN_ALIASES.get(normalized)
    if direct:
        if normalized == "transactiontype":
            return direct, 1
        aliases = [
            alias for alias, field in _COLUMN_ALIASES.items() if field == direct
        ]
        return direct, 100 - aliases.index(normalized)

    scores: dict[str, int] = {}
    priority_aliases = {
        "transaction_date": ("date", "posted", "purchased"),
        "description": ("description", "merchant", "vendor", "payee"),
        "amount": ("amount", "debit", "credit", "spend", "expense", "value", "total"),
        "category": ("category", "classification", "label", "type"),
    }
    for field, keywords in _FIELD_KEYWORDS.items():
        score = sum(2 for keyword in keywords if keyword in normalized)
        score += sum(
            3
            for alias in priority_aliases[field]
            if normalized == alias or normalized.endswith(alias)
        )
        if score:
            scores[field] = score
    if not scores:
        return None
    highest = max(scores.values())
    matches = [field for field, score in scores.items() if score == highest]
    if len(matches) == 1:
        return matches[0], 1 if normalized == "type" else 20
    return None


_CATEGORY_RULES = (
    ("Housing", ("rent", "lease", "mortgage", "apartment")),
    ("Groceries", ("grocery", "supermarket", "market", "food mart")),
    ("Dining", ("restaurant", "cafe", "coffee", "takeaway", "lunch", "dinner")),
    ("Transport", ("bus", "train", "taxi", "uber", "lyft", "gas", "fuel", "parking")),
    ("Utilities", ("electric", "water", "utility", "internet", "phone", "mobile")),
    ("Healthcare", ("pharmacy", "doctor", "hospital", "medical", "health")),
    ("Entertainment", ("cinema", "movie", "streaming", "netflix", "game")),
    ("Shopping", ("amazon", "shopping", "store", "retail", "clothing")),
    ("Travel", ("hotel", "flight", "airline", "booking", "travel")),
    ("Education", ("school", "college", "tuition", "course", "book")),
)


def assign_basic_categories(transactions: pd.DataFrame) -> pd.DataFrame:
    """Fill missing or blank categories using recognizable merchant keywords."""
    result = transactions.copy()
    if "description" not in result:
        return result

    if "category" not in result:
        result["category"] = None

    missing = result["category"].isna() | result["category"].astype("string").str.strip().eq("")
    for index in result.index[missing]:
        description = str(result.at[index, "description"]).casefold()
        category = "Other"
        for category_name, keywords in _CATEGORY_RULES:
            if any(keyword in description for keyword in keywords):
                category = category_name
                break
        result.at[index, "category"] = category
    return result


def normalize_transaction_columns(transactions: pd.DataFrame) -> pd.DataFrame:
    """Map recognized CSV column names to the transaction import schema."""
    matches: dict[str, list[tuple[object, int]]] = {}
    for column in transactions.columns:
        detected = _detect_column_field(column)
        if detected is not None:
            field, confidence = detected
            matches.setdefault(field, []).append((column, confidence))

    selected: dict[str, list[object]] = {}
    for field, candidates in matches.items():
        if field == "category" and any(confidence >= 20 for _, confidence in candidates):
            candidates = [
                (column, confidence)
                for column, confidence in candidates
                if confidence >= 20
            ]
        selected[field] = [
            column
            for column, _ in sorted(
                candidates, key=lambda candidate: -candidate[1]
            )
        ]

    missing = [field for field in _REQUIRED_FIELDS if field not in selected]
    if missing:
        raise ValueError(
            "CSV is missing required fields: " + ", ".join(missing) + "."
        )

    normalized = pd.DataFrame(index=transactions.index)
    for field in (*_REQUIRED_FIELDS, "category"):
        columns = selected.get(field, [])
        if not columns:
            normalized[field] = None
            continue
        values = transactions[columns[0]].replace(r"^\s*$", pd.NA, regex=True)
        for column in columns[1:]:
            fallback = transactions[column].replace(r"^\s*$", pd.NA, regex=True)
            values = values.combine_first(fallback)
        normalized[field] = values
    return assign_basic_categories(normalized)
