"""Unit tests for CategoryConfig class."""

import json

import pytest
import yaml

from personal_finance_toolkit.config.category_config import CategoryConfig


class TestCategoryConfigInitialization:
    """Test CategoryConfig initialization and basic operations."""

    @pytest.fixture
    def basic_config_dict(self):
        """Fixture providing a basic category configuration."""
        return {
            "Groceries": ["Tesco", "Aldi", "Coop"],
            "Utilities": ["Electricity", "Water"],
            "Entertainment": ["Cinema", "Netflix"],
        }

    @pytest.fixture
    def config(self, basic_config_dict):
        """Fixture providing a CategoryConfig instance."""
        return CategoryConfig(basic_config_dict)

    def test_initialization_with_valid_categories(self, basic_config_dict):
        """Test that CategoryConfig initializes correctly with valid categories."""
        config = CategoryConfig(basic_config_dict)
        assert config.categories == basic_config_dict

    def test_initialization_builds_keyword_lookup(self, basic_config_dict):
        """Test that keyword lookup is built during initialization."""
        config = CategoryConfig(basic_config_dict)
        assert len(config._keyword_to_category) > 0
        assert "tesco" in config._keyword_to_category
        assert config._keyword_to_category["tesco"] == "Groceries"

    def test_keyword_lookup_is_lowercase(self, config):
        """Test that keyword lookup uses lowercase keys."""
        assert "electricity" in config._keyword_to_category
        assert "cinema" in config._keyword_to_category

    def test_empty_categories(self):
        """Test initialization with empty categories."""
        config = CategoryConfig({})
        assert config.categories == {}
        assert len(config._keyword_to_category) == 0

    def test_category_with_empty_keywords(self):
        """Test initialization with category containing empty keyword list."""
        categories = {"EmptyCategory": [], "WithKeywords": ["Keyword1"]}
        config = CategoryConfig(categories)
        # Categories with empty keywords don't create entries in the lookup
        assert "emptycat" not in config._keyword_to_category
        # But categories with keywords should have entries
        assert "keyword1" in config._keyword_to_category
        assert config._keyword_to_category["keyword1"] == "WithKeywords"


class TestCategoryConfigGetters:
    """Test getter methods of CategoryConfig."""

    @pytest.fixture
    def config(self):
        """Fixture providing a populated CategoryConfig instance."""
        categories = {
            "Groceries": ["Tesco", "Aldi", "Coop"],
            "Utilities": ["Electricity", "Water"],
            "Entertainment": ["Cinema", "Netflix", "Gaming"],
        }
        return CategoryConfig(categories)

    @pytest.mark.parametrize(
        "expected_categories",
        [["Groceries", "Utilities", "Entertainment"]],
    )
    def test_get_categories_returns_all_categories(self, config, expected_categories):
        """Test that get_categories returns all defined categories."""
        categories = config.get_categories()
        assert set(categories) == set(expected_categories)

    @pytest.mark.parametrize(
        ("category", "expected_keywords"),
        [
            ("Groceries", ["Tesco", "Aldi", "Coop"]),
            ("Utilities", ["Electricity", "Water"]),
            ("Entertainment", ["Cinema", "Netflix", "Gaming"]),
        ],
    )
    def test_get_keywords_returns_keywords_for_category(self, config, category, expected_keywords):
        """Test that get_keywords returns correct keywords for each category."""
        keywords = config.get_keywords(category)
        assert keywords == expected_keywords

    def test_get_keywords_returns_empty_list_for_unknown_category(self, config):
        """Test that get_keywords returns empty list for unknown category."""
        keywords = config.get_keywords("UnknownCategory")
        assert keywords == []


class TestCategoryConfigFindCategory:
    """Test category matching functionality."""

    @pytest.fixture
    def config(self):
        """Fixture providing a CategoryConfig instance."""
        return CategoryConfig(
            {
                "Groceries": ["Tesco", "Aldi", "Supermarket"],
                "Utilities": ["Electricity", "Water Company"],
                "Entertainment": ["Netflix", "Cinema"],
            }
        )

    @pytest.mark.parametrize(
        ("text", "expected_category"),
        [
            ("Tesco Store", "Groceries"),
            ("tesco store", "Groceries"),  # Case-insensitive
            ("ALDI", "Groceries"),  # Full uppercase
            ("I shop at Supermarket", "Groceries"),  # Substring match
            ("Electricity Company", "Utilities"),
            ("Netflix Subscription", "Entertainment"),
            ("Cinema Tickets", "Entertainment"),
        ],
    )
    def test_find_category_matches_keywords(self, config, text, expected_category):
        """Test that find_category correctly matches keywords."""
        category = config.find_category(text)
        assert category == expected_category

    @pytest.mark.parametrize(
        "text",
        [
            "",
            "Unknown Vendor",
            "RandomText",
            "No Match Here",
        ],
    )
    def test_find_category_returns_none_for_unmatched_text(self, config, text):
        """Test that find_category returns None when no match is found."""
        category = config.find_category(text)
        assert category is None

    def test_find_category_returns_none_for_empty_string(self, config):
        """Test that find_category returns None for empty string."""
        assert config.find_category("") is None

    def test_find_category_returns_none_for_none_text(self, config):
        """Test that find_category returns None for None input."""
        assert config.find_category(None) is None

    def test_find_category_is_case_insensitive(self, config):
        """Test various case combinations for case-insensitive matching."""
        assert config.find_category("TESCO") == "Groceries"
        assert config.find_category("tEsCo") == "Groceries"
        assert config.find_category("TeScO PartnEr") == "Groceries"


class TestCategoryConfigFileOperations:
    """Test loading and saving configuration files."""

    @pytest.fixture
    def sample_yaml_content(self):
        """Fixture providing sample YAML content."""
        return {
            "Groceries": ["Tesco", "Aldi"],
            "Utilities": ["Electricity"],
        }

    @pytest.fixture
    def sample_json_content(self):
        """Fixture providing sample JSON content."""
        return {
            "Groceries": ["Tesco", "Aldi"],
            "Utilities": ["Electricity"],
        }

    @pytest.mark.parametrize(
        "categories",
        [
            {"Single": ["Keyword"]},
            {"Cat1": ["K1", "K2"], "Cat2": ["K3"]},
            {
                "Groceries": ["Tesco", "Aldi", "Carrefour"],
                "Entertainment": ["Netflix", "Cinema"],
            },
        ],
    )
    def test_load_from_yaml_valid_file(self, tmp_path, categories):
        """Test loading configuration from valid YAML file."""
        yaml_file = tmp_path / "config.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(categories, f)

        config = CategoryConfig.from_yaml(str(yaml_file))
        assert config.categories == categories

    def test_from_yaml_file_not_found(self):
        """Test that from_yaml raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            CategoryConfig.from_yaml("/nonexistent/path/config.yaml")

    def test_from_yaml_invalid_format_not_dict(self, tmp_path):
        """Test that from_yaml raises TypeError for non-dict content."""
        yaml_file = tmp_path / "invalid.yaml"
        with open(yaml_file, "w") as f:
            f.write("- item1\n- item2\n")  # List instead of dict

        with pytest.raises(TypeError, match="must contain a dictionary"):
            CategoryConfig.from_yaml(str(yaml_file))

    @pytest.mark.parametrize(
        "categories",
        [
            {"Single": ["Keyword"]},
            {"Cat1": ["K1", "K2"], "Cat2": ["K3"]},
        ],
    )
    def test_load_from_json_valid_file(self, tmp_path, categories):
        """Test loading configuration from valid JSON file."""
        json_file = tmp_path / "config.json"
        with open(json_file, "w") as f:
            json.dump(categories, f)

        config = CategoryConfig.from_json(str(json_file))
        assert config.categories == categories

    def test_from_json_file_not_found(self):
        """Test that from_json raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            CategoryConfig.from_json("/nonexistent/path/config.json")

    def test_from_json_invalid_format_not_dict(self, tmp_path):
        """Test that from_json raises TypeError for non-dict content."""
        json_file = tmp_path / "invalid.json"
        with open(json_file, "w") as f:
            json.dump(["item1", "item2"], f)  # List instead of dict

        with pytest.raises(TypeError, match="must contain a dictionary"):
            CategoryConfig.from_json(str(json_file))

    def test_save_to_yaml(self, tmp_path):
        """Test saving configuration to YAML file."""
        categories = {
            "Groceries": ["Tesco", "Aldi"],
            "Utilities": ["Electricity"],
        }
        config = CategoryConfig(categories)
        yaml_file = tmp_path / "output.yaml"

        config.save_to_yaml(str(yaml_file))

        assert yaml_file.exists()
        loaded = CategoryConfig.from_yaml(str(yaml_file))
        assert loaded.categories == categories

    def test_save_to_yaml_creates_parent_directories(self, tmp_path):
        """Test that save_to_yaml creates parent directories if needed."""
        categories = {"Test": ["Keyword"]}
        config = CategoryConfig(categories)
        yaml_file = tmp_path / "nested" / "deep" / "config.yaml"

        config.save_to_yaml(str(yaml_file))

        assert yaml_file.exists()
        assert yaml_file.parent.is_dir()

    def test_save_to_json(self, tmp_path):
        """Test saving configuration to JSON file."""
        categories = {
            "Groceries": ["Tesco", "Aldi"],
            "Utilities": ["Electricity"],
        }
        config = CategoryConfig(categories)
        json_file = tmp_path / "output.json"

        config.save_to_json(str(json_file))

        assert json_file.exists()
        loaded = CategoryConfig.from_json(str(json_file))
        assert loaded.categories == categories

    def test_save_to_json_creates_parent_directories(self, tmp_path):
        """Test that save_to_json creates parent directories if needed."""
        categories = {"Test": ["Keyword"]}
        config = CategoryConfig(categories)
        json_file = tmp_path / "nested" / "deep" / "config.json"

        config.save_to_json(str(json_file))

        assert json_file.exists()
        assert json_file.parent.is_dir()


class TestCategoryConfigEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.parametrize(
        "categories",
        [
            {"Category": [""]},  # Empty keyword
            {"": ["Keyword"]},  # Empty category name
            {"Category": ["  "]},  # Whitespace keyword
        ],
    )
    def test_handles_edge_case_empty_strings(self, categories):
        """Test that CategoryConfig handles edge cases with empty strings."""
        config = CategoryConfig(categories)
        assert config.categories == categories

    def test_special_characters_in_keywords(self):
        """Test handling of special characters in keywords."""
        categories = {
            "Shopping": ["Amazon & eBay", "H&M", "C&A"],
            "Services": ["AT&T"],
        }
        config = CategoryConfig(categories)
        assert config.find_category("Amazon & eBay Store") == "Shopping"
        assert config.find_category("visit h&m") == "Shopping"

    def test_unicode_characters_in_keywords(self):
        """Test handling of Unicode characters in keywords."""
        categories = {
            "Utilities": ["ELMŰ", "TIGÁZ"],
            "Groceries": ["Carrefour", "Netto"],
        }
        config = CategoryConfig(categories)
        assert config.find_category("ELMŰ Számla") == "Utilities"
        assert config.find_category("tigáz") == "Utilities"

    def test_very_long_text(self):
        """Test matching with very long text content."""
        categories = {"Target": ["keyword"]}
        config = CategoryConfig(categories)
        long_text = "A" * 10000 + " keyword " + "B" * 10000
        assert config.find_category(long_text) == "Target"

    def test_multiple_keyword_matches_returns_first_match(self):
        """Test behavior when multiple keywords could match."""
        # Keywords from different categories that could both match
        categories = {
            "Entertainment": ["Netflix"],
            "Subscriptions": ["Netflix Plus"],
        }
        config = CategoryConfig(categories)
        # Should return based on which is checked first
        result = config.find_category("Netflix subscription")
        assert result in ["Entertainment", "Subscriptions"]
