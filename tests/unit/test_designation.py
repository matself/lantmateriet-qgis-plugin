#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.unit.test_designation

Note on ``block`` typing: ``parse_designation`` converts a numeric ``block``
to ``int`` when both block and enhet are given (colon form), while
``parse_designation_exact`` keeps a numeric ``block`` as ``str`` in the
equivalent case - see ``test_block_type_differs_between_parse_and_parse_exact``.
This pre-existing inconsistency is unrelated to the ``s``/``ga`` parsing fix
below and is left as-is.
"""

import unittest

from lantmateriet_qgis.core.util import cql2
from lantmateriet_qgis.core.util.designation import (
    parse_designation,
    parse_designation_exact,
)


class TestParseDesignation(unittest.TestCase):
    def test_empty_string_returns_none(self):
        self.assertIsNone(parse_designation(""))

    def test_digits_only_returns_none(self):
        # designation_re requires at least one non-digit character up front.
        self.assertIsNone(parse_designation("123"))

    def test_name_only(self):
        self.assertEqual(
            parse_designation("Morby"),
            [cql2.and_([cql2.startswith(cql2.property("trakt"), "MORBY")])],
        )

    def test_name_with_municipality_prefix(self):
        result = parse_designation("Danderyd Morby")
        self.assertEqual(
            result,
            [
                cql2.and_(
                    [
                        cql2.equals(cql2.property("kommunkod"), "0162"),
                        cql2.startswith(cql2.property("trakt"), "MORBY"),
                    ]
                )
            ],
        )

    def test_name_with_single_number_splits_into_two_queries(self):
        # With only one number and no colon, it's ambiguous whether that
        # number is a block or an enhet, so two queries are returned.
        result = parse_designation("Morby 1")
        self.assertEqual(
            result,
            [
                cql2.and_(
                    [
                        cql2.startswith(cql2.property("trakt"), "MORBY"),
                        cql2.startswith(cql2.property("block"), "1"),
                    ]
                ),
                cql2.and_(
                    [
                        cql2.startswith(cql2.property("trakt"), "MORBY"),
                        cql2.is_null(cql2.property("block")),
                        cql2.equals(cql2.property("enhet"), 1),
                    ]
                ),
            ],
        )

    def test_name_with_block_and_enhet(self):
        result = parse_designation("Morby 1:1")
        self.assertEqual(
            result,
            [
                cql2.and_(
                    [
                        cql2.startswith(cql2.property("trakt"), "MORBY"),
                        cql2.equals(cql2.property("block"), 1),
                        cql2.equals(cql2.property("enhet"), 1),
                    ]
                )
            ],
        )

    def test_municipality_prefix_with_block_and_enhet(self):
        result = parse_designation("Danderyd Morby 1:1")
        self.assertEqual(
            result,
            [
                cql2.and_(
                    [
                        cql2.equals(cql2.property("kommunkod"), "0162"),
                        cql2.startswith(cql2.property("trakt"), "MORBY"),
                        cql2.equals(cql2.property("block"), 1),
                        cql2.equals(cql2.property("enhet"), 1),
                    ]
                )
            ],
        )

    def test_samfallighet_colon_notation(self):
        # "Morby s:1" designates samfällighet 1 in Morby, structurally
        # equivalent to how "Morby 1:1" designates fastighet 1:1 - block is
        # the literal string "s" rather than a number.
        result = parse_designation("Morby s:1")
        self.assertEqual(
            result,
            [
                cql2.and_(
                    [
                        cql2.startswith(cql2.property("trakt"), "MORBY"),
                        cql2.equals(cql2.property("block"), "s"),
                        cql2.equals(cql2.property("enhet"), 1),
                    ]
                )
            ],
        )

    def test_gemensamhetsanlaggning_colon_notation(self):
        result = parse_designation("Morby ga:2")
        self.assertEqual(
            result,
            [
                cql2.and_(
                    [
                        cql2.startswith(cql2.property("trakt"), "MORBY"),
                        cql2.equals(cql2.property("block"), "ga"),
                        cql2.equals(cql2.property("enhet"), 2),
                    ]
                )
            ],
        )

    def test_municipality_prefix_with_samfallighet_colon_notation(self):
        result = parse_designation("Danderyd Morby s:1")
        self.assertEqual(
            result,
            [
                cql2.and_(
                    [
                        cql2.equals(cql2.property("kommunkod"), "0162"),
                        cql2.startswith(cql2.property("trakt"), "MORBY"),
                        cql2.equals(cql2.property("block"), "s"),
                        cql2.equals(cql2.property("enhet"), 1),
                    ]
                )
            ],
        )

    def test_name_ending_in_bare_s_without_colon_is_not_split(self):
        # A name that happens to end in "s" (e.g. a place name) must not be
        # misread as an empty name plus a bare "s" block when there's no
        # colon-enhet after it. "Xyzzys" is not a real designation, just a
        # non-digit name that happens to end in "s" and isn't a municipality.
        result = parse_designation("Xyzzys")
        self.assertEqual(
            result,
            [cql2.and_([cql2.startswith(cql2.property("trakt"), "XYZZYS")])],
        )

    def test_bare_s_without_colon_is_not_treated_as_block(self):
        # Without a colon+enhet, "s"/"ga" are ambiguous the same way a lone
        # trailing letter would be, so they're left as part of the name
        # rather than being guessed at.
        result = parse_designation("Morby s")
        self.assertEqual(
            result,
            [cql2.and_([cql2.startswith(cql2.property("trakt"), "MORBY S")])],
        )

    def test_block_type_differs_between_parse_and_parse_exact(self):
        # parse_designation returns block as int in the block:enhet form...
        with_colon = parse_designation("Morby 1:1")[0]
        block_arg = with_colon["args"][1]["args"][1]
        self.assertIsInstance(block_arg, int)

        # ...while parse_designation_exact returns it as a str.
        exact = parse_designation_exact("Morby 1:1")
        exact_block_arg = exact["args"][1]["args"][1]
        self.assertIsInstance(exact_block_arg, str)


class TestParseDesignationExact(unittest.TestCase):
    def test_empty_string_returns_none(self):
        self.assertIsNone(parse_designation_exact(""))

    def test_name_only_returns_none(self):
        # parse_designation_exact requires at least a block/enhet number.
        self.assertIsNone(parse_designation_exact("Morby"))

    def test_name_with_enhet_only(self):
        result = parse_designation_exact("Morby 1")
        self.assertEqual(
            result,
            cql2.and_(
                [
                    cql2.equals(cql2.property("trakt"), "MORBY"),
                    cql2.is_null(cql2.property("block")),
                    cql2.equals(cql2.property("enhet"), 1),
                ]
            ),
        )

    def test_name_with_block_and_enhet(self):
        result = parse_designation_exact("Morby 1:1")
        self.assertEqual(
            result,
            cql2.and_(
                [
                    cql2.equals(cql2.property("trakt"), "MORBY"),
                    cql2.equals(cql2.property("block"), "1"),
                    cql2.equals(cql2.property("enhet"), 1),
                ]
            ),
        )

    def test_municipality_prefix(self):
        result = parse_designation_exact("Danderyd Morby 1:1")
        self.assertEqual(
            result,
            cql2.and_(
                [
                    cql2.equals(cql2.property("kommunkod"), "0162"),
                    cql2.equals(cql2.property("trakt"), "MORBY"),
                    cql2.equals(cql2.property("block"), "1"),
                    cql2.equals(cql2.property("enhet"), 1),
                ]
            ),
        )

    def test_samfallighet_colon_notation(self):
        result = parse_designation_exact("Morby s:1")
        self.assertEqual(
            result,
            cql2.and_(
                [
                    cql2.equals(cql2.property("trakt"), "MORBY"),
                    cql2.equals(cql2.property("block"), "s"),
                    cql2.equals(cql2.property("enhet"), 1),
                ]
            ),
        )

    def test_gemensamhetsanlaggning_colon_notation(self):
        result = parse_designation_exact("Morby ga:2")
        self.assertEqual(
            result,
            cql2.and_(
                [
                    cql2.equals(cql2.property("trakt"), "MORBY"),
                    cql2.equals(cql2.property("block"), "ga"),
                    cql2.equals(cql2.property("enhet"), 2),
                ]
            ),
        )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
