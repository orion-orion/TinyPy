def concat_comma_separated(items):
    """Convert the items in the sequence to a string, and separate them
    with commas.

    >>> concat_comma_separated([2, 'foo', True])
    '2, foo, True'
    >>> concat_comma_separated([2])
    '2'
    >>> concat_comma_separated([])
    ''
    """
    return ', '.join([str(item) for item in items])
