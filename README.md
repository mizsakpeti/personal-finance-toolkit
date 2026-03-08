# Personal Finance Toolkit

A comprehensive Python toolkit for managing and analyzing personal finances. This project provides tools to categorize, track, and analyze expenses and income from bank statements.

## Purpose

This toolkit helps you:

- **Categorize expenses** automatically from bank statements using keyword matching
- **Track spending** by category across time periods
- **Analyze financial patterns** to better understand your spending habits
- **Generate reports** from bank statement data

## Features

### 1. Expense Categorizer

Automatically categorizes bank statement transactions using configurable keyword matching.

**Key Features:**

- Keyword-based categorization
- Support for CSV and Excel files
- Flexible configuration (YAML or JSON)
- Summary generation by category
- Uncategorized transaction tracking

**See [Expense Categorizer README](docs/expense_categorizer.md) for detailed documentation and usage examples.**

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/personal-finance-toolkit.git
cd personal-finance-toolkit

# Install dependencies
uv sync
```

### Requirements

- Python 3.12+
- pandas >= 1.5.0
- pyyaml >= 6.0

## Quick Start

### Expense Categorizer

1. **Prepare your bank statement** in CSV or Excel format

2. **Create a category configuration** file (YAML or JSON):

   ```yaml
   Groceries:
     - Tesco
     - Aldi
   Entertainment:
     - Netflix
     - Spotify
   ```

3. **Run the categorizer**:

   ```bash
   uv run pft-categorize bank_statement.csv -c categories.yaml -o categorized.csv
   ```

See the [Expense Categorizer documentation](docs/expense_categorizer.md) for more details.

## Examples

The `examples/` directory contains:

- `sample_bank_statement.csv` - Sample Hungarian bank statement
- `categories_config.yaml` - Example category configuration

## Development

### Run Tests

```bash
uv run pytest tests/
```

### Check Code Quality

```bash
uv run ruff check .
uv run ty check .
```

## License

MIT License - see LICENSE file for details

## Roadmap

Future planned features:

- Income categorizer
