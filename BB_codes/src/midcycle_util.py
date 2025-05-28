from .bb_code import BBCode

import networkx as nx

def homo_func(homo: str):
    def fx(tup):
        return tup[0] % 2

    def fy(tup):
        return tup[1] % 2

    def fxy(tup):
        return (tup[0] + tup[1]) % 2

    if homo == "x":
        return fx
    elif homo == "y":
        return fy
    elif homo == "xy":
        return fxy

def stab_order(vals: list):
    # Find the unique value (0 or 1) in a_vals
    unique_val = None
    for val in [0, 1]:
        if vals.count(val) == 1:
            unique_val = val
            break
    
    # Create ordered list with unique value first
    ordered = []
    # Add the unique value first
    for i, val in enumerate(vals):
        if val == unique_val:
            ordered.append(i)
            break
    # Add the other two indices
    for i, val in enumerate(vals):
        if val != unique_val:
            ordered.append(i)

    return ordered

def gen_connection(code: BBCode, homo: str):
    """
    Generate the connection of each round.
    We assume that the code has a toric layout.
    
    Parameters:
    - code: An instance of BBCode representing the code structure.
    - homo: A string that can be 'x', 'y', or 'xy', indicating the type of homomoprhism function. 
    """

    l = code.l
    m = code.m
    a3x, a3y, b3x, b3y = code.poly_params
    a_lst = ((0,0),(1,0),(a3x,a3y))
    b_lst = ((0,0),(0,1),(b3x,b3y))

    f = homo_func(homo)

    a_vals = [f(a) for a in a_lst]
    b_vals = [f(b) for b in b_lst]

    left_stab_order = stab_order(a_vals)
    right_stab_order = stab_order(b_vals)

    # sort a_lst and b_lst based on the stab_order
    a_lst = [a_lst[i] for i in left_stab_order]
    b_lst = [b_lst[i] for i in right_stab_order]

    # Shift all the elements in a_lst by (-a_lst[0][0], -a_lst[0][1]) then mod (l,m)
    shift_x, shift_y = -a_lst[0][0], -a_lst[0][1]
    a_lst = [(((x + shift_x) % l), ((y + shift_y) % m)) for x,y in a_lst]
    
    shift_x, shift_y = -b_lst[0][0], -b_lst[0][1]
    b_lst = [(((x + shift_x) % l), ((y + shift_y) % m)) for x,y in b_lst]

    print(a_lst)
    print(b_lst)

    # generate the even and odd lattice sites
    even_sites = []
    odd_sites = []
    for i in range(l):
        for j in range(m):
            if f((i, j)) == 0:
                even_sites.append((i, j))
            else:
                odd_sites.append((i, j))
    
    # F1 round 1
    f11_lst = []
    for i,j in even_sites:
        f11_lst.append((i,j,i+b_lst[2][0],j+b_lst[2][1]))
        f11_lst.append((i+a_lst[2][0],j+a_lst[2][1],i,j))
    
    # F1 round 2
    f12_lst = []
    for i,j in even_sites:
        f12_lst.append((i,j,i+b_lst[1][0],j+b_lst[1][1]))
        f12_lst.append((i+a_lst[1][0],j+a_lst[1][1],i,j))
    
    print(f12_lst[:10])

    # F1 round 3
    f13_lst = []
    for i,j in even_sites:
        f13_lst.append((i,j,i,j))

    # F2 round 1
    f21_lst = []
    for i,j in odd_sites:
        f21_lst.append((i,j,i+b_lst[2][0],j+b_lst[2][1]))
        f21_lst.append((i+a_lst[2][0],j+a_lst[2][1],i,j))
    
    # F2 round 2
    f22_lst = []
    for i,j in odd_sites:
        f22_lst.append((i,j,i+b_lst[1][0],j+b_lst[1][1]))
        f22_lst.append((i+a_lst[1][0],j+a_lst[1][1],i,j))

    # F2 round 3
    f23_lst = []
    for i,j in odd_sites:
        f23_lst.append((i,j,i,j))

    return [f11_lst, f12_lst, f13_lst, f21_lst, f22_lst, f23_lst]

def tuple_to_edge_coordinate(tup, l, m):
    a,b,c,d = tup
    a = a % l   
    b = b % m
    c = c % l
    d = d % m

    def shift_lattice(a,b):
        nb = a % l
        na = (b-4*a) % m
        return (na,nb)

    a,b = shift_lattice(a,b)
    c,d = shift_lattice(c,d)

    return ((2*a+1,2*b), (2*c,2*d+1))

    





