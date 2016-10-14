# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

"""
A strategy for generating dbus signatures.
"""

from hypothesis.errors import InvalidArgument

from hypothesis.strategies import builds
from hypothesis.strategies import just
from hypothesis.strategies import lists
from hypothesis.strategies import recursive
from hypothesis.strategies import sampled_from


class _DBusSignatureStrategy(object):
    """
    Initializes a d-bus signature generating strategy, modified according to
    the parameters.
    """
    # pylint: disable=too-few-public-methods

    CODES = \
       ['b', 'd', 'g', 'h', 'i', 'n', 'o', 'q', 's', 't', 'u', 'v', 'x', 'y']

    def __init__(
       self,
       *,
       max_codes=5,
       min_complete_types=0,
       max_complete_types=5,
       min_struct_len=1,
       max_struct_len=5,
       blacklist=None
    ):
        # pylint: disable=too-many-arguments

        """
        Initializer.

        :param int max_codes: the maximum number of codes in a complete type
        :param int min_complete_types: the minimum number of complete types
        :param int max_complete_types: the maximum number of complete types
        :param int max_struct_len: the number of complete types in a struct
        :param str blacklist: blacklisted constructors

        If blacklist contains all type codes, then it is impossible to
        generate any elements from the strategy.
        """

        def _array_fun(children):
            return children.flatmap(lambda v: just('a' + v))

        def _struct_fun(children):
            return builds(
                ''.join,
                lists(
                   elements=children,
                   min_size=min_struct_len,
                   max_size=max_struct_len
                )
            ).flatmap(lambda v: just('(' + v + ')'))

        if blacklist is None:
            codes = self.CODES[:]
            array_fun = _array_fun
            struct_fun = _struct_fun

        else:
            codes = [x for x in self.CODES if x not in frozenset(blacklist)]
            array_fun = (lambda x: x) if 'a' in blacklist else _array_fun
            struct_fun = (lambda x: x) if '(' in blacklist else _struct_fun

        self._CODE_STRATEGY = sampled_from(codes)

        if blacklist is not None and ('{' in blacklist or 'a' in blacklist):
            dict_fun = lambda children: children
        else:
            def dict_fun(children):
                """
                Builds the signature for an array of dict entries.
                """
                return builds(
                   lambda x, y: x + y,
                   self._CODE_STRATEGY.filter(lambda x: x != 'v'),
                   children
                ).flatmap(lambda v: just('a' + '{' + v + '}'))

        self._COMPLETE_STRATEGY = recursive(
           self._CODE_STRATEGY,
           lambda children: \
              struct_fun(children) | array_fun(children) | dict_fun(children),
           max_leaves=max_codes
        )

        self.SIGNATURE_STRATEGY = builds(
           ''.join,
           lists(
              self._COMPLETE_STRATEGY,
              min_size=min_complete_types,
              max_size=max_complete_types
           )
        )


def dbus_signatures(
   *,
   max_codes=5,
   min_complete_types=0,
   max_complete_types=5,
   min_struct_len=1,
   max_struct_len=5,
   blacklist=None
):
    """
    Return a strategy for generating dbus signatures.

    :param int max_codes: the maximum number of type codes in a complete type
    :param int min_complete_types: the minimum number of complete types
    :param int max_complete_types: the maximum number of complete types
    :param int min_struct_len: the minimum number of complete types in a struct
    :param int max_struct_len: the maximum number of complete types in a struct
    :param str blacklist: blacklisted symbols, default is None

    :rtype: strategy
    :raises InvalidArgument: if blacklist contains every type code

    If included in blacklist, a symbol will not appear in a dbus signature.
    Symbols are not restricted to type codes, but may include identifiers for
    complex types, like 'a'. Including the character '(' in the string of
    blacklisted symbols will prevent the inclusion of struct signatures in
    a dbus signature; the inclusion of '{' will do the same for dict entries.

    For technical reason, the max_codes limit does not apply to the first type
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
    if blacklist is not None and \
       (frozenset(blacklist) >= frozenset(_DBusSignatureStrategy.CODES)):
        raise InvalidArgument(
           "all type codes blacklisted, no signature possible"
        )

    if max_codes < 1:
        raise InvalidArgument("can not have signature with 0 type codes")

    if min_complete_types < 0:
        raise InvalidArgument("can not have signature of negative length")

    if min_struct_len < 1:
        raise InvalidArgument("can not have struct of zero length")

    if max_complete_types is not None and \
       min_complete_types > max_complete_types:
        raise InvalidArgument(
           "minimum complete types specified greater than maximum"
        )

    if max_struct_len is not None and max_struct_len < min_struct_len:
        raise InvalidArgument(
           "minimum struct length specified is greater than maximum"
        )

    return _DBusSignatureStrategy(
       max_codes=max_codes,
       min_complete_types=min_complete_types,
       max_complete_types=max_complete_types,
       min_struct_len=min_struct_len,
       max_struct_len=max_struct_len,
       blacklist=blacklist
    ).SIGNATURE_STRATEGY
