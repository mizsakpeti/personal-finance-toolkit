"""Unit tests for ExpenseCategorizer and Transaction classes."""

import pandas as pd
import pytest

from personal_finance_toolkit.categorizers.expense_categorizer import (
    ExpenseCategorizer,
    Transaction,
)
from personal_finance_toolkit.config.category_config import CategoryConfig


class TestTransaction:
    """Test Transaction dataclass."""

    @pytest.fixture
    def sample_transaction(self):
        """Fixture providing a sample transaction."""
        return Transaction(
            amount=100.0,
            partner_name="Tesco",
            description="Weekly groceries",
            date="2024-01-15",
        )

    def test_transaction_initialization_with_category(self):
        """Test Transaction initialization with category."""
        txn = Transaction(
            amount=50.0,
            partner_name="Netflix",
            description="Monthly subscription",
            date="2024-01-01",
            category="Entertainment",
        )
        assert txn.amount == 50.0
        assert txn.partner_name == "Netflix"
        assert txn.description == "Monthly subscription"
        assert txn.date == "2024-01-01"
        assert txn.category == "Entertainment"

    def test_transaction_initialization_without_category(self, sample_transaction):
        """Test Transaction initialization with default None category."""
        assert sample_transaction.category is None

    @pytest.mark.parametrize(
        ("amount", "partner_name", "date"),
        [
            (100.0, "Store A", "2024-01-15"),
            (0.0, "Store B", "2024-01-16"),
            (-50.0, "Refund", "2024-01-17"),
            (999999.99, "Expensive Purchase", "2024-01-18"),
        ],
    )
    def test_transaction_with_various_amounts(self, amount, partner_name, date):
        """Test Transaction with various amount values."""
        txn = Transaction(
            amount=amount,
            partner_name=partner_name,
            description="Test",
            date=date,
        )
        assert txn.amount == amount

    def test_transaction_str_representation_with_category(self):
        """Test string representation of transaction with category."""
        txn = Transaction(
            amount=100.0,
            partner_name="Tesco",
            description="Groceries",
            date="2024-01-15",
            category="Groceries",
        )
        result = str(txn)
        assert "2024-01-15" in result
        assert "Tesco" in result
        assert "100.0" in result
        assert "Groceries" in result

    def test_transaction_str_representation_without_category(self, sample_transaction):
        """Test string representation of transaction without category."""
        result = str(sample_transaction)
        assert "2024-01-15" in result
        assert "Tesco" in result
        assert "100.0" in result
        assert "Uncategorized" in result


class TestExpenseCategorizer:
    """Test ExpenseCategorizer class."""

    @pytest.fixture
    def config(self):
        """Fixture providing a CategoryConfig instance."""
        return CategoryConfig(
            {
                "Groceries": ["Tesco", "Aldi", "Carrefour"],
                "Utilities": ["Electricity", "Water Company"],
                "Entertainment": ["Netflix", "Cinema", "Spotify"],
                "Transportation": ["Uber", "Taxi"],
            }
        )

    @pytest.fixture
    def categorizer(self, config):
        """Fixture providing an ExpenseCategorizer instance."""
        return ExpenseCategorizer(config)

    @pytest.fixture
    def sample_transactions(self):
        """Fixture providing sample transactions."""
        return [
            Transaction(
                amount=50.0,
                partner_name="Tesco",
                description="Weekly shopping",
                date="2024-01-15",
            ),
            Transaction(
                amount=30.0,
                partner_name="Electricity Provider",
                description="Monthly bill",
                date="2024-01-16",
            ),
            Transaction(
                amount=15.0,
                partner_name="Netflix",
                description="Subscription",
                date="2024-01-17",
            ),
            Transaction(
                amount=25.0,
                partner_name="Unknown Store",
                description="Purchase",
                date="2024-01-18",
            ),
        ]

    def test_categorizer_initialization(self, config):
        """Test ExpenseCategorizer initialization."""
        categorizer = ExpenseCategorizer(config)
        assert categorizer.config == config

    def test_categorize_text_with_matching_keyword(self, categorizer):
        """Test categorize_text with matching keyword."""
        result = categorizer.categorize_text("Tesco Store")
        assert result == "Groceries"

    @pytest.mark.parametrize(
        ("text", "expected_category"),
        [
            ("Tesco", "Groceries"),
            ("Aldi", "Groceries"),
            ("Electricity Bill", "Utilities"),
            ("Water Company", "Utilities"),
            ("Netflix Subscription", "Entertainment"),
            ("Cinema Tickets", "Entertainment"),
            ("Uber Ride", "Transportation"),
        ],
    )
    def test_categorize_text_with_various_partners(self, categorizer, text, expected_category):
        """Test categorize_text with various partner names."""
        result = categorizer.categorize_text(text)
        assert result == expected_category

    def test_categorize_text_with_non_matching_text(self, categorizer):
        """Test categorize_text with non-matching text."""
        result = categorizer.categorize_text("Unknown Vendor")
        assert result is None

    def test_categorize_text_with_empty_string(self, categorizer):
        """Test categorize_text with empty string."""
        result = categorizer.categorize_text("")
        assert result is None

    def test_categorize_single_transaction_by_partner_name(self, categorizer):
        """Test categorizing transaction by partner name."""
        txn = Transaction(
            amount=100.0,
            partner_name="Tesco",
            description="Shopping",
            date="2024-01-15",
        )
        result = categorizer.categorize_transaction(txn)

        assert result.category == "Groceries"
        assert result.amount == 100.0
        assert result.partner_name == "Tesco"

    def test_categorize_single_transaction_by_description(self, categorizer):
        """Test categorizing transaction by description when partner name doesn't match."""
        txn = Transaction(
            amount=50.0,
            partner_name="Unknown Shop",
            description="Netflix subscription",
            date="2024-01-15",
        )
        result = categorizer.categorize_transaction(txn)

        assert result.category == "Entertainment"

    def test_categorize_single_transaction_prioritizes_partner_name(self, categorizer):
        """Test that partner name takes priority over description."""
        txn = Transaction(
            amount=50.0,
            partner_name="Tesco",
            description="Netflix subscription",
            date="2024-01-15",
        )
        result = categorizer.categorize_transaction(txn)

        # Should match Tesco (partner_name), not Netflix (description)
        assert result.category == "Groceries"

    def test_categorize_single_transaction_uncategorized(self, categorizer):
        """Test categorizing transaction with no matches."""
        txn = Transaction(
            amount=25.0,
            partner_name="Unknown Store",
            description="Random stuff",
            date="2024-01-15",
        )
        result = categorizer.categorize_transaction(txn)

        assert result.category == "Uncategorized"

    def test_categorize_transaction_mutation(self, categorizer):
        """Test that categorize_transaction modifies the original transaction."""
        txn = Transaction(
            amount=100.0,
            partner_name="Tesco",
            description="Shopping",
            date="2024-01-15",
        )
        result = categorizer.categorize_transaction(txn)

        # Should return the same object
        assert result is txn
        assert txn.category == "Groceries"

    def test_categorize_multiple_transactions(self, categorizer, sample_transactions):
        """Test categorizing multiple transactions."""
        results = categorizer.categorize_transactions(sample_transactions)

        assert len(results) == len(sample_transactions)
        assert results[0].category == "Groceries"
        assert results[1].category == "Utilities"
        assert results[2].category == "Entertainment"
        assert results[3].category == "Uncategorized"

    def test_categorize_multiple_transactions_preserves_order(self, categorizer):
        """Test that categorizing multiple transactions preserves order."""
        transactions = [
            Transaction(
                amount=10.0,
                partner_name="Netflix",
                description="",
                date="2024-01-01",
            ),
            Transaction(
                amount=20.0,
                partner_name="Tesco",
                description="",
                date="2024-01-02",
            ),
            Transaction(
                amount=30.0,
                partner_name="Uber",
                description="",
                date="2024-01-03",
            ),
        ]
        results = categorizer.categorize_transactions(transactions)

        assert results[0].date == "2024-01-01"
        assert results[1].date == "2024-01-02"
        assert results[2].date == "2024-01-03"

    def test_categorize_empty_transaction_list(self, categorizer):
        """Test categorizing an empty list of transactions."""
        results = categorizer.categorize_transactions([])
        assert results == []

    def test_categorize_dataframe_with_empty_dataframe(self, categorizer):
        """Test categorizing an empty DataFrame - returns as-is without category column."""
        df = pd.DataFrame(columns=["partner_name", "amount", "date", "description"])
        result = categorizer.categorize_dataframe(df)

        # Empty DataFrame is returned as-is without category column
        assert result.empty
        assert "category" not in result.columns

    def test_categorize_dataframe_with_valid_data(self, categorizer):
        """Test categorizing a DataFrame with transaction data."""
        df = pd.DataFrame(
            {
                "partner_name": ["Tesco", "Netflix", "Unknown", "Electricity"],
                "amount": [100.0, 15.0, 50.0, 80.0],
                "date": ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18"],
                "description": ["", "subscription", "random", "bill"],
            }
        )
        result = categorizer.categorize_dataframe(df)

        assert "category" in result.columns
        assert result["category"].tolist() == [
            "Groceries",
            "Entertainment",
            "Uncategorized",
            "Utilities",
        ]

    def test_categorize_dataframe_without_description_column(self, categorizer):
        """Test categorizing a DataFrame without description column."""
        df = pd.DataFrame(
            {
                "partner_name": ["Tesco", "Netflix"],
                "amount": [100.0, 15.0],
                "date": ["2024-01-15", "2024-01-16"],
            }
        )
        result = categorizer.categorize_dataframe(df)

        assert "category" in result.columns
        assert result["category"].tolist() == ["Groceries", "Entertainment"]

    def test_categorize_dataframe_preserves_original(self, categorizer):
        """Test that categorize_dataframe doesn't modify original DataFrame."""
        df = pd.DataFrame(
            {
                "partner_name": ["Tesco"],
                "amount": [100.0],
                "date": ["2024-01-15"],
            }
        )
        original_len = len(df.columns)
        result = categorizer.categorize_dataframe(df)

        # Original should not be modified
        assert len(df.columns) == original_len
        assert "category" not in df.columns
        # Result should have category
        assert "category" in result.columns


class TestExpenseCategorizer_Summary:
    """Test summary functionality of ExpenseCategorizer."""

    @pytest.fixture
    def config(self):
        """Fixture providing a CategoryConfig instance."""
        return CategoryConfig(
            {
                "Groceries": ["Tesco", "Aldi"],
                "Entertainment": ["Netflix", "Cinema"],
            }
        )

    @pytest.fixture
    def categorizer(self, config):
        """Fixture providing an ExpenseCategorizer instance."""
        return ExpenseCategorizer(config)

    def test_get_summary_single_category(self, categorizer):
        """Test get_summary with transactions in a single category."""
        transactions = [
            Transaction(50.0, "Tesco", "", "2024-01-01", "Groceries"),
            Transaction(30.0, "Aldi", "", "2024-01-02", "Groceries"),
        ]
        summary = categorizer.get_summary(transactions)

        assert summary == {"Groceries": 80.0}

    def test_get_summary_multiple_categories(self, categorizer):
        """Test get_summary with transactions across multiple categories."""
        transactions = [
            Transaction(50.0, "Tesco", "", "2024-01-01", "Groceries"),
            Transaction(15.0, "Netflix", "", "2024-01-02", "Entertainment"),
            Transaction(30.0, "Aldi", "", "2024-01-03", "Groceries"),
        ]
        summary = categorizer.get_summary(transactions)

        assert summary == {"Groceries": 80.0, "Entertainment": 15.0}

    def test_get_summary_includes_uncategorized(self, categorizer):
        """Test get_summary includes uncategorized transactions."""
        transactions = [
            Transaction(50.0, "Tesco", "", "2024-01-01", "Groceries"),
            Transaction(25.0, "Unknown", "", "2024-01-02", "Uncategorized"),
        ]
        summary = categorizer.get_summary(transactions)

        assert "Uncategorized" in summary
        assert summary["Uncategorized"] == 25.0

    def test_get_summary_sorts_by_amount_descending(self, categorizer):
        """Test that get_summary returns categories sorted by amount."""
        transactions = [
            Transaction(10.0, "Tesco", "", "2024-01-01", "Groceries"),
            Transaction(100.0, "Netflix", "", "2024-01-02", "Entertainment"),
            Transaction(50.0, "Aldi", "", "2024-01-03", "Groceries"),
        ]
        summary = categorizer.get_summary(transactions)
        categories = list(summary.keys())

        # Entertainment (100) should come before Groceries (60)
        assert categories == ["Entertainment", "Groceries"]

    def test_get_summary_with_negative_amounts(self, categorizer):
        """Test get_summary with negative amounts (refunds)."""
        transactions = [
            Transaction(50.0, "Tesco", "", "2024-01-01", "Groceries"),
            Transaction(-20.0, "Tesco", "", "2024-01-02", "Groceries"),
        ]
        summary = categorizer.get_summary(transactions)

        # Absolute values should be used
        assert summary["Groceries"] == 70.0

    def test_get_summary_empty_list(self, categorizer):
        """Test get_summary with empty transaction list."""
        summary = categorizer.get_summary([])
        assert summary == {}

    @pytest.mark.parametrize(
        "amounts,expected_total",
        [
            ([10.0, 20.0, 30.0], 60.0),
            ([0.0, 0.0, 0.0], 0.0),
            ([1.5, 2.5, 1.0], 5.0),
        ],
    )
    def test_get_summary_calculates_totals_correctly(self, categorizer, amounts, expected_total):
        """Test that get_summary calculates category totals correctly."""
        transactions = [
            Transaction(amount, "Tesco", "", f"2024-01-{i:02d}", "Groceries")
            for i, amount in enumerate(amounts, 1)
        ]
        summary = categorizer.get_summary(transactions)

        assert summary["Groceries"] == expected_total


class TestExpenseCategorizer_UncategorizedFiltering:
    """Test uncategorized transaction filtering."""

    @pytest.fixture
    def config(self):
        """Fixture providing a CategoryConfig instance."""
        return CategoryConfig(
            {
                "Groceries": ["Tesco"],
                "Entertainment": ["Netflix"],
            }
        )

    @pytest.fixture
    def categorizer(self, config):
        """Fixture providing an ExpenseCategorizer instance."""
        return ExpenseCategorizer(config)

    def test_get_uncategorized_returns_uncategorized_only(self, categorizer):
        """Test that get_uncategorized returns only uncategorized transactions."""
        transactions = [
            Transaction(50.0, "Tesco", "", "2024-01-01", "Groceries"),
            Transaction(25.0, "Unknown", "", "2024-01-02", "Uncategorized"),
            Transaction(15.0, "Netflix", "", "2024-01-03", "Entertainment"),
            Transaction(10.0, "Unknown2", "", "2024-01-04", "Uncategorized"),
        ]
        uncategorized = categorizer.get_uncategorized(transactions)

        assert len(uncategorized) == 2
        assert all(t.category == "Uncategorized" for t in uncategorized)
        assert uncategorized[0].partner_name == "Unknown"
        assert uncategorized[1].partner_name == "Unknown2"

    def test_get_uncategorized_empty_list(self, categorizer):
        """Test get_uncategorized with no uncategorized transactions."""
        transactions = [
            Transaction(50.0, "Tesco", "", "2024-01-01", "Groceries"),
            Transaction(15.0, "Netflix", "", "2024-01-02", "Entertainment"),
        ]
        uncategorized = categorizer.get_uncategorized(transactions)

        assert uncategorized == []

    def test_get_uncategorized_all_uncategorized(self, categorizer):
        """Test get_uncategorized when all transactions are uncategorized."""
        transactions = [
            Transaction(25.0, "Unknown", "", "2024-01-01", "Uncategorized"),
            Transaction(10.0, "Unknown2", "", "2024-01-02", "Uncategorized"),
        ]
        uncategorized = categorizer.get_uncategorized(transactions)

        assert len(uncategorized) == 2
        assert uncategorized == transactions

    def test_get_uncategorized_preserves_order(self, categorizer):
        """Test that get_uncategorized preserves transaction order."""
        transactions = [
            Transaction(10.0, "Unknown1", "", "2024-01-01", "Uncategorized"),
            Transaction(50.0, "Tesco", "", "2024-01-02", "Groceries"),
            Transaction(20.0, "Unknown2", "", "2024-01-03", "Uncategorized"),
        ]
        uncategorized = categorizer.get_uncategorized(transactions)

        assert uncategorized[0].date == "2024-01-01"
        assert uncategorized[1].date == "2024-01-03"
