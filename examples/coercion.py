from easycommandline import program

def collect(value, previous_value):
    previous_value.append(value)
    return previous_value

def make_range(value):
    components = value.split('..')
    return range( int(components[0]), int(components[1]) )

def sum(value, previous_value):
    return previous_value + int(value)

program.version('1.0.1')
program.options(
    ('-r', '--recursive'),
    ('-p', '--preload', 'preload enabled'),
    ('-n', '--name', 'username'),
    ('-i', '--integer <int>', 'an integer argument', int),
    ('-f', '--float <float>', 'a float argument', float),
    ('-a', '--anotherfloat', 'another float argument', float),
    ('-c', '--collection [example]', 'collection', collect, []),
    ('-x', '--range A..B', 'range', make_range),
    ('-s', '--sum', 'the sum of numbers', sum, 0),
    )
program.parse_argv()

print('recursive  : ', program.recursive)
print('preload    : ', program.preload)
print('name       : ', program.name)
print('integer    : ', program.integer)
print('float      : ', program.float)
print('collection : ', program.collection)
print('range      : ', program.range)
print('sum        : ', program.sum)
