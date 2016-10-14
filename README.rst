A Hypothesis Strategy for Generating Arbitrary DBus Signatures
==============================================================

This package contains a Hypothesis strategy for generating dbus signatures.
An informal specification of dbus signatures is available at:
https://dbus.freedesktop.org/doc/dbus-specification.html.

The strategy is intended to be both sound and complete. That is, it should
never generate an invalid dbus signature and it should be capable, modulo
size constraints, of generating any valid dbus signature.

Usage
-----

Import the function and obtain a strategy with the default parameters. ::

    >>> from hs_dbus_signature import dbus_signatures
    >>> strategy = dbus_signatures()

Obtain a few examples of valid signatures, e.g., ::

    >>> strategy.example()
    ''
    >>> strategy.example()
    'a{ng}'
    >>> strategy.example()
    'a{xas}a{gah}a{nau}'

Make use of the strategy in your tests, e.g. ::

    from hypothesis import given

    @given(dbus_signatures())
    def test(signature):
        ...

Use the parameters to omit dicts ::

    >>> strategy = dbus_signatures(blacklist="{")
    >>> strategy.example()
    '(gnggg)(n)(gn)(nnnnn)(nn)'

or to ensure that no example signature is the empty string ::

    >>> strategy = dbus_signatures(min_complete_types=1)
    >>> strategy.example()
    'a{sv}'

The strategy will raise an InvalidArgument exception immediately if it is given
arguments which allow no examples to be drawn. ::

    >>> strategy = dbus_signatures(blacklist=string.ascii_lowercase)
    Traceback (most recent call last):
    ...

Remarks
-------

Documentation for the Hypothesis testing library can be found at
http://hypothesis.readthedocs.io.

This strategy makes use of the Hypothesis higher-order strategy, recursive(),
which is discussed here: http://hypothesis.works/articles/recursive-data/.

It is only supported for Python 3 as it uses Python 3 only syntax.
