from django.contrib.auth import get_user_model
from django.test import TestCase

from core import choices
from core.models import (
    FileWithLang,
    FlexibleDate,
    Gender,
    Language,
    LanguageFallbackManager,
    License,
    LicenseStatement,
    RichTextWithLanguage,
    TextLanguageMixin,
    TextWithLang,
)
from core.utils.utils import language_iso

User = get_user_model()


class LanguageIsoTest(TestCase):
    def test_language_iso_normalizes_code(self):
        self.assertEqual(language_iso("pt"), "pt")

    def test_language_iso_splits_on_hyphen(self):
        self.assertEqual(language_iso("pt-BR"), "pt")

    def test_language_iso_splits_on_underscore(self):
        self.assertEqual(language_iso("pt_BR"), "pt")

    def test_language_iso_empty_string(self):
        self.assertEqual(language_iso(""), "")

    def test_language_iso_none(self):
        self.assertEqual(language_iso(None), "")

    def test_language_iso_invalid(self):
        self.assertEqual(language_iso("xyz123"), "")


class GenderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_create_or_update_creates_new(self):
        gender = Gender.create_or_update(self.user, code="M", gender="Male")
        self.assertIsNotNone(gender)
        self.assertEqual(gender.code, "M")
        self.assertEqual(gender.gender, "Male")

    def test_create_or_update_returns_existing(self):
        g1 = Gender.create_or_update(self.user, code="F", gender="Female")
        g2 = Gender.create_or_update(self.user, code="F", gender="Female")
        self.assertEqual(g1.pk, g2.pk)

    def test_unique_together(self):
        Gender.create_or_update(self.user, code="M", gender="Male")
        self.assertEqual(Gender.objects.filter(code="M", gender="Male").count(), 1)

    def test_str(self):
        gender = Gender.create_or_update(self.user, code="M", gender="Male")
        self.assertEqual(str(gender), "Male")

    def test_load(self):
        Gender.load(self.user)
        self.assertEqual(Gender.objects.count(), len(choices.GENDER_CHOICES))


class LanguageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_get_or_create_creates_new(self):
        lang = Language.get_or_create(name="English", code2="en", creator=self.user)
        self.assertIsNotNone(lang)
        self.assertEqual(lang.code2, "en")
        self.assertEqual(lang.name, "English")

    def test_get_or_create_normalizes_code2(self):
        lang = Language.get_or_create(name="Portuguese", code2="pt-BR", creator=self.user)
        self.assertEqual(lang.code2, "pt")

    def test_get_or_create_returns_existing(self):
        l1 = Language.get_or_create(name="English", code2="en", creator=self.user)
        l2 = Language.get_or_create(name="English", code2="en", creator=self.user)
        self.assertEqual(l1.pk, l2.pk)

    def test_load_populates_when_empty(self):
        Language.load(self.user)
        self.assertGreater(Language.objects.count(), 0)

    def test_load_does_not_duplicate(self):
        Language.load(self.user)
        count1 = Language.objects.count()
        Language.load(self.user)
        count2 = Language.objects.count()
        self.assertEqual(count1, count2)

    def test_str(self):
        lang = Language.get_or_create(name="English", code2="en", creator=self.user)
        self.assertEqual(str(lang), "English | en")

    def test_str_none(self):
        lang = Language()
        self.assertEqual(str(lang), "None")


class LicenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_get_uses_iexact(self):
        License.create(self.user, license_type="by")
        lic = License.get("BY")
        self.assertEqual(lic.license_type, "by")

    def test_create_or_update(self):
        l1 = License.create_or_update(self.user, license_type="by-nc")
        l2 = License.create_or_update(self.user, license_type="by-nc")
        self.assertEqual(l1.pk, l2.pk)

    def test_unique_together(self):
        License.create(self.user, license_type="by")
        self.assertEqual(License.objects.filter(license_type="by").count(), 1)

    def test_str(self):
        lic = License.create(self.user, license_type="by")
        self.assertEqual(str(lic), "by")

    def test_get_raises_on_empty(self):
        with self.assertRaises(ValueError):
            License.get(None)


class LicenseStatementModelTest(TestCase):
    def test_parse_url_extracts_type_and_version(self):
        result = LicenseStatement.parse_url(
            "https://creativecommons.org/licenses/by/4.0/"
        )
        self.assertEqual(result["license_type"], "by")
        self.assertEqual(result["license_version"], "4.0")

    def test_parse_url_by_nc(self):
        result = LicenseStatement.parse_url(
            "https://creativecommons.org/licenses/by-nc/3.0/br/"
        )
        self.assertEqual(result["license_type"], "by-nc")
        self.assertEqual(result["license_version"], "3.0")

    def test_parse_url_empty(self):
        result = LicenseStatement.parse_url("")
        self.assertEqual(result, {})

    def test_parse_url_none(self):
        result = LicenseStatement.parse_url(None)
        self.assertEqual(result, {})

    def test_parse_url_invalid(self):
        result = LicenseStatement.parse_url("https://example.com/")
        self.assertEqual(result, {})

    def test_str(self):
        ls = LicenseStatement(url="https://creativecommons.org/licenses/by/4.0/")
        self.assertEqual(str(ls), "https://creativecommons.org/licenses/by/4.0/")


class FlexibleDateModelTest(TestCase):
    def test_data_property(self):
        fd = FlexibleDate(year=2024, month=3, day=15)
        expected = {
            "date__year": 2024,
            "date__month": 3,
            "date__day": 15,
        }
        self.assertEqual(fd.data, expected)

    def test_data_property_with_none(self):
        fd = FlexibleDate(year=2024)
        expected = {
            "date__year": 2024,
            "date__month": None,
            "date__day": None,
        }
        self.assertEqual(fd.data, expected)

    def test_str(self):
        fd = FlexibleDate(year=2024, month=3, day=15)
        self.assertEqual(str(fd), "2024/3/15")


class AbstractModelsTest(TestCase):
    def test_text_with_lang_is_abstract(self):
        self.assertTrue(TextWithLang._meta.abstract)

    def test_text_language_mixin_is_abstract(self):
        self.assertTrue(TextLanguageMixin._meta.abstract)

    def test_rich_text_with_language_is_abstract(self):
        self.assertTrue(RichTextWithLanguage._meta.abstract)

    def test_file_with_lang_is_abstract(self):
        self.assertTrue(FileWithLang._meta.abstract)

    def test_flexible_date_is_not_abstract(self):
        self.assertFalse(FlexibleDate._meta.abstract)

    def test_gender_is_not_abstract(self):
        self.assertFalse(Gender._meta.abstract)

    def test_language_is_not_abstract(self):
        self.assertFalse(Language._meta.abstract)

    def test_license_is_not_abstract(self):
        self.assertFalse(License._meta.abstract)

    def test_license_statement_is_not_abstract(self):
        self.assertFalse(LicenseStatement._meta.abstract)


class LanguageFallbackManagerTest(TestCase):
    def test_manager_is_language_fallback_manager(self):
        # Abstract models pass their managers to concrete subclasses;
        # verify the declared default manager type on the abstract model
        managers = [m for m in RichTextWithLanguage._meta.managers]
        self.assertTrue(
            any(isinstance(m, LanguageFallbackManager) for m in managers)
        )
