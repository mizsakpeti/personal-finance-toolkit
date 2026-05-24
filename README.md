# Personal Finance Toolkit

A comprehensive Python toolkit for managing and analyzing personal finances. This project provides tools to categorize, track, and analyze expenses and income from bank statements.

## Purpose

This toolkit helps you:

- **Categorize expenses** automatically from bank statements using keyword matching
- **Track spending** by category across time periods
- **Analyze financial patterns** to better understand your spending habits
- **Generate reports** from bank statement data

## Features

### Web Calculators

Interactive financial calculators served via [GitHub Pages](https://mizsakpeti.github.io/personal-finance-toolkit/). All available in English and Hungarian.

- **Cash Opportunity Cost** — see what keeping too much in savings is actually costing you
- **HUF vs EUR Returns** — compare currency-denominated investment paths
- **Compound Growth & Monthly SIP** — project how regular contributions compound over time

### Expense Categorizer (CLI)

Automatically categorizes bank statement transactions using configurable keyword matching.

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

# Install dependencies (with development extra)
uv sync --extra "dev"
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

## Adding a new calculator

The site uses Jinja2 templates rendered at build time. Templates use a two-level inheritance hierarchy:

```
templates/
  _base.html.jinja                  # HTML skeleton, CSS reset, variables
  _calculator_base.html.jinja       # Shared calculator CSS, Chart.js/KaTeX, nav, footer
  index.html.jinja                  # Landing page (lists all calculators manually)
  calculators/
    <name>/
      index.html.jinja              # English version
      hu/index.html.jinja           # Hungarian version (optional)
```

### Steps

1. **Create the template** at `templates/calculators/<your-calculator>/index.html.jinja`:

   ```jinja
   {% set lang = "en" %}
   {% set use_katex = false %}
   {% set root = "../../" %}
   {% set nav_all_tools = "All tools" %}
   {% set footer_part_of = "Part of" %}
   {% set footer_disclaimer = "Not financial advice." %}
   {% extends "_calculator_base.html.jinja" %}

   {% block title %}Your Calculator Title{% endblock %}

   {% block lang_switch %}
           <div class="lang-switch">
               <span class="current">EN</span>
               <span class="sep">|</span>
               <a href="hu/">HU</a>
           </div>
   {% endblock %}

   {% block page_css %}
           /* page-specific CSS here */
   {% endblock %}

   {% block content %}
   <div class="article">
       <div class="container">
           <div class="meta">Calculator</div>
           <h1>Your Calculator Title</h1>
           <p class="subtitle">Short description.</p>
       </div>
   </div>
   <div class="calculator">
       <div class="container">
           <!-- inputs, results, charts -->
       </div>
   </div>
   {% endblock %}

   {% block scripts %}
   <script>
   function calculate() {
       // your logic
   }
   </script>
   {% endblock %}
   ```

   Set `use_katex = true` if you need math formula rendering.

2. **Add a card to the landing page** in `templates/index.html.jinja`:

   ```jinja
   <a href="calculators/<your-calculator>/" class="card">
       <span class="tag tag-web">Calculator</span>
       <h3>Your Calculator Title</h3>
       <p>Short description of what it does.</p>
       <span class="arrow">Open calculator →</span>
   </a>
   ```

3. **Build and verify:**

   ```bash
   uv run python scripts/build.py
   open docs/calculators/<your-calculator>/index.html
   ```

4. **Commit `templates/`** — CI builds and deploys to GitHub Pages automatically. The generated HTML in `docs/` is gitignored.

### Adding a Hungarian version

Create `templates/calculators/<your-calculator>/hu/index.html.jinja` with `lang = "hu"`, `root = "../../../"`, and Hungarian text. Update both EN and HU `lang_switch` blocks to link to each other.

### Customizing styles

`_calculator_base.html.jinja` exposes many override blocks for fine-tuning per page (e.g. `article_padding`, `result_cards_cols`, `calc_title_mb`, `extra_css_vars`). See the file for the full list.

## Development

### Build the site locally

```bash
uv run python scripts/build.py    # render templates/ → docs/
open docs/index.html               # preview in browser
```

The generated HTML in `docs/` is gitignored — CI builds and deploys it to GitHub Pages on every push to `main`.

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
