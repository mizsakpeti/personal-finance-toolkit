"""Command-line interface for personal finance toolkit tools."""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from personal_finance_toolkit.categorizers.expense_categorizer import (
    ExpenseCategorizer,
    Transaction,
)
from personal_finance_toolkit.config.category_config import CategoryConfig
from personal_finance_toolkit.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


def load_transactions_from_file(file_path: str, sheet_name: int = 0) -> pd.DataFrame:
    """Load transactions from CSV or Excel file.

    Args:
        file_path: Path to the file (CSV or Excel)
        sheet_name: Sheet name/index for Excel files

    Returns:
        DataFrame with transaction data
    """
    path = Path(file_path)

    if not path.exists():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)

    if path.suffix.lower() == ".csv":
        # Try to detect delimiter
        with path.open(encoding="utf-8") as f:
            first_line = f.readline()
            # Check if tab-separated or comma-separated
            delimiter = "\t" if "\t" in first_line else ","
        return pd.read_csv(path, sep=delimiter)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=sheet_name)
    msg = f"Unsupported file format: {path.suffix}"
    raise ValueError(msg)


def _load_config(config_path: Path) -> CategoryConfig:
    """Load configuration from file based on extension.

    Args:
        config_path: Path to configuration file

    Returns:
        CategoryConfig instance

    Raises:
        ValueError: If config format is not supported
    """
    if config_path.suffix.lower() in {".yaml", ".yml"}:
        return CategoryConfig.from_yaml(str(config_path))
    if config_path.suffix.lower() == ".json":
        return CategoryConfig.from_json(str(config_path))
    msg = f"Unsupported config format: {config_path.suffix}"
    raise ValueError(msg)


def _validate_columns(df: pd.DataFrame, required_cols: list[str]) -> None:
    """Validate that required columns exist in dataframe.

    Args:
        df: DataFrame to validate
        required_cols: List of required column names

    Raises:
        ValueError: If required columns are missing
    """
    for col in required_cols:
        if col not in df.columns:
            msg = (
                f"Required column '{col}' not found. "
                f"Please check column names or use --{col.replace('_', '-')}-column"
            )
            raise ValueError(msg)


def _log_summary(categorizer: ExpenseCategorizer, df: pd.DataFrame) -> None:
    """Log categorization summary.

    Args:
        categorizer: ExpenseCategorizer instance
        df: Categorized dataframe
    """
    summary = categorizer.get_summary(
        [
            Transaction(
                amount=row["amount"],
                partner_name=row["partner_name"],
                description=row.get("description", ""),
                date=row["date"],
                category=row["category"],
            )
            for _, row in df.iterrows()
        ],
    )

    logger.info("Categorization Summary:")
    logger.info("-" * 50)
    for category, total in summary.items():
        logger.info(f"  {category:.<30} {total:>10,.0f}")
    logger.info("-" * 50)


def main_categorize() -> int:
    """Main function for expense categorizer CLI."""
    parser = argparse.ArgumentParser(
        description="Categorize bank statement transactions using keyword matching",
    )

    parser.add_argument(
        "bank_file",
        help="Path to bank statement file (CSV or Excel)",
    )

    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Path to category configuration file (YAML or JSON)",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path to output file (CSV or Excel). If not specified, prints to stdout",
    )

    parser.add_argument(
        "--partner-column",
        default="Partner név",
        help="Name of the partner column in bank statement (default: 'Partner név')",
    )

    parser.add_argument(
        "--amount-column",
        default="Összeg",
        help="Name of the amount column in bank statement (default: 'Összeg')",
    )

    parser.add_argument(
        "--date-column",
        default="Könyvelés dátuma",
        help="Name of the date column in bank statement (default: 'Könyvelés dátuma')",
    )

    parser.add_argument(
        "--description-column",
        default="Könyvelési információk",
        help="Name of the description column in bank statement (optional)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Set logging level (overrides verbose flag)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    if args.log_level:
        logging.getLogger("personal_finance_toolkit").setLevel(args.log_level)
    elif args.verbose:
        logging.getLogger("personal_finance_toolkit").setLevel(logging.DEBUG)

    try:
        # Load configuration
        config_path = Path(args.config)
        config = _load_config(config_path)

        logger.info(f"Loaded configuration from {config_path}")
        logger.debug(f"Categories: {', '.join(config.get_categories())}")

        # Load transactions
        df = load_transactions_from_file(args.bank_file)

        logger.info(f"Loaded {len(df)} transactions from {args.bank_file}")

        # Rename columns to expected names
        column_mapping = {
            args.partner_column: "partner_name",
            args.amount_column: "amount",
            args.date_column: "date",
        }

        if args.description_column in df.columns:
            column_mapping[args.description_column] = "description"

        df = df.rename(columns=column_mapping)

        # Ensure required columns exist
        required_cols = ["partner_name", "amount", "date"]
        _validate_columns(df, required_cols)

        # Categorize transactions
        categorizer = ExpenseCategorizer(config)
        df_categorized = categorizer.categorize_dataframe(df)

        logger.debug("Categorization completed successfully")

        if args.verbose:
            _log_summary(categorizer, df_categorized)

        # Save or display results
        if args.output:
            output_path = Path(args.output)
            if output_path.suffix.lower() == ".csv":
                df_categorized.to_csv(output_path, index=False)
            else:
                df_categorized.to_excel(output_path, index=False)

            message = f"Categorized {len(df_categorized)} transactions saved to {output_path}"
            logger.info(message)
        else:
            # Print to stdout
            print(df_categorized.to_string(index=False))
            logger.debug("Output written to stdout")

        return 0

    except FileNotFoundError:
        logger.exception("File not found")
        return 1
    except ValueError:
        logger.exception("Invalid value")
        return 1
    except BaseException:
        logger.exception("Unexpected error")
        return 1


if __name__ == "__main__":
    sys.exit(main_categorize())
