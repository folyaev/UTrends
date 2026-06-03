import unittest

from text_match import matches_query, title_signature, titles_similar


class TextMatchTests(unittest.TestCase):
    def test_matches_russian_word_forms(self):
        self.assertTrue(matches_query("Мессенджер Max пропал из App Store", "мессенджера max"))

    def test_matches_by_keywords(self):
        self.assertTrue(matches_query("Путин заявил о новом качестве конфликта", "новое качество конфликт"))

    def test_title_similarity_ignores_common_noise(self):
        self.assertTrue(
            titles_similar(
                "Мессенджер Max пропал из App Store",
                "Мессенджера MAX больше нет в App Store",
            )
        )

    def test_title_signature_is_stable_for_word_order(self):
        self.assertEqual(
            title_signature("Max пропал из App Store"),
            title_signature("App Store: пропал Max"),
        )


if __name__ == "__main__":
    unittest.main()
