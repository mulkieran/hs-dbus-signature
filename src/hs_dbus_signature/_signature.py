# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
"""
A strategy for generating dbus signatures.
"""

# isort: THIRDPARTY
from hypothesis.errors import InvalidArgument
from hypothesis.strategies import lists, recursive, sampled_from, tuples

_CODES = ("b", "d", "g", "h", "i", "n", "o", "q", "s", "t", "u", "v", "x", "y")


def dbus_signatures(
    *,
    max_codes=5,
    min_complete_types=0,
    max_complete_types=5,
    min_struct_len=1,
    max_struct_len=5,
    exclude_arrays=False,
    exclude_dicts=False,
    exclude_structs=False,
    blacklist=None
):
    """
    Return a strategy for generating dbus signatures.

    :param int max_codes: the maximum number of type codes in a complete type
    :param int min_complete_types: the minimum number of complete types
    :param int max_complete_types: the maximum number of complete types
    :param int min_struct_len: the minimum number of complete types in a struct
    :param int max_struct_len: the maximum number of complete types in a struct
    :param bool exclude_arrays: whether to exclude arrays
    :param bool exclude_dicts: whether to exclude dicts
    :param bool exclude_structs: whether to exclude structs
    :param str blacklist: blacklisted symbols, default is None

    :rtype: strategy
    :raises InvalidArgument: if blacklist contains every type code

    If included in blacklist, a symbol will not appear in a dbus signature.

    For technical reasons, the max_codes limit does not apply to the first type
    of a dict entry. Thus, the actual number of type codes in a resulting
    signature may exceed max_codes by the number of dict entry types in that
    signature.

    The default for all max_* values is 5. max_complete_types and
    max_struct_len may be set to None, in which case the size of the generated
    signatures will be unbounded. This is not really recommended.

    The default for all min_* values is set to their lowest allowed value.
    Structs may not be empty, so min_struct_len is 1. However, the empty
    string is a valid signature, so min_complete_types is 0.
    """

    if max_codes < 1:
        raise InvalidArgument("can not have signature with 0 type codes")

    if min_complete_types < 0:
        raise InvalidArgument("can not have signature of negative length")

    if min_struct_len < 1:
        raise InvalidArgument("can not have struct of zero length")

    if max_complete_types is not None and min_complete_types > max_complete_types:
        raise InvalidArgument("minimum complete types specified greater than maximum")

    if max_struct_len is not None and max_struct_len < min_struct_len:
        raise InvalidArgument("minimum struct length specified is greater than maximum")

    if blacklist is None:
        codes = list(_CODES)
    else:
        codes = list(frozenset(_CODES).difference(frozenset(blacklist)))
        if codes == []:
            raise InvalidArgument("all type codes blacklisted, no signature possible")

    # The keys in a dict are not permitted to be variants, so if the only code
    # allowed is 'v', exclude dicts.
    if codes == ["v"]:
        exclude_dicts = True

    def extend(strat):
        if not exclude_arrays:
            strat |= strat.map(lambda v: "a" + v)
        if not exclude_structs:
            strat |= lists(strat, min_size=min_struct_len, max_size=max_struct_len).map(
                lambda v: "(" + "".join(v) + ")"
            )
        if not exclude_dicts:
            strat |= tuples(sampled_from([c for c in codes if c != "v"]), strat).map(
                lambda kv: "a{%s%s}" % kv
            )
        return strat

    return lists(
        recursive(sampled_from(codes), extend, max_leaves=max_codes),
        min_size=min_complete_types,
        max_size=max_complete_types,
    ).map("".join)
