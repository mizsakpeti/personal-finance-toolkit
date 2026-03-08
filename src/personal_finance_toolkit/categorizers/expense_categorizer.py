"""Expense categorizer module for classifying transactions."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    import pandas as pd

    from personal_finance_toolkit.config.category_config import CategoryConfig


class Transaction(BaseModel):
    """Represents a single transaction."""

    amount: float
    partner_name: str
    description: str
    date: date
    category: str | None = None

    def __str__(self) -> str:
        """Return string representation of transaction."""
        return f"{self.date}: {self.partner_name} ({self.amount}) - {self.category or 'Uncategorized'}"


class ExpenseCategorizer:
    """Categorizes expenses based on configuration rules."""

    def __init__(self, config: CategoryConfig) -> None:
        """Initialize the expense categorizer.

        Args:
            config: CategoryConfig instance with category definitions
        """
        self.config = config

    def categorize_text(self, text: str) -> str | None:
        """Categorize based on text content.

        Args:
            text: Text to categorize (e.g., partner name or description)

        Returns:
            Category name if found, None otherwise
        """
        return self.config.find_category(text)

    def categorize_transaction(self, transaction: Transaction) -> Transaction:
        """Categorize a single transaction.

        Args:
            transaction: Transaction to categorize

        Returns:
            Transaction with category assigned
        """
        # Try partner name first
        category = self.categorize_text(transaction.partner_name)

        # If not found, try description
        if not category and transaction.description:
            category = self.categorize_text(transaction.description)

        transaction.category = category or "Uncategorized"
        return transaction

    def categorize_transactions(
        self, transactions: list[Transaction]
    ) -> list[Transaction]:
        """Categorize multiple transactions.

        Args:
            transactions: List of transactions to categorize

        Returns:
            List of categorized transactions
        """
        return [self.categorize_transaction(t) for t in transactions]

    def categorize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize transactions from a pandas DataFrame.

        Expected columns:
            - partner_name: Name of transaction partner
            - amount: Transaction amount
            - date: Transaction date
            - description (optional): Additional description

        Args:
            df: DataFrame with transaction data

        Returns:
            DataFrame with added 'category' column
        """
        if df.empty:
            return df.copy()

        df_copy = df.copy()

        # Create default description if not present
        if "description" not in df_copy.columns:
            df_copy["description"] = ""

        # Categorize each row
        categories = []
        for _, row in df_copy.iterrows():
            transaction = Transaction(
                amount=row.get("amount", 0),
                partner_name=row.get("partner_name", ""),
                description=row.get("description", ""),
                date=row.get("date", ""),
            )
            categorized = self.categorize_transaction(transaction)
            categories.append(categorized.category)

        df_copy["category"] = categories
        return df_copy

    def get_summary(self, transactions: list[Transaction]) -> dict[str, float]:
        """Get summary of spending by category.

        Args:
            transactions: List of categorized transactions

        Returns:
            Dict mapping categories to total amounts
        """
        summary: dict[str, float] = {}
        for transaction in transactions:
            if transaction.amount > 0:
                continue  # Skip income transactions
            category = transaction.category or "Uncategorized"
            summary[category] = summary.get(category, 0) + abs(transaction.amount)

        return dict(sorted(summary.items(), key=lambda x: x[1], reverse=True))

    def get_uncategorized(self, transactions: list[Transaction]) -> list[Transaction]:
        """Get list of uncategorized transactions.

        Args:
            transactions: List of categorized transactions

        Returns:
            List of transactions with category 'Uncategorized'
        """
        return [t for t in transactions if t.category == "Uncategorized"]
