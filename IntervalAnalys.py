import copy
from math import inf

#Graph is stored in massive
vertices = list()
blk_beg = dict()
class Segment:
    #
    # +, -, * Segment
    # >>= cut left border
    # <<= cut right border
    # left: int
    # right: int
    def __init__(self, left = None, right = None):
        self.left = left
        self.right = right

    def __iadd__(self, other): #intersection
        # print('conc')
        # print(self)
        # print(other)
        if self.left and other.left:
            self.left = min(self.left, other.left)
            self.right = max(self.right, other.right)
        elif other.left:
            self.left = other.left
            self.right = other.right
        return self

    def __add__(self, other):
        if self.left and other.left:
            return Segment(self.left + other.left, self.right + other.right)
        return Segment(None, None)

    def __sub__(self, other):
        if self.left and other.left:
            return Segment(self.left - other.right, self.right - other.left)
        return Segment(None, None)

    def __mul__(self, other):
        comb = [self.left, self.right, other.left, other.right]
        ans = []
        for i in range(2):
            for j in range(2, 4):
                if comb[i] and comb[j]:
                    ans.append(comb[i] * comb[j])
                else:
                    return Segment(None, None)
        return Segment(min(ans), max(ans))

    def __lshift__(self, other: int):  # cut interval from right side
        if not self.right:
            return Segment(None, None)
        tmp = min(other, self.right)
        if tmp < self.left:
            return Segment(None, None)
        return Segment(self.left, tmp)

    def __rshift__(self, other: int):  # cut interval from left side
        if not self.left:
            return Segment(None, None)
        tmp = max(other, self.left)
        if tmp > self.right:
            return Segment(None, None)
        return Segment(tmp, self.right)

    def __str__(self):
        return f"[{self.left}, {self.right}]"

class Command:
    # IN: dict {key: str, value: Segment}
    # OUT: dict {key: str, value: Segment}
    # next_com: list(edges{child:int, com:str, border:int)
    # com: list(com, op1, ?op2, dest)
    def __init__(self, command: list, blk_num: int):
        self.blk_num = blk_num
        self.com = command
        self.IN = dict()
        self.OUT = dict()

    def __eq__(self, other):
        return self.com == other.com and self.IN == other.IN and self.OUT == other.OUT

    def execute(self):
        if self.com[0] == 'add':
            self.OUT = f_add(self.com[1], self.com[2], self.com[3], self.IN)
        elif self.com[0] == 'sub':
            self.OUT = f_sub(self.com[1], self.com[2], self.com[3], self.IN)
        elif self.com[0] == 'mul':
            self.OUT = f_mul(self.com[1], self.com[2], self.com[3], self.IN)
        elif self.com[0] == 'str':
            self.OUT = f_str(self.com[1], self.com[2], self.IN)
        elif self.com[0] == 'jl':
            for chl in vertices[self.blk_num].children:
                u = blk_beg[chl[0]]
                merge(vertices[u].commands[0].IN, f_jl(self.blk_num, chl[1]))
        elif self.com[0] == 'jg':
            for chl in vertices[self.blk_num].children:
                u = blk_beg[chl[0]]
                merge(vertices[u].commands[0].IN, f_jg(self.blk_num, chl[1]))
        elif self.com[0] == 'jle':
            for chl in vertices[self.blk_num].children:
                u = blk_beg[chl[0]]
                merge(vertices[u].commands[0].IN, f_jle(self.blk_num, chl[1]))
        elif self.com[0] == 'jge':
            for chl in vertices[self.blk_num].children:
                u = blk_beg[chl[0]]
                merge(vertices[u].commands[0].IN, f_jge(self.blk_num, chl[1]))
        elif self.com[0] == 'nop':
            self.OUT = self.IN
        if vertices[self.blk_num].commands[-1] == self:
            for chl in vertices[self.blk_num].children:
                if not chl[1]:
                    print(vertices[blk_beg[chl[0]]].commands[0].com)
                    print(self.com)
                    merge(vertices[blk_beg[chl[0]]].commands[0].IN, self.OUT)


class BaseBlock:
    def __init__(self):
        self.children = list()
        self.commands = list()


def f_add(op1, op2, dest, table):
    num1 = Segment(int(op1), int(op1)) if (op1[0] in '0123456789') or (op1[0] == '-' and op1[1] in '0123456789') else table[op1]
    num2 = Segment(int(op2), int(op2)) if (op2[0] in '0123456789') or (op2[0] == '-' and op2[1] in '0123456789') else table[op2]
    tmp = copy.copy(table)
    tmp[dest] = num1 + num2
    return tmp


def f_sub(op1, op2, dest, table):
    num1 = Segment(int(op1), int(op1)) if (op1[0] in '0123456789') or (op1[0] == '-' and op1[1] in '0123456789') else table[op1]
    num2 = Segment(int(op2), int(op2)) if (op2[0] in '0123456789') or (op2[0] == '-' and op2[1] in '0123456789') else table[op2]
    tmp = copy.copy(table)
    tmp[dest] = num1 - num2
    return tmp


def f_mul(op1, op2, dest, table):
    num1 = Segment(int(op1), int(op1)) if (op1[0] in '0123456789') or (op1[0] == '-' and op1[1] in '0123456789') else table[op1]
    num2 = Segment(int(op2), int(op2)) if (op2[0] in '0123456789') or (op2[0] == '-' and op2[1] in '0123456789') else table[op2]
    tmp = copy.copy(table)
    tmp[dest] = num1 * num2
    return tmp


def f_str(op, dest, table):
    tmp = copy.copy(table)
    tmp[dest] = copy.copy(tmp[op])
    return tmp


def f_jl(ver: int, edge: str):
    if edge == 'jnl':
        return f_jge(ver, 'jge')
    last_com = vertices[ver].commands[-1]
    table = last_com.OUT
    op1 = last_com.com[1]
    op2 = last_com.com[2]
    tmp = copy.copy(last_com.IN)
    if op1 in list(tmp.keys()) and isinstance(tmp[op1], Segment):
        tmp[op1] = tmp[op1] << (int(op2) - 1)
    elif op2 in list(tmp.keys()) and isinstance(tmp[op2], Segment):
        tmp[op2] = tmp[op2] >> (int(op1) + 1)
    return tmp


def f_jle(ver: int, edge: str):
    if edge == 'jnle':
        return f_jg(ver, 'jg')
    last_com = vertices[ver].commands[-1]
    table = last_com.OUT
    op1 = last_com.com[1]
    op2 = last_com.com[2]
    tmp = copy.copy(last_com.IN)
    if op1 in list(tmp.keys()) and isinstance(tmp[op1], Segment):
        tmp[op1] = tmp[op1] << (int(op2))
    elif op2 in list(tmp.keys()) and isinstance(tmp[op2], Segment):
        tmp[op2] = tmp[op2] >> (int(op1))
    return tmp


def f_jg(ver: int, edge: str):
    if edge == 'jng':
        return f_jle(ver, 'jle')
    last_com = vertices[ver].commands[-1]
    table = last_com.OUT
    op1 = last_com.com[1]
    op2 = last_com.com[2]
    tmp = copy.copy(last_com.IN)
    if op1 in list(tmp.keys()) and isinstance(tmp[op1], Segment):
        tmp[op1] = tmp[op1] >> (int(op2) + 1)
    elif op2 in list(tmp.keys()) and isinstance(tmp[op2], Segment):
        tmp[op2] = tmp[op2] << (int(op1) - 1)
    return tmp


def f_jge(ver: int, edge: str):
    if edge == 'jnge':
        return f_jl(ver, 'jl')
    last_com = vertices[ver].commands[-1]
    table = last_com.OUT
    op1 = last_com.com[1]
    op2 = last_com.com[2]
    tmp = copy.copy(last_com.IN)
    if op1 in list(tmp.keys()) and isinstance(tmp[op1], Segment):
        tmp[op1] = tmp[op1] >> (int(op2))
    elif op2 in list(tmp.keys()) and isinstance(tmp[op2], Segment):
        tmp[op2] = tmp[op2] << (int(op1))
    return tmp


def top_sort(v: int, vertices: list, blk_beg: dict, visited: list, order: list):
    visited[v] = True
    for chl in vertices[v].children:
        u = blk_beg[chl[0]]
        if not visited[u]:
            top_sort(u, vertices, blk_beg, visited, order)
    order.append(v)


def merge(dest : dict, new_data: dict):
    for key in list(new_data.keys()):
        if key not in list(dest.keys()):
            dest[key] = new_data[key]
        else:
            dest[key] += new_data[key]


def calculating(v: int):
    for i in range(len(vertices[v].commands)):
        if i != 0:
            vertices[v].commands[i].IN = vertices[v].commands[i - 1].OUT
        vertices[v].commands[i].execute()


if __name__ == "__main__":
    lst = list(map(lambda x: x.rstrip('\n').split(), open("testcase.reil").readlines()))
    cur_beg_in = 0
    pre_beg_in = -1
    for i in range(len(lst)):
        if i in list(blk_beg.keys()):
            pre_beg_in = cur_beg_in
            cur_beg_in = i
        command = lst[i]
        if command[0][0] == '#':
            continue
        elif len(vertices) == 0:
            blk_beg[i] = 0
            vertices.append(BaseBlock())
        if command[0][0] == 'j':
            if i < len(lst) and i + 1 not in list(blk_beg.keys()):
                blk_beg[i + 1] = len(vertices)
                vertices.append(BaseBlock())
            if int(command[3]) - 1 not in list(blk_beg.keys()):
                blk_beg[int(command[3]) - 1] = len(vertices)
                vertices.append(BaseBlock())
            vertices[blk_beg[cur_beg_in]].children.append([i + 1, 'jn' + command[0][1:], inf])
            vertices[blk_beg[cur_beg_in]].children.append([int(command[3]) - 1, command[0], int(command[2])])
        if pre_beg_in != -1 and vertices[blk_beg[pre_beg_in]].commands[-1].com[0][0] != 'j':
            vertices[blk_beg[pre_beg_in]].children.append([cur_beg_in, '', inf])
        vertices[blk_beg[cur_beg_in]].commands.append(Command(command, blk_beg[cur_beg_in]))
    print('blk_beg - info about beginning of every block:\n', blk_beg, sep='')
    print('Graph structure:')
    for i in range(len(vertices)):
        v = vertices[i]
        print(f'BaseBlock number {i}:')
        print('Commands:')
        for com in v.commands:
            print(com.com)
        print('Edges:\n', v.children, sep='')
    #preparation for top_sort
    order = list()
    visited = [False] * len(vertices)
    top_sort(0, vertices, blk_beg, visited, order)
    order.reverse()
    print('Sequence of topological sorted vertices:\n', order, sep='')
    left_x, right_x = list(map(lambda x: int(x),
                               input('Input limitations for x in format: min_value max_value\n').split()))
    left_y, right_y = list(map(lambda x: int(x),
                               input('Input limitations for y in format: min_value max_value\n').split()))
    vertices[order[0]].commands[0].IN = {"arg0": Segment(left_x, right_x),
                                         "arg1": Segment(left_y, right_y)}
    for v in order:
        calculating(v)
    for v in order:
        for command in vertices[v].commands:
            print(command.com)
            print("IN:")
            for key in command.IN.keys():
                print(key, command.IN[key], sep=': ')
            print("OUT:")
            for key in command.OUT.keys():
                print(key, command.OUT[key], sep=': ')
    print('Limitations for return value:', vertices[order[-1]].commands[-1].OUT['ret'])