import math
from mKAL_inputs import *


# machined plate thicknesses
range1 = range(17, 100, 5)
range2 = range(107, 120, 10)
range3 = range(125, 300, 5)
plate_950_1 = tuple(chain(range1, range2, range3))
# print(plate_950_1)

range1 = range(19, 98, 5)
range2 = range(104, 118, 10)
range3 = range(120, 300, 10)
plate_950_2 = tuple(chain(range1, range2, range3))
# print(plate_950_2)

range1 = range(16, 100, 5)
range2 = range(106, 120, 10)
range3 = range(125, 300, 5)
plate_1500_1 = tuple(chain(range1, range2, range3))
# print(plate_1500_1)

range1 = range(22, 98, 5)
range2 = range(102, 118, 10)
range3 = range(120, 300, 10)
plate_1500_2 = tuple(chain(range1, range2, range3))
# print(plate_1500_2)


def mach_depth(diag,thk):
    if diag < 950 and thk <=120:
        mach_dep = 3
    else:
        if diag < 1500 and thk <= 120:
            mach_dep = 4
        else: mach_dep = 5
    return mach_dep

def mach_add(type,diag,thk):
    sides = mach_sides(type)
    tot_add = mach_depth(diag,thk)*sides
    final_thk = tot_add + thk
    while final_thk % 5 != 0:
        final_thk += 1
    if final_thk > 100:
        while final_thk % 10 != 0:
            final_thk += 1
    return (final_thk-tot_add,final_thk,sides)

def mach_reverse(sides,diag,thk):
    tot_add = mach_depth(diag,thk)*sides
    final_thk = tot_add + thk
    while final_thk % 5 != 0:
        final_thk += 1
    if final_thk > 100:
        while final_thk % 10 != 0:
            final_thk += 1
    return final_thk

def mach_sides(type):
    sides = 0

    if pot_side_surf_conc:
        pot_ap_mach_sides = 1
    else: pot_ap_mach_sides = 2

    if piston_side_surf_conc and sp_ap_qty < 1:
        sp_mach_sides = 1
    else: sp_mach_sides = 2

    if piston_side_surf_conc and sp_ap_qty == 1:
        sp_mach_sides = 2
        piston_ap_mach_sides = 1

    if not piston_side_surf_conc and sp_ap_qty == 1:
        sp_mach_sides = 2
        piston_ap_mach_sides = 2

    if type == "sp":
        sides = sp_mach_sides
    if type == "pot_ap":
        sides = pot_ap_mach_sides
    if type == "piston_ap":
        sides = piston_ap_mach_sides

    return sides