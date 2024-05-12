#!/usr/bin/env python3

import argparse
import itertools
import os
import re
import sys

def main():
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--field', '--field-pattern', type=str)
    group.add_argument('-s', '--separator', '--separator-pattern', type=str)
    group.add_argument('-w', '--width', '--fixed-width', type=str)

    parser.add_argument('-I', '--id', type=int, default=0)
    parser.add_argument('-p', '--parent', type=int, default=1)
    parser.add_argument('--indent', '--indent-marker', type=str, default='  |')
    parser.add_argument('--item', '--item-marker', type=str, default='__ ')
    parser.add_argument('--last-item', '--last-item-marker', type=str, default=r'\_ ')
    parser.add_argument('--os', '--output-separator', type=str, default=' ')

    output_width = 120

    try:
        tsize = os.get_terminal_size()
    except:
        tsize = None

    if tsize != None:
        output_width = tsize.columns

    parser.add_argument('-o', '--output-width', type=int, default=output_width)

    args = parser.parse_args()

    if args.id == args.parent:
        print('ID and parent ID index cannot be the same!', file=sys.stderr)
        exit(1)

    if args.field:
        field_extractor = FieldFinder(args.field)
    elif args.separator:
        field_extractor = FieldSplitter(args.separator)
    elif args.width:
        field_extractor = FieldExtractor(parse_int_list(args.width))
    else:
        field_extractor = FieldSplitter(r'\s+')

    nodes = {}

    for line in sys.stdin:
        line = line.strip()
        node = Node(line, field_extractor.get_fields(line))
        nodes[node.fields[args.id]] = node

    for node in nodes.values():
        if node.fields[args.parent] in nodes:
            node.parent = nodes[node.fields[args.parent]]

    roots = [ node for node in nodes.values() if node.parent == None ]

    for node in nodes.values():
        if node.parent:
            node.parent.subnodes.append(node)

    for node in roots:
        assertIsTree(node)

    def get_id(node):
        return node.fields[args.id]

    roots.sort(key=get_id)

    for node in nodes.values():
        node.subnodes.sort(key=get_id)

    for node in roots:
        print(formatNode(
            node,
            args.output_width,
            field_separator=args.os,
            exclude=[args.id, args.parent],
            indent_marker=args.indent,
            item_marker=args.item,
            last_item_marker=args.last_item))

def formatNode(
        node,
        output_width,
        field_separator=' ',
        exclude=[],
        indent_marker='  |',
        item_marker='__ ',
        last_item_marker='\\_'):
    class PrintState:
        def __init__(self, node):
            self.node = node
            self.at = 0
            self.printed = False

    print_states = [ PrintState(node) ]
    at = 0

    last_indent_marker = ' ' * len(indent_marker)
    lines = []

    while len(print_states) > 0:
        state = print_states[at]

        if not state.printed:
            tokens = []

            for prev_state in print_states[:-1]:
                if prev_state.at < len(prev_state.node.subnodes):
                    tokens.append(indent_marker)
                else:
                    tokens.append(last_indent_marker)

            if at > 0:
                prev_state = print_states[at - 1]

                if prev_state.at < len(prev_state.node.subnodes):
                    tokens.append(item_marker)
                else:
                    tokens.append(last_item_marker)

            data_tokens = []

            for i in range(len(state.node.fields)):
                if i not in exclude:
                    data_tokens.append(state.node.fields[i])

            tokens.append(field_separator.join(data_tokens))
            lines.append(''.join(tokens)[0:output_width])
            state.printed = True

        if state.at < len(state.node.subnodes):
            node = state.node
            print_states.append(PrintState(node.subnodes[state.at]))
            state.at += 1
            at += 1
        else:
            print_states.pop()
            at -= 1
            state.at += 1

    return '\n'.join(lines)

class FieldFinder:
    def __init__(self, field_pattern):
        self.field_matcher = re.compile(field_pattern)

    def get_fields(self, line):
        return self.field_matcher.findall(line)

class FieldSplitter:
    def __init__(self, split_pattern):
        self.split_matcher = re.compile(split_pattern)

    def get_fields(self, line):
        return self.split_matcher.split(line)

class FieldExtractor:
    def __init__(self, widths):
        self.widths = widths

    def get_fields(self, line):
        ret = []
        at = 0

        for width in self.widths:
            ret.append(line[at:at+width - 1])
            at += width

        return ret

class Node:
    def __init__(self, full_line, fields):
        self.full_line = full_line
        self.fields = fields
        self.subnodes = []
        self.parent = None
        self.visited = False

INT_LIST_SEPARATOR = re.compile(r'\s*,\s*')

def parse_int_list(line):
    return [ int(part) for part in INT_LIST_SEPARATOR.split(line) ]

def assertIsTree(node):
    if node.visited:
        raise 'Graph contains cycles!'

    for subnode in node.subnodes:
        assertIsTree(subnode)

if __name__ == "__main__":
    main()
