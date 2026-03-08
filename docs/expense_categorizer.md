# Expense Categorizer

The Expense Categorizer is a tool that automatically categorizes bank statement transactions using configurable keyword matching. It helps you understand your spending patterns by grouping similar expenses into pre-defined categories.

## Overview

This tool reads transaction data from bank statements (CSV or Excel files) and matches transaction details against a set of configurable keywords to assign categories. Transactions that don't match any keywords are marked as "Uncategorized" for manual review.

## How It Works

### Categorization Process

1. **Load Configuration**: Read category definitions and associated keywords from a YAML or JSON configuration file
2. **Load Transactions**: Import transactions from a bank statement file
3. **Match Keywords**: For each transaction, search for keywords in:
   - Partner/merchant name (primary)
   - Description/notes (secondary)
4. **Assign Category**: Assign the first matching category or mark as "Uncategorized"
5. **Export Results**: Save categorized transactions to a new file or display on console

### Keyword Matching

- **Case-insensitive**: Keywords are matched regardless of case
- **Substring matching**: A keyword matches if it's contained in the transaction text
- **First match wins**: If multiple categories could match, the first match is assigned
- **Fallback order**: Partner name is checked first, then description

## Configuration

### Configuration File Format

#### YAML Format

```yaml
Groceries:
  - Tesco
  - Aldi
  - Coop

Entertainment:
  - Netflix
  - Spotify
  - Cinema

Utilities:
  - ELMŰ
  - TIGÁZ
  - Internet Provider
```

#### JSON Format

```json
{
  "Groceries": [
    "Tesco",
    "Aldi",
    "Coop"
  ],
  "Entertainment": [
    "Netflix",
    "Spotify",
    "Cinema"
  ],
  "Utilities": [
    "ELMŰ",
    "TIGÁZ",
    "Internet Provider"
  ]
}
```

### Configuration Guidelines

- **Keep keywords specific**: Use detailed keywords to avoid false matches
- **Case sensitivity**: Keywords work regardless of case
- **Abbreviations**: Include common abbreviations (e.g., "Netflix", "NFLX")
- **Special characters**: Include punctuation if it appears in transaction data
- **Updates**: Update configuration regularly based on uncategorized transactions

## Bank Statement Format

### Expected Columns

The tool expects your bank statement to have at minimum:

| Column | Default Name | Description |
|--------|--------------|-------------|
| Partner Name | `Partner név` | Name of the merchant/payee |
| Amount | `Összeg` | Transaction amount |
| Date | `Könyvelés dátuma` | Transaction date |
| Description | `Könyvelési információk` | Additional transaction details (optional) |

**Note**: The default column names are in Hungarian (common for Hungarian banks). Use the `--*-column` flags to specify different column names.

### Example Bank Statement

```csv
Felhasználónév,Számlaszám,Könyvelés dátuma,Összeg,Devizanem,Partner név,Partner IBAN száma,Partner számlaszáma,Partner bankkódja,Könyvelési információk,Tranzakcióazonosító,Tranzakció dátuma és ideje
hitel,,2026.01.06,-16358,HUF,SIMPLEP*PREMIUMEP,,,022L0215 Budapest SIMPLE P*PREMIUMEP,,2025.12.30 12:14:10
hitel,,2026.01.06,-3240,HUF,Alza.hu Kft.,,,Apple Pay Budapest Alza. hu Kft.,,2025.12.30 17:20:37
hitel,,2026.01.07,-4990,HUF,eMAG.hu,,,RO21573 Budapest eMAG.hu,,2025.12.31 16:03:04
```

## Usage

### Command Line Interface

```bash
uv run pft-categorize <bank_file> -c <config_file> [options]
```

### Basic Example

```bash
# Categorize a Hungarian bank statement
uv runpft-categorize bank_statement.csv \
  -c categories.yaml \
  -o categorized.csv
```

### With Custom Column Names

```bash
# If your bank statement has different column names
uv runpft-categorize statement.xlsx \
  -c categories.json \
  -o results.xlsx \
  --partner-column "Merchant" \
  --amount-column "Transaction Amount" \
  --date-column "Date" \
  --description-column "Memo"
```

### Verbose Output

```bash
# Show categorization summary and statistics
uv runpft-categorize bank_statement.csv \
  -c categories.yaml \
  -o categorized.csv \
  -v
```

### Print to Console

```bash
# Display results instead of saving to file
uv run pft-categorize bank_statement.csv \
  -c categories.yaml
```

## Arguments and Options

```plaintext
Positional Arguments:
  bank_file              Path to bank statement file (CSV or Excel)

Required Options:
  -c, --config PATH      Path to category configuration file (YAML or JSON)

Optional Arguments:
  -o, --output PATH      Output file path (CSV or Excel)
                        Defaults to stdout if not specified

  --partner-column NAME  Partner/merchant column name
                        Default: 'Partner név'

  --amount-column NAME   Amount column name
                        Default: 'Összeg'

  --date-column NAME     Date column name
                        Default: 'Könyvelés dátuma'

  --description-column NAME
                        Description column name
                        Default: 'Könyvelési információk'

  -v, --verbose          Show detailed output including summary statistics

  -h, --help            Show help message
```

## Python API

You can also use the Expense Categorizer programmatically in your Python code.

### Basic Usage

```python
from personal_finance_toolkit import ExpenseCategorizer
from personal_finance_toolkit.config import CategoryConfig
import pandas as pd

# Load configuration
config = CategoryConfig.from_yaml('categories.yaml')

# Create categorizer
categorizer = ExpenseCategorizer(config)

# Load transactions
df = pd.read_csv('bank_statement.csv')

# Categorize
df_categorized = categorizer.categorize_dataframe(df)

# Save results
df_categorized.to_csv('categorized.csv', index=False)
```

### Working with Transactions

```python
from personal_finance_toolkit.categorizers.expense_categorizer import Transaction

# Create transaction objects
transactions = [
    Transaction(
        date='2026.01.06',
        partner_name='Tesco Supermarket',
        description='Grocery shopping',
        amount=-5000.0
    ),
    Transaction(
        date='2026.01.07',
        partner_name='Netflix Inc',
        description='Monthly subscription',
        amount=-3090.0
    )
]

# Categorize transactions
categorized = categorizer.categorize_transactions(transactions)

# Get summary
summary = categorizer.get_summary(categorized)
print(summary)
# Output: {'Groceries': 5000.0, 'Entertainment': 3090.0}

# Find uncategorized transactions
uncategorized = categorizer.get_uncategorized(categorized)
```

### Using Different Configuration Formats

```python
# Load from YAML
config = CategoryConfig.from_yaml('config.yaml')

# Load from JSON
config = CategoryConfig.from_json('config.json')

# Create from dictionary
config = CategoryConfig({
    'Groceries': ['Tesco', 'Aldi'],
    'Entertainment': ['Netflix', 'Spotify']
})

# Save to file
config.save_to_yaml('my_config.yaml')
config.save_to_json('my_config.json')
```

## Output

### Categorized Transactions File

The output file contains the original data plus a new `category` column:

```csv
Felhasználónév,Számlaszám,Könyvelés dátuma,Összeg,Devizanem,Partner név,...,category
hitel,,2026.01.06,-16358,HUF,SIMPLEP*PREMIUMEP,...,Shopping
hitel,,2026.01.06,-3240,HUF,Alza.hu Kft.,...,Shopping
hitel,,2026.01.07,-4990,HUF,eMAG.hu,...,Shopping
```

### Verbose Summary Output

When using `-v` flag:

```
✓ Loaded configuration from categories.yaml
  Categories: Groceries, Entertainment, Shopping, Utilities

✓ Loaded 100 transactions from bank_statement.csv

Categorization Summary:
--------------------------------------------------
  Shopping............................... 45,000
  Groceries............................. 32,000
  Entertainment......................... 18,500
  Utilities............................. 12,000
  Uncategorized.......................... 2,500
--------------------------------------------------
✓ Saved results to categorized.csv
```

## Tips and Best Practices

### 1. Start with Common Merchants

Focus on the merchants you frequent most. Calculate their percentage of your transactions:

```bash
# Get uncategorized for review
pft-categorize bank_statement.csv -c categories.yaml | grep "Uncategorized"
```

### 2. Use Keyword Variations

Many merchants have multiple names:

```yaml
Shopping:
  - Amazon
  - AMZN
  - amazon.com
  - Amazon Prime
```

### 3. Handle Special Cases

For merchants with special characters:

```yaml
Utilities:
  - "E.ON"
  - "E.ON Energy"
  - "E.ON Energie"
```

### 4. Regular Updates

Update your configuration as you discover new merchants:

```bash
# Check uncategorized regularly
pft-categorize bank_statement.csv -c categories.yaml -v | grep "Uncategorized"
```

### 5. Organize by Frequency

Place more frequent merchants first to improve matching speed:

```yaml
Groceries:
  - Tesco          # Your most frequent store
  - Aldi           # Second most frequent
  - Coop
```

## Examples

### Example 1: Hungarian Bank Statement

See `examples/sample_bank_statement.csv` and `examples/categories_config.yaml`

```bash
cd examples/
pft-categorize sample_bank_statement.csv \
  -c categories_config.yaml \
  -o sample_categorized.csv \
  -v
```

### Example 2: US Bank Statement

```bash
pft-categorize us_statement.csv \
  -c us_categories.yaml \
  --partner-column "Merchant" \
  --amount-column "Amount" \
  --date-column "Transaction Date" \
  -o categorized.csv
```

### Example 3: Integrating with Your Workflow

```bash
# Monthly process
for month in {01..12}; do
  pft-categorize "statement_2026_${month}.csv" \
    -c categories.yaml \
    -o "categorized_2026_${month}.csv" \
    -v
done
```

## Troubleshooting

### Issue: "File not found" Error

```
Error: File not found: bank_statement.csv
```

**Solution**: Ensure the file path is correct and the file exists:

```bash
# Check if file exists
ls -la bank_statement.csv

# Use absolute path if needed
pft-categorize /full/path/to/bank_statement.csv -c categories.yaml
```

### Issue: Column Not Found

```plaintext
Error: Required column 'Partner' not found
```

**Solution**: Use the correct column name or specify it with flags:

```bash
pft-categorize statement.csv \
  -c categories.yaml \
  --partner-column "Merchant Name"
```

### Issue: Many Uncategorized Transactions

This is normal! Review uncategorized transactions and update your configuration:

```bash
# Save to file for review
pft-categorize statement.csv -c categories.yaml -o temp.csv -v

# Review uncategorized (search for category='Uncategorized' in the output)
# Update categories.yaml with new keywords
# Re-run the categorizer
```

## Limitations and Future Improvements

### Current Limitations

- **Simple keyword matching**: Uses substring matching only
- **Single category per transaction**: Each transaction gets one category
- **No machine learning**: Doesn't learn from your categorization patterns
- **Case-sensitive keywords**: Requires exact keyword matching (case-insensitive)

### Planned Improvements

- Fuzzy matching for typos and variations
- Machine learning-based categorization
- Multiple categories per transaction
- Performance optimization for large files
- Interactive configuration builder
- Automatic category discovery from transaction history

## Contributing

Found an issue or have a suggestion? Please contribute!

1. Test with your bank statement format
2. Add new keywords or categories
3. Report issues or feature requests
4. Submit improvements via pull requests

## License

MIT License - see repository for details
