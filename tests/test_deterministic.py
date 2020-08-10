# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""
Deterministic testing of the signature producing strategy.
"""

# isort: STDLIB
import unittest

# isort: THIRDPARTY
from hypothesis import errors

# isort: LOCAL
from hs_dbus_signature import dbus_signatures
from hs_dbus_signature._signature import _CODES


class SignatureStrategyDeterministicTestCase(unittest.TestCase):
    """
    Test for the signature strategy which are deterministic in operation.
    """

    def test_superset_blacklist(self):
        """
        Verify correct behavior when blacklist contains all type codes.
        """
        blacklist = "".join(_CODES)
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(blacklist=blacklist)

    def test_conflicting_min_max(self):
        """
        If the minimum complete types is greater than the maximum, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(min_complete_types=3, max_complete_types=2)

    def test_negative_max(self):
        """
        If the max is less than 0, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(min_complete_types=-1)

    def test_non_positive_max(self):
        """
        If the maximum struct length is less than 1, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(min_struct_len=0)

    def test_conflicting_min_max_struct_len(self):
        """
        If the minimum complete types is greater than the maximum, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(min_struct_len=3, max_struct_len=2)

    def test_max_type_codes(self):
        """
        If the maximum type codes is less than 1, must fail.
        """
        with self.assertRaises(errors.InvalidArgument):
            dbus_signatures(max_codes=0)
