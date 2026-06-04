import unittest

from utrends.text_match import (
    matches_query,
    title_signature,
    titles_similar,
    tracked_topic_matches,
)


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

    def test_tracked_topic_rejects_weak_common_overlap(self):
        self.assertFalse(
            tracked_topic_matches(
                "Apple touts $1.4 trillion in App Store billings and sales",
                "макс удалили из app store",
            )
        )

    def test_tracked_topic_accepts_strong_overlap(self):
        self.assertTrue(
            tracked_topic_matches(
                "Мессенджер Макс удалили из App Store",
                "макс удалили из app store",
            )
        )

    def test_tracked_topic_matches_max_alias(self):
        self.assertTrue(
            tracked_topic_matches(
                "Финуслуги интегрировали сервис в экосистему мессенджера Макс",
                "Мессенджер MAX",
            )
        )

    def test_tracked_topic_rejects_generic_putin_overlap(self):
        self.assertFalse(
            tracked_topic_matches(
                "Путин не планирует встречаться с делегацией США на ПМЭФ",
                "Путин заявил, что от Украины не",
            )
        )


if __name__ == "__main__":
    unittest.main()
