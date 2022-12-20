from rsync_zfs_snapshot.schema import Schema
import unittest

EXAMPLE = "tests/data/schema.conf"


class TestSchema(unittest.TestCase):
    def test_sections(self):
        s = Schema(EXAMPLE)
        self.assertListEqual(s.config.sections(), ["normal", "critical", "negative"])

    def test_nonexisting_config(self):
        with self.assertRaises(RuntimeError):
            s = Schema("this-should-not-exist.confg")

    def test_normal(self):
        s = Schema(EXAMPLE)
        self.assertEqual(s.get_count("normal", "hourly"), None)
        self.assertEqual(s.get_count("normal", "daily"), 10)
        self.assertEqual(s.get_count("normal", "monthly"), 5)

    def test_normal(self):
        s = Schema(EXAMPLE)
        self.assertEqual(s.get_count("critical", "hourly"), 4)
        self.assertEqual(s.get_count("critical", "daily"), 30)
        self.assertEqual(s.get_count("critical", "monthly"), 12)
        self.assertEqual(s.get_count("critical", "yearly"), 3)

    def test_illegal_label(self):
        with self.assertRaises(RuntimeError):
            s = Schema(EXAMPLE)
            s.get_count("normal", "unknown")

    def test_negative_label(self):
        with self.assertRaises(RuntimeError):
            s = Schema(EXAMPLE)
            s.get_count("negative", "hourly")
