def enum_to_choices(enum_class):
    '''Given an `enum.Enum` class produce a Django-style
    choices list of 2-tuples'''
    return [
        (x, x.name.lower().replace('_', ' '))
        for x in enum_class
    ]
