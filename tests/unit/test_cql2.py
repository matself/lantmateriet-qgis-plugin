#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.unit.test_cql2
"""

import unittest

from lantmateriet_qgis.core.util import cql2


class TestProperty(unittest.TestCase):
    def test_property(self):
        self.assertEqual(cql2.property("trakt"), {"property": "trakt"})


class TestLike(unittest.TestCase):
    def test_like_with_string_operand(self):
        self.assertEqual(
            cql2.like(cql2.property("trakt"), "MORBY%"),
            {"op": "like", "args": [{"property": "trakt"}, "MORBY%"]},
        )

    def test_like_with_property_operand(self):
        self.assertEqual(
            cql2.like(cql2.property("a"), cql2.property("b")),
            {"op": "like", "args": [{"property": "a"}, {"property": "b"}]},
        )


class TestStartswith(unittest.TestCase):
    def test_appends_wildcard(self):
        self.assertEqual(
            cql2.startswith(cql2.property("trakt"), "MORBY"),
            {"op": "like", "args": [{"property": "trakt"}, "MORBY%"]},
        )

    def test_empty_prefix(self):
        self.assertEqual(
            cql2.startswith(cql2.property("trakt"), ""),
            {"op": "like", "args": [{"property": "trakt"}, "%"]},
        )


class TestEquals(unittest.TestCase):
    def test_equals_string(self):
        self.assertEqual(
            cql2.equals(cql2.property("kommunkod"), "0162"),
            {"op": "=", "args": [{"property": "kommunkod"}, "0162"]},
        )

    def test_equals_int(self):
        self.assertEqual(
            cql2.equals(cql2.property("enhet"), 1),
            {"op": "=", "args": [{"property": "enhet"}, 1]},
        )

    def test_equals_nested_property(self):
        self.assertEqual(
            cql2.equals(cql2.property("a"), cql2.property("b")),
            {"op": "=", "args": [{"property": "a"}, {"property": "b"}]},
        )


class TestBetween(unittest.TestCase):
    def test_between(self):
        self.assertEqual(
            cql2.between(cql2.property("enhet"), 1, 10),
            {"op": "between", "args": [{"property": "enhet"}, 1, 10]},
        )


class TestIn(unittest.TestCase):
    def test_single_item_collapses_to_equals(self):
        self.assertEqual(
            cql2.in_(cql2.property("enhet"), [1]),
            cql2.equals(cql2.property("enhet"), 1),
        )

    def test_multiple_items_uses_in_operator(self):
        self.assertEqual(
            cql2.in_(cql2.property("enhet"), [1, 2, 3]),
            {"op": "in", "args": [{"property": "enhet"}, [1, 2, 3]]},
        )

    def test_empty_list_uses_in_operator(self):
        self.assertEqual(
            cql2.in_(cql2.property("enhet"), []),
            {"op": "in", "args": [{"property": "enhet"}, []]},
        )


class TestIsNull(unittest.TestCase):
    def test_is_null(self):
        self.assertEqual(
            cql2.is_null(cql2.property("block")),
            {"op": "isNull", "args": [{"property": "block"}]},
        )


class TestPlus(unittest.TestCase):
    def test_plus(self):
        self.assertEqual(
            cql2.plus(cql2.property("a"), cql2.property("b")),
            {"op": "+", "args": [{"property": "a"}, {"property": "b"}]},
        )

    def test_plus_with_string_operand(self):
        self.assertEqual(
            cql2.plus("prefix-", cql2.property("a")),
            {"op": "+", "args": ["prefix-", {"property": "a"}]},
        )


class TestAnd(unittest.TestCase):
    def test_single_item_collapses_to_that_item(self):
        term = cql2.equals(cql2.property("a"), 1)
        self.assertEqual(cql2.and_([term]), term)

    def test_multiple_items_uses_and_operator(self):
        term_a = cql2.equals(cql2.property("a"), 1)
        term_b = cql2.equals(cql2.property("b"), 2)
        self.assertEqual(
            cql2.and_([term_a, term_b]),
            {"op": "and", "args": [term_a, term_b]},
        )


class TestOr(unittest.TestCase):
    def test_single_item_collapses_to_that_item(self):
        term = cql2.equals(cql2.property("a"), 1)
        self.assertEqual(cql2.or_([term]), term)

    def test_multiple_items_uses_or_operator(self):
        term_a = cql2.equals(cql2.property("a"), 1)
        term_b = cql2.equals(cql2.property("b"), 2)
        self.assertEqual(
            cql2.or_([term_a, term_b]),
            {"op": "or", "args": [term_a, term_b]},
        )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
