# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

"""
Test the signature producing strategy.
"""

import unittest

from hypothesis import errors
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies

from hs_dbus_signature import dbus_signatures

from hs_dbus_signature._signature import _DBusSignatureStrategy

_TYPE_CODES = _DBusSignatureStrategy.CODES
_CODES = _TYPE_CODES + ['a', '{', '(']
_NUM_CODES = len(_CODES)

@strategies.composite
def dbus_signature_strategy(draw):
    """
    Generates any valid dbus signature strategy.
    """
    max_codes = draw(strategies.integers(min_value=1, max_value=10))
    min_complete_types = draw(strategies.integers(min_value=0, max_value=10))
    max_complete_types = draw(
       strategies.one_of(
          strategies.integers(min_value=min_complete_types, max_value=10),
          strategies.none()
       )
    )
    min_struct_len = draw(strategies.integers(min_value=1, max_value=10))
    max_struct_len = draw(
       strategies.one_of(
          strategies.integers(min_value=min_struct_len, max_value=10),
          strategies.none()
       )
    )
    blacklist_chars = \
       strategies.frozensets(elements=strategies.sampled_from(_CODES)). \
          filter(lambda x: len(x) < _NUM_CODES)
    blacklist = draw(
       strategies.one_of(
          blacklist_chars.flatmap(lambda x: strategies.just("".join(x))),
          strategies.none()
       )
    )

    return dbus_signatures(
       max_codes=max_codes,
       min_complete_types=min_complete_types,
       max_complete_types=max_complete_types,
       min_struct_len=min_struct_len,
       max_struct_len=max_struct_len,
       blacklist=blacklist
    )

class SignatureStrategyTestCase(unittest.TestCase):
    """
    Test for the signature strategy.
    """

    @given(
       strategies.text(
          alphabet=strategies.sampled_from(_CODES),
          min_size=1,
          max_size=len(_CODES)
       ).flatmap(
          lambda x: strategies.tuples(
             strategies.just(x),
             dbus_signatures(blacklist=x)
          )
       )
    )
    def testOmitsBlacklist(self, strategy):
        """
        Make sure all characters in blacklist are missing from signature.
        """
        (blacklist, signature) = strategy
        assert [x for x in blacklist if x in signature] == []

    @given(
       strategies.integers(min_value=2, max_value=10). \
       flatmap(
          lambda x: strategies.tuples(
             strategies.just(x),
             dbus_signatures(
                   max_codes=x,
                   min_complete_types=1,
                   max_complete_types=1,
                   blacklist='{'
             )
          )
       )
    )
    @settings(max_examples=100)
    def testBounds(self, strategy):
        """
        Verify that the number of codes in a single complete type does not
        exceed the max number of codes, so long as dict entry types are omitted.
        """
        (max_codes, signature) = strategy
        leaves = [x for x in signature if x in _DBusSignatureStrategy.CODES]
        assert len(leaves) <= max_codes

    @given(dbus_signature_strategy()) # pylint: disable=no-value-for-parameter
    @settings(max_examples=50)
    def testNoBlacklist(self, strategy):
        """
        Just make sure there is a result for an arbitrary legal strategy.
        """
        self.assertIsNotNone(strategy.example())

    def testSuperSetBlacklist(self):
        """
        Verify correct behavior when blacklist contains all type codes.
        """
        blacklist = ''.join(_TYPE_CODES)
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(blacklist=blacklist)

    def testConflictingMinMax(self):
        """
        If the minimum complete types is greater than the maximum, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(min_complete_types=3, max_complete_types=2)

    def testNegativeMax(self):
        """
        If the max is less than 0, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(min_complete_types=-1)

    def testNonPositiveMax(self):
        """
        If the maximum struct length is less than 1, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(min_struct_len=0)

    def testConflictingMinMaxStructLen(self):
        """
        If the minimum complete types is greater than the maximum, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(min_struct_len=3, max_struct_len=2)

    def testMaxTypeCodes(self):
        """
        If the maximum type codes is less than 1, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(max_codes=0)
