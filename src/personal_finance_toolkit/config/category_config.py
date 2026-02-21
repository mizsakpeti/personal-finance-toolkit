"""Configuration management for expense categorizer."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


class CategoryConfig:
    """Manages expense category configuration."""

    def __init__(self, categories: dict[str, list[str]]) -> None:
        """Initialize category configuration.

        Args:
            categories: Dict mapping category names to lists of keywords
        """
        self.categories = categories
        self._keyword_to_category: dict[str, str] = {}
        self._build_keyword_lookup()

    def _build_keyword_lookup(self) -> None:
        """Build a lookup table mapping keywords to categories."""
        self._keyword_to_category = {}
        for category, keywords in self.categories.items():
            for keyword in keywords:
                # Store lowercase version for case-insensitive matching
                self._keyword_to_category[keyword.lower()] = category

    @classmethod
    def from_yaml(cls, yaml_path: str) -> CategoryConfig:
        """Load configuration from a YAML file.

        Args:
            yaml_path: Path to the YAML configuration file

        Returns:
            CategoryConfig instance

        Example YAML format:
            Groceries:
              - Tesco
              - Aldi
              - Coop
            Utilities:
              - Electricity Company
              - Water Works
            Entertainment:
              - Cinema
              - Netflix
        """
        path = Path(yaml_path)
        if not path.exists():
            msg = f"Configuration file not found: {yaml_path}"
            raise FileNotFoundError(msg)

        with path.open(encoding="utf-8") as f:
            categories = yaml.safe_load(f)

        if not isinstance(categories, dict):
            msg = "Configuration file must contain a dictionary of categories"
            raise TypeError(msg)

        return cls(categories)

    @classmethod
    def from_json(cls, json_path: str) -> CategoryConfig:
        """Load configuration from a JSON file.

        Args:
            json_path: Path to the JSON configuration file

        Returns:
            CategoryConfig instance
        """
        path = Path(json_path)
        if not path.exists():
            msg = f"Configuration file not found: {json_path}"
            raise FileNotFoundError(msg)

        with path.open(encoding="utf-8") as f:
            categories = json.load(f)

        if not isinstance(categories, dict):
            msg = "Configuration file must contain a dictionary of categories"
            raise TypeError(msg)

        return cls(categories)

    def get_categories(self) -> list[str]:
        """Get list of all defined categories."""
        return list(self.categories.keys())

    def get_keywords(self, category: str) -> list[str]:
        """Get keywords for a specific category."""
        return self.categories.get(category, [])

    def find_category(self, text: str) -> str | None:
        """Find category that matches the text based on keywords.

        Args:
            text: Text to search for keywords (e.g., partner name or description)

        Returns:
            Category name if match found, None otherwise
        """
        if not text:
            return None

        text_lower = text.lower()

        # Exact keyword match first
        for keyword, category in self._keyword_to_category.items():
            if keyword in text_lower:
                return category

        return None

    def save_to_yaml(self, yaml_path: str) -> None:
        """Save configuration to a YAML file."""
        path = Path(yaml_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            yaml.dump(self.categories, f, default_flow_style=False, allow_unicode=True)

    def save_to_json(self, json_path: str) -> None:
        """Save configuration to a JSON file."""
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            json.dump(self.categories, f, indent=2, ensure_ascii=False)
