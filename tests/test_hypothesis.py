# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""
Hypothesis-based testing of the signature producing strategy.
"""

# isort: STDLIB
import unittest
from os import sys

# isort: THIRDPARTY
from hypothesis import HealthCheck, given, settings, strategies

# isort: LOCAL
from hs_dbus_signature import dbus_signatures
from hs_dbus_signature._signature import _CODES

settings.register_profile("tracing", deadline=None)
if sys.gettrace() is not None:
    settings.load_profile("tracing")


@strategies.composite
def dbus_signature_strategy(draw):
    """
    Generates any valid dbus signature strategy.
    """
    max_codes = draw(strategies.integers(min_value=1, max_value=5))
    min_complete_types = draw(strategies.integers(min_value=0, max_value=5))
    max_complete_types = draw(
        strategies.one_of(
            strategies.integers(min_value=min_complete_types, max_value=5),
            strategies.none(),
        )
    )
    min_struct_len = draw(strategies.integers(min_value=1, max_value=5))
    max_struct_len = draw(
        strategies.one_of(
            strategies.integers(min_value=min_struct_len, max_value=5),
            strategies.none(),
        )
    )
    blacklist_chars = strategies.frozensets(
        elements=strategies.sampled_from(_CODES), max_size=len(_CODES) - 1
    )
    blacklist = draw(strategies.none() | blacklist_chars.map("".join))

    return dbus_signatures(
        max_codes=max_codes,
        min_complete_types=min_complete_types,
        max_complete_types=max_complete_types,
        min_struct_len=min_struct_len,
        max_struct_len=max_struct_len,
        exclude_arrays=not draw(strategies.booleans()),
        exclude_dicts=not draw(strategies.booleans()),
        exclude_structs=not draw(strategies.booleans()),
        blacklist=blacklist,
    )


class SignatureStrategyHypothesisTestCase(unittest.TestCase):
    """
    Test for the signature strategy.
    """

    @given(
        strategies.lists(
            strategies.sampled_from(_CODES),
            min_size=1,
            max_size=len(_CODES) - 1,
            unique=True,
        ).flatmap(
            lambda x: strategies.tuples(
                strategies.just(x), dbus_signatures(blacklist=x)
            )
        )
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_omits_blacklist(self, strategy):
        """
        Make sure all characters in blacklist are missing from signature.
        """
        (blacklist, signature) = strategy
        self.assertEqual([x for x in blacklist if x in signature], [])

    @given(
        strategies.just([x for x in _CODES if x != "v"]).flatmap(
            lambda x: strategies.tuples(
                strategies.just(x), dbus_signatures(blacklist=x)
            )
        )
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.too_slow])
    def test_blacklist_all_but_v(self, strategy):
        """
        Test correct behavior when blacklist excludes all codes but 'v'.
        """
        (blacklist, signature) = strategy
        self.assertEqual([x for x in blacklist if x in signature], [])

    @given(
        strategies.integers(min_value=2, max_value=10).flatmap(
            lambda x: strategies.tuples(
                strategies.just(x),
                dbus_signatures(
                    max_codes=x,
                    min_complete_types=1,
                    max_complete_types=1,
                    exclude_dicts=True,
                ),
            )
        )
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_bounds(self, strategy):
        """
        Verify that the number of codes in a single complete type does not
        exceed the max number of codes, so long as dict entry types are omitted.
        """
        (max_codes, signature) = strategy
        leaves = [x for x in signature if x in _CODES]
        self.assertLessEqual(len(leaves), max_codes)

    @given(strategies.data())  # pylint: disable=no-value-for-parameter
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_no_blacklist(self, data):
        """
        Just make sure there is a result for an arbitrary legal strategy.
        """
        # pylint: disable=no-value-for-parameter
        data.draw(data.draw(dbus_signature_strategy()))
