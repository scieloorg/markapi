from django.test import TestCase
from django.utils.functional import Promise

from core.choices import GENDER_CHOICES, LANGUAGE, LICENSE_TYPES, MONTHS, ROLE


class LanguageChoicesTest(TestCase):
    def test_language_is_list(self):
        self.assertIsInstance(LANGUAGE, list)

    def test_language_covers_iso_639_1(self):
        codes = [code for code, _ in LANGUAGE]
        # Verify some well-known ISO 639-1 codes are present
        for code in ["en", "es", "pt", "fr", "de", "zh", "ja", "ar", "ru", "hi"]:
            self.assertIn(code, codes)

    def test_language_entries_are_tuples(self):
        for entry in LANGUAGE:
            self.assertIsInstance(entry, tuple)
            self.assertEqual(len(entry), 2)

    def test_language_codes_are_two_chars(self):
        for code, _ in LANGUAGE:
            self.assertEqual(len(code), 2, f"Language code '{code}' is not 2 characters")


class RoleChoicesTest(TestCase):
    def test_role_is_list(self):
        self.assertIsInstance(ROLE, list)

    def test_role_has_entries(self):
        self.assertGreater(len(ROLE), 0)

    def test_role_labels_are_lazy_strings(self):
        for _, label in ROLE:
            self.assertIsInstance(label, Promise)


class MonthsChoicesTest(TestCase):
    def test_months_is_list(self):
        self.assertIsInstance(MONTHS, list)

    def test_months_has_twelve_entries(self):
        self.assertEqual(len(MONTHS), 12)

    def test_months_labels_are_lazy_strings(self):
        for _, label in MONTHS:
            self.assertIsInstance(label, Promise)

    def test_months_codes_are_zero_padded(self):
        expected_codes = [f"{i:02d}" for i in range(1, 13)]
        actual_codes = [code for code, _ in MONTHS]
        self.assertEqual(actual_codes, expected_codes)


class LicenseTypesChoicesTest(TestCase):
    def test_license_types_is_list(self):
        self.assertIsInstance(LICENSE_TYPES, list)

    def test_license_types_has_six_entries(self):
        self.assertEqual(len(LICENSE_TYPES), 6)

    def test_license_types_covers_all_cc_types(self):
        codes = [code for code, _ in LICENSE_TYPES]
        expected = ["by", "by-sa", "by-nc", "by-nc-sa", "by-nd", "by-nc-nd"]
        self.assertEqual(codes, expected)

    def test_license_types_labels_are_lazy_strings(self):
        for _, label in LICENSE_TYPES:
            self.assertIsInstance(label, Promise)


class GenderChoicesTest(TestCase):
    def test_gender_choices_is_list(self):
        self.assertIsInstance(GENDER_CHOICES, list)

    def test_gender_choices_has_entries(self):
        self.assertGreater(len(GENDER_CHOICES), 0)

    def test_gender_choices_labels_are_lazy_strings(self):
        for _, label in GENDER_CHOICES:
            self.assertIsInstance(label, Promise)
