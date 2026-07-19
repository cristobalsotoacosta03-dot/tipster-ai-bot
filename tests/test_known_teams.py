"""Tests for the team-name typo correction helper."""
from src.data.known_teams import correct_team_name_typo


class TestCorrectTeamNameTypo:
    def test_corrects_common_typo(self):
        assert correct_team_name_typo("Real Madrd") == "Real Madrid"

    def test_corrects_missing_letter(self):
        assert correct_team_name_typo("Barcelna") == "Barcelona"

    def test_exact_match_returns_none(self):
        # Nothing to correct - caller should just use the original name.
        assert correct_team_name_typo("Real Madrid") is None

    def test_unrelated_gibberish_returns_none(self):
        assert correct_team_name_typo("xyzqwerty123") is None

    def test_empty_string_returns_none(self):
        assert correct_team_name_typo("") is None
        assert correct_team_name_typo("   ") is None

    def test_different_team_not_confused(self):
        # A real but different team name shouldn't be "corrected" into
        # an unrelated one just because both are in the known list.
        assert correct_team_name_typo("Sevilla") is None
