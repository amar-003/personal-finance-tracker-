"""TF-IDF and amount-based transaction category classifier."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


@dataclass
class CategoryClassifier:
    vectorizer: TfidfVectorizer
    amount_scaler: StandardScaler
    classifier: LogisticRegression

    def predict(
        self, descriptions: list[str], amounts: list[float]
    ) -> list[dict[str, str | float]]:
        if len(descriptions) != len(amounts):
            raise ValueError("Descriptions and amounts must have matching lengths.")
        clean_descriptions = [str(text).strip() for text in descriptions]
        numeric_amounts = np.asarray(amounts, dtype=float).reshape(-1, 1)
        if not np.isfinite(numeric_amounts).all():
            raise ValueError("Amounts must be finite numeric values.")
        features = hstack(
            [
                self.vectorizer.transform(clean_descriptions),
                csr_matrix(self.amount_scaler.transform(numeric_amounts)),
            ],
            format="csr",
        )
        probabilities = self.classifier.predict_proba(features)
        classes = self.classifier.classes_
        return [
            {
                "category": str(classes[index]),
                "confidence": round(float(probability[index]), 4),
            }
            for probability in probabilities
            for index in [int(np.argmax(probability))]
        ]


def train_category_classifier(transactions: pd.DataFrame) -> CategoryClassifier:
    """Train a baseline classifier from labeled transaction descriptions."""
    required = {"description", "amount", "category"}
    missing = required.difference(transactions.columns)
    if missing:
        raise ValueError("Missing classifier columns: " + ", ".join(sorted(missing)))

    data = transactions.dropna(subset=["category"]).copy()
    data["description"] = data["description"].fillna("").astype(str).str.strip()
    data["category"] = data["category"].astype(str).str.strip()
    data = data[data["category"] != ""]
    if data["category"].nunique() < 2:
        raise ValueError("At least two labeled categories are needed to train.")
    counts = data["category"].value_counts()
    if (counts < 2).any():
        raise ValueError("Each category needs at least two labeled transactions.")

    amounts = pd.to_numeric(data["amount"], errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(amounts).all():
        raise ValueError("Labeled transaction amounts must be finite numbers.")

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        token_pattern=r"(?u)\b\w+\b",
    )
    text_features = vectorizer.fit_transform(data["description"])
    amount_scaler = StandardScaler()
    amount_features = amount_scaler.fit_transform(amounts.reshape(-1, 1))
    features = hstack(
        [text_features, csr_matrix(amount_features)],
        format="csr",
    )
    classifier = LogisticRegression(max_iter=1000, class_weight="balanced")
    classifier.fit(features, data["category"])
    return CategoryClassifier(vectorizer, amount_scaler, classifier)
