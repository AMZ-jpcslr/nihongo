"""原文に無い発信者名・組織名と、公式らしさの言葉を足した文を候補に出すか。名前はすべて架空。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "nihongo/scripts"))
from check_meaning import check  # noqa: E402


def sender_items(src, dst):
    return [x for x in check(src, dst) if x.startswith("[発信者・権威]")]


class SenderAuthorityTests(unittest.TestCase):
    def test_added_bank_name_is_flagged(self):
        items = sender_items("口座の確認をお願いします。\n", "東西銀行カスタマーサポートより、口座の確認をお願いします。\n")
        self.assertTrue(any("増えた" in x and "東西銀行" in x for x in items), items)

    def test_added_company_and_office_are_flagged(self):
        items = sender_items("手続きのご案内です。\n", "株式会社サンプルと北南市役所からの手続きのご案内です。\n")
        self.assertTrue(any("株式会社サンプル" in x and "北南市役所" in x for x in items), items)

    def test_added_official_words_are_flagged(self):
        items = sender_items("口座の確認をお願いします。\n", "【重要】公式のお知らせです。口座の確認をお願いします。\n")
        self.assertTrue(any("公式" in x and "【重要】" in x for x in items), items)

    def test_removed_sender_is_flagged(self):
        items = sender_items("東西銀行からのお知らせです。\n", "お知らせです。\n")
        self.assertTrue(any("消えた" in x and "東西銀行" in x for x in items), items)

    def test_kept_own_organization_is_not_flagged(self):
        self.assertEqual(sender_items("東西銀行からのお知らせです。\n", "東西銀行からのお知らせになります。\n"), [])

    def test_kept_official_word_is_not_flagged(self):
        self.assertEqual(sender_items("公式サイトで確かめてください。\n", "公式サイトから確かめてください。\n"), [])

    def test_generic_words_are_not_flagged(self):
        self.assertEqual(sender_items("記載を省略しました。\n", "記載を一部省略しました。\n"), [])
        self.assertEqual(sender_items("手続きできます。\n", "各銀行で手続きできます。\n"), [])


if __name__ == "__main__":
    unittest.main()
