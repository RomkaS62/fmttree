# fmttree

A dumb as bricks program that turns lists of parent-child relationships into
trees.

## Example

This:

    1 0 Data1
    2 1 Data2
    3 1 Data3
    4 2 Data4
    5 2 Data5
    6 3 Data6
    7 3 Data7

Becomes this:

    Data1
      |__ Data2
      |  |__ Data4
      |   \_ Data5
       \_ Data3
         |__ Data6
          \_ Data7
