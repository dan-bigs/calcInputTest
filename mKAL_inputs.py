import numpy as np
import math
from itertools import chain

# import subprocess

# # Run file1.py as a separate process
# subprocess.run(["python", "mKAL_array_maker.py"])


#Variable USER Inputs -----------------------

ULS_max_vert_entry = 20000 #kN

ULS_max_vert = ULS_max_vert_entry*1000 #N
SLS_max_vert = ULS_max_vert/1.5
Perm_load = ULS_max_vert/3
long_mov_tot = 200
tran_mov_tot = 50
HP_pad = True
HP_sliding = True
site_temp_min = -25
site_temp_max = 50
ULS_rotation_x = 0.001 #rad
ULS_rotation_y = 0.015 #rad

h_load_test = ULS_max_vert*0.25

dust_seal_h = 10
steel_type = 355

pad_manufacturer = "Ars"

max_press_lower_contact = 55
max_press_upper_contact = 50

pot_side_surf_conc = True
piston_side_surf_conc = True

sp_ap_qty = 1
pot_ap_qty = 1

bolt_qty_max = 20

conc_cyl = 40

sliding_protru = 2.5

#Variable USER Inputs -----------------------





#Derived Variables -----------------------

if HP_pad: pad_type = "HP"

ULS_rotation_tot = math.sqrt(ULS_rotation_x**2+ULS_rotation_y**2)
ULS_rotation_x_perm = ULS_rotation_x/2
ULS_rotation_y_perm = ULS_rotation_y/2
ULS_rotation_x_var = ULS_rotation_x/2
ULS_rotation_y_var = ULS_rotation_y/2

if HP_sliding:
    sliding_mat_thk = 8
    sliding_mat_recess = 5.6
rs_safety_fact = 1.4
if HP_pad: char_press_pad = 120 #MPa
else: char_press_pad = 60 #MPa
allow_press_pad = char_press_pad/1.3 #Mpa

max_vert = np.max(ULS_max_vert)

Econc = (22*(conc_cyl/10)**0.3)

def bolt_sz_min(row):
    pad_dia = row[pad_dia_col]
    critical_point = pad_dia/35
    bolt_sz_min = [num for num in bolt_size if num >= critical_point]
    # Return the minimum of the filtered values if any, otherwise return None
    return min(bolt_sz_min, default=None)

def bolt_sz_max(row):
    pad_dia = row[pad_dia_col]
    critical_point = pad_dia/7
    bolt_sz_max = [num for num in bolt_size if num <= critical_point]
    # print (bolt_sz_max)
    return max(bolt_sz_max, default=None)

#Derived Variables -----------------------


#Static assumptions -----------------------

min_contact_h_pot_piston = 5
steel_material_safety_factor = 1.3
steel_steel_fric = 0.6

# pot_lug_qty = 2
# sp_lug_qty = 2

designs_above_min = 7
# rs_recess = 5.6
piston_min = 25
steel_density = .00785 #g/mm3
steel_density = steel_density/1000 #convert to kg/mm3
extra_mov_for_ss = 50
min_spacing_ss_to_sp = 20

pad_disc_diff_ceil = 30
pot_bot_to_wall = 0.6

ap_perimeter = 10

lug_edge_factor = 1.5
bolt_sep_parallel_to_force_factor = 2.2
bolt_sep_perp_to_force_factor = 2.4
lug_pot_ratio = 0.8

pot_wall_min = 20
pot_wall_max = 20 + min(300,(ULS_max_vert+h_load_test)/100000)
print(pot_wall_max,"pot wall max")
pot_wall_step = 5


# pot_wall = tuple(range(20,150,5))
pot_bot_min = int(12 + (ULS_max_vert+h_load_test)/2000000)
pot_bot_max = int(min(pot_wall_max*0.75,16 + (ULS_max_vert+h_load_test)/200000))
pot_bot = tuple(range(pot_bot_min,pot_bot_max,2))
print(pot_bot)


# bolt_qual = (8.8,)
bolt_size = (12,16,20,24,30,36)


sp_tmax = 150

# Example points
load_range = [0, 20000000]
# h_load_mod = h_load_test/ULS_max_vert
# h_load_mod = 0
low_bound = [0.0, 0.0]

# Interpolate
x = ULS_max_vert
proof_low_bound_pot_bot = np.interp(x, load_range, low_bound)
proof_low_bound_pot_wall = proof_low_bound_pot_bot
print(f"Interpolated value at x={x} is y={proof_low_bound_pot_bot}")


#Static assumptions -----------------------


#Pricing assumptions -----------------------

Steel_EUR_per_kg = 1.5
Weld_mat__EUR_per_kg = 1

bolt_EUR_per = [
    (12,8.8,1),
    (12,10.9,1),
    (16,8.8,1),
    (16,10.9,1),
    (20,8.8,1),
    (20,10.9,1),
    (24,8.8,1),
    (24,10.9,1),
    (30,8.8,1),
    (30,10.9,1),
    (36,8.8,1),
    (36,10.9,1),
]

RS75_EUR_per_kg = 1.6
mach_EUR_per_kg = 2.5

#Pricing assumptions -----------------------


#component positions in the final matrix -----------------------
pad_dia_col = 0 
pad_thk_col = 1 
main_sliding_dia_col = 2 
stainless_long_col = 3 
stainless_tran_col = 4 
sliding_long_col = 5 
sliding_tran_col = 6
sliding_thk_col = 7
pot_wall_thk_col = 8 
pot_bot_thk_col = 9 
piston_thk_col = 10
bolt_sz_col = 11
bolt_qual_col = 12
bolt_qty_col = 13
pot_lug_qty_col = 14
pot_lug_l_col = 15
pot_lug_w_col = 16
pot_lug_t_col = 17
sp_lug_qty_col = 18
sp_lug_l_col = 19
sp_lug_w_col = 20
sp_lug_t_col = 21
pot_ap_long_col = 22
pot_ap_tran_col = 23
pot_ap_t_col = 24
sp_ap_long_col = 25
sp_ap_tran_col = 26
sp_ap_t_col = 27
bearing_kg_col = 28
#component positions in the final matrix -----------------------

steel_yield_tuple = (
    (40, 235, 355),  # thickness, S235, S355J2+N
    (80, 215, 335),
    (100, 215, 315),
    (150, 295, 295),
    (200, 185, 285),
    (250, 175, 275),
    (400, 0, 265)
)

rs_char_str_values = (
    (35, 180, 180),  # degC, rs, rs75
    (48, 135, 150),
    (60, 110, 135),
    (70, 90, 120),
    (80, 70, 105),
)

sliding_disc_dia_defined_array = (
    140,170,200,235,270,300,335,365,400,435,465,500,535,570,600,635,670,705,740,775,805,840)

# Given pad data
pad_defined_tuple = (
    [1, 152, 16, 18],  # size, diameter, standard_t, HP_t
    [1.5, 183, 16, 18],
    [2, 215, 16, 18],
    [2.5, 248, 17, 18],
    [3, 282, 19, 21],
    [3.5, 314, 21, 24],
    [4, 349, 24, 27],
    [4.5, 381, 26, 29],
    [5, 416, 28, 31],
    [5.5, 449, 30, 33],
    [6, 484, 33, 37],
    [6.5, 516, 35, 39],
    [7, 551, 37, 41],
    [7.5, 584, 39, 43],
    [8, 619, 42, 47],
    [8.5, 652, 44, 49],
    [9, 687, 46, 51],
    [9.5, 719, 48, 53],
    [10, 754, 51, 57],
    [10.5, 795, 53, 59],
    [11, 822, 55, 61]
)

F_values = (
    ("Ars","HP",0.01,0.3,2.65),
    ("maI","HP",0.01,0.2,1.33),
    ("maSK","HP",0.01,0.33,2.34),
    ("Ars","standard",0.01,0.35,4.69),
    ("maI","standard",0.01,0.31,3.18),
)

# standard, diameter, material, shear plane, ultimate, lug min
lug_thk_min = [
    ("EN", 12, 8.8,10),
    ("EN", 12, 10.9,10),
    ("EN", 16, 8.8,10),
    ("EN", 16, 10.9,10),
    ("EN", 20, 8.8,15),
    ("EN", 20, 10.9,15),
    ("EN", 24, 8.8,15),
    ("EN", 24, 10.9,15),
    ("EN", 30, 8.8,15),
    ("EN", 30, 10.9,20),
    ("EN", 36, 8.8,15),
    ("EN", 36, 10.9,20),
]

bolt_shear_ULS_thread = [
    (12,8.8,32.4),
    (12,10.9,33.7),
    (16,8.8,60.3),
    (16,10.9,62.8),
    (20,8.8,94.1),
    (20,10.9,98),
    (24,8.8,135.6),
    (24,10.9,141.2),
    (30,8.8,215.4),
    (30,10.9,224.4),
    (36,8.8,313.7),
    (36,10.9,326.8),
]

def get_value(table, name, category,ref):
    for row in table:
        if row[0] == name and row[1] == category:
            return row[ref]  # You can also choose to return specific columns if needed
    return None  # Return None if no match is found

def terminal_print(combo,name):
    total_elements = sum(len(row) for row in combo)
    row_num = len(combo)
    # print("pot walls added:\n", combo2)
    
    print(f"{name} tuple Rows:", row_num)
    print(f"{name} tuple Elements:", total_elements,"\n")
    