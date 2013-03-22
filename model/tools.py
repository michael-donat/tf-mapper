
def enumrange(elements):
    last = 1
    for i in range(elements):
        yield last
        last <<= 1


def enum(*sequential, **named):
    enums = dict(zip(sequential, enumrange(len(sequential))), **named)
    return type('Enum', (), enums)


