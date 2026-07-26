#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.unit.test_core_util
"""

import unittest

from lantmateriet_qgis.core.util import UUID_RE, flatten, omit


class TestOmit(unittest.TestCase):
    def test_removes_given_keys(self):
        self.assertEqual(
            omit({"a": 1, "b": 2, "c": 3}, ["b"]),
            {"a": 1, "c": 3},
        )

    def test_removes_multiple_keys(self):
        self.assertEqual(
            omit({"a": 1, "b": 2, "c": 3}, ["a", "c"]),
            {"b": 2},
        )

    def test_missing_keys_are_ignored(self):
        self.assertEqual(
            omit({"a": 1}, ["b"]),
            {"a": 1},
        )

    def test_empty_dict(self):
        self.assertEqual(omit({}, ["a"]), {})

    def test_does_not_mutate_input(self):
        data = {"a": 1, "b": 2}
        omit(data, ["a"])
        self.assertEqual(data, {"a": 1, "b": 2})


class TestFlatten(unittest.TestCase):
    def test_flat_dict_is_unchanged(self):
        self.assertEqual(flatten({"a": 1, "b": 2}), {"a": 1, "b": 2})

    def test_nested_dict(self):
        self.assertEqual(
            flatten({"a": 1, "b": {"c": 2, "d": 3}}),
            {"a": 1, "b.c": 2, "b.d": 3},
        )

    def test_deeply_nested_dict(self):
        self.assertEqual(
            flatten({"a": {"b": {"c": 1}}}),
            {"a.b.c": 1},
        )

    def test_list_of_scalars(self):
        self.assertEqual(
            flatten({"a": [1, 2, 3]}),
            {"a.0": 1, "a.1": 2, "a.2": 3},
        )

    def test_list_of_dicts(self):
        self.assertEqual(
            flatten({"a": [{"x": 1}, {"y": 2}]}),
            {"a.0.x": 1, "a.1.y": 2},
        )

    def test_empty_dict(self):
        self.assertEqual(flatten({}), {})

    def test_empty_list(self):
        self.assertEqual(flatten({"a": []}), {})


class TestUuidRe(unittest.TestCase):
    def test_matches_lowercase_uuid(self):
        self.assertIsNotNone(
            UUID_RE.fullmatch("123e4567-e89b-12d3-a456-426614174000")
        )

    def test_does_not_match_uppercase_uuid(self):
        # UUID_RE only matches lowercase hex digits.
        self.assertIsNone(
            UUID_RE.fullmatch("123E4567-E89B-12D3-A456-426614174000")
        )

    def test_finds_uuid_within_larger_string(self):
        match = UUID_RE.search("id: 123e4567-e89b-12d3-a456-426614174000 end")
        self.assertEqual(match.group(), "123e4567-e89b-12d3-a456-426614174000")

    def test_does_not_match_malformed_uuid(self):
        self.assertIsNone(UUID_RE.fullmatch("not-a-uuid"))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
