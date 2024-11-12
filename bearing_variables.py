import numpy as np
import math

#Inputs -----------------------

ULS_max_vert = 20000000 #N
long_mov = 200
tran_mov = 50
HP_pad = True
HP_sliding = True
site_temp_min = -5
site_temp_max = 50
ULS_rotation_x = 0.001 #rad
ULS_rotation_y = 0.02 #rad

dust_seal_h = 10
steel_type = 355

pad_manufacturer = "Ars"

max_press_lower_struct = 50
max_press_upper_struct = 50

upper_ap = False
lower_ap = False

#Inputs -----------------------

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

#Derived Variables -----------------------


#Static assumptions -----------------------

min_contact_h_pot_piston = 5
steel_material_safety_factor = 1.3
steel_steel_fric = 0.6

designs_above_min = 7
# rs_recess = 5.6
piston_min = 25
steel_density = .00785 #g/mm3
steel_density = steel_density/1000 #convert to kg/mm3
extra_mov_for_ss = 50
min_spacing_ss_to_sp = 20
pad_disc_diff_floor = 10
pad_disc_diff_ceil = 70

lug_edge_factor = 1.2
bolt_sep_parallel_to_force_factor = 2.2
bolt_sep_perp_to_force_factor = 2.4

#Static assumptions -----------------------

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
lug_l_col = 14
lug_w_col = 15
lug_t_col = 16
bearing_kg_col = 17
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

pot_wall = tuple(range(20,200,5))
pot_bot = tuple(range(12,50,1))
bolt_qual = (8.8,10.9)
bolt_size = (12,16,20,24,30,36)

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
    ("EN", 20, 8.8,12),
    ("EN", 20, 10.9,12),
    ("EN", 24, 8.8,12),
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