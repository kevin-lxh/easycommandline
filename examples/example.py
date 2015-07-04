import sys
from easycommandline import program, arg

def collect(value, previous_value):
    previous_value.append(value)
    return previous_value

def make_range(value):
    components = value.split('..')
    return range( int(components[0]), int(components[1]) )

def sum(value, previous_value):
    return previous_value + int(value)

program.version('1.0.1')
program.options([
        ('-r', '--recursive'),
        ('-p', '--preload', 'preload enabled'),
        ('-n', '--name', 'username'),
        ('-i', '--integer <int>', 'an integer argument', int),
        ('-f', '--float <float>', 'a float argument', float),
        ('-a', '--anotherfloat', 'another float argument', float),
        ('-c', '--collection [example]', 'collection', collect, []),
        ('-x', '--range A..B', 'range', make_range),
        ('-s', '--sum', 'the sum of numbers', sum, 0),
    ])
program.parse(sys.argv)

print 'recursive  : ', arg('recursive')
print 'preload    : ', arg('preload')
print 'name       : ', arg('name')
print 'integer    : ', arg('integer')
print 'float      : ', arg('float')
print 'collection : ', arg('collection')
print 'range      : ', arg('range')
print 'sum        : ', arg('sum')
