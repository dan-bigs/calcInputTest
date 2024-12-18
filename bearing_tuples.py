import math
import numpy as np
import itertools
import pandas as pd
from bearing_statics import *
from bearing_weight import *
import time

start_time = time.time()

np.set_printoptions(threshold=np.inf) #show an infinite amount in print window


# determination of minimum values of pad and disc dia from the predefined groups ----------------------

pad_min_dia = math.sqrt((max_vert/allow_press_pad)/3.142)*2
pad_min_dia_position = next((i for i, pad in enumerate(pad_defined_tuple) if pad[1] > pad_min_dia), None)

sliding_disc_dia_defined_array = [140,170,200,235,270,300,335,365,400,435,465,500,535,570,600,635,670,705,740,775,805,840]
sliding_disc_min_dia_position = next((i for i, disc in enumerate(sliding_disc_dia_defined_array) if disc > pad_min_dia*.8), None)
sliding_disc_min_dia = sliding_disc_dia_defined_array[sliding_disc_min_dia_position]

# determination of minimum values of pad and disc dia from the predefined groups ----------------------


# define arrays for geometry

pad_dia_tuple = tuple([pad[1] for pad in pad_defined_tuple[pad_min_dia_position:pad_min_dia_position + designs_above_min]])

if HP_pad: column_ref = 3
else: column_ref = 2

pad_h_tuple = tuple([pad[column_ref] for pad in pad_defined_tuple[pad_min_dia_position:pad_min_dia_position + designs_above_min]])


# Combine pad diameter and height into a 2D array
# pad_dia_h_comb = np.column_stack((pad_dia_tuple, pad_h_tuple))
pad_dia_h_comb = tuple(zip(pad_dia_tuple, pad_h_tuple))
# terminal_print(pad_dia_h_comb,"pad_dia_h_comb")

# print(pad_restraint_moment(pad_dia_h_comb[1],"ULS")[0])

sliding_disc_dia_array = np.array([disc for disc in sliding_disc_dia_defined_array[sliding_disc_min_dia_position:sliding_disc_min_dia_position + designs_above_min]])


pad_and_disc = []

# Repeat each block with the same value from `sliding_disc_dia_array`
for value in sliding_disc_dia_array:
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((dia, height, value) for dia, height in pad_dia_h_comb)
    pad_and_disc.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
# terminal_print(pad_and_disc,"pad_and_disc")


pad_disc_dia_relation = tuple(
    pair for pair in pad_and_disc if pad_disc_diff_floor <= abs(pair[0] - pair[2]) <= pad_disc_diff_ceil
)
# terminal_print(pad_disc_dia_relation,"pad_disc_dia_relation")


sp_prop_add = tuple(
    (
        pad_dia, height, disc_dia,
        *sp_properties(disc_dia,long_mov_tot,tran_mov_tot)
    )
    for pad_dia, height, disc_dia in pad_disc_dia_relation
)
# terminal_print(sp_prop_add,"sp_prop_add")


pot_walls_added = []
# Repeat each block with the same value from `sliding_disc_dia_array
for value in pot_wall:
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, value) for row in sp_prop_add)
    pot_walls_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
# terminal_print(pot_walls_added,"pot_walls_added")s

pot_bot_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in pot_bot:
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, value) for row in pot_walls_added)
    pot_bot_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
# terminal_print(pot_bot_added,"pot_bot_added")


pot_bases_passing_disc_tension = tuple(row for row in pot_bot_added if pot_base_disc_tension(row))
# terminal_print(pot_bases_passing_disc_tension,"pot_bases_passing_disc_tension")


walls_passing_design_force = tuple(row for row in pot_bases_passing_disc_tension if design_force_pot_wall(row))
# terminal_print(walls_passing_design_force,"walls_passing_design_force")


walls_passing_shear_stress = tuple(row for row in walls_passing_design_force if h_shear_stress_wall(row))
# terminal_print(walls_passing_shear_stress,"walls_passing_shear_stress")


data_with_piston_h = tuple((*row, piston_h(row)) for row in walls_passing_shear_stress)


discs_passing_excentric_press = tuple(row for row in data_with_piston_h if sliding_disc_max_ecc_press(row))
terminal_print(discs_passing_excentric_press,"discs_passing_excentric_press")

# print(rs_plus_char_str(site_temp_max)[1],"ex press")

bolt_sizes_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in bolt_size:
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, value) for row in discs_passing_excentric_press)
    bolt_sizes_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
terminal_print(bolt_sizes_added,"bolt_sizes_added")

bolt_qual_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in bolt_qual:
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, value) for row in bolt_sizes_added)
    bolt_qual_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
terminal_print(bolt_qual_added,"bolt_qual_added")

bolt_qty_added = tuple((*row, bolt_qty(row)) for row in bolt_qual_added)
terminal_print(bolt_qty_added,"bolt_qty_added")

bolt_qty_considering_max = tuple(row for row in bolt_qty_added if row[bolt_qty_col] <= bolt_qty_max)
terminal_print(bolt_qty_considering_max,"bolt_qty_considering_max")

# pot_lug_dims_add = tuple((*row, *lug_builder(row,2)) for row in bolt_qty_considering_max)
# terminal_print(pot_lug_dims_add,"pot_lug_dims_add")



pot_lugs_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in (2,4):
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, *lug_builder(row,value)) for row in bolt_qty_considering_max)
    pot_lugs_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
terminal_print(pot_lugs_added,"pot_lugs_added")


sp_lug_dims_add = tuple((*row, *lug_builder(row,sp_lug_qty)) for row in pot_lugs_added)
terminal_print(sp_lug_dims_add,"sp_lug_dims_add")

sp_lugs_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in (2,4):
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, *lug_builder(row,value)) for row in pot_lugs_added)
    sp_lugs_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
terminal_print(sp_lugs_added,"sp_lugs_added")

# # Print each row on its own line
# for row in sp_lug_dims_add:
#     print(row)

anchor_plates_add = tuple((*row, *anchor_plate_builder(row)) for row in sp_lug_dims_add)
terminal_print(anchor_plates_add,"anchor_plates_add")

passing_lower_conc_press = tuple(row for row in anchor_plates_add if conc_press_pot(row)<max_press_lower_contact)
# terminal_print(passing_lower_conc_press,"passing_lower_conc_press")

# Calculate and stack weight into the tuple
data_with_weight = tuple((*row, weight_check(row)) for row in passing_lower_conc_press)
# for row in data_with_weight:
#     print(row)

# Sort the tuple based on the specific column (bearing_kg_col) in ascending order
sorted_data_with_weight = tuple(
    row for row in sorted(data_with_weight, key=lambda x: x[-1], reverse=False)
)


# print(design_moment(sorted_data_with_weight[0],"ULS",ULS_max),"design mom")

# print(sliding_disc_max_ecc_press(sorted_data_with_weight[0]),"ex press")

# Accessing first row in sorted data
first_row = sorted_data_with_weight[0]

# Print the first row (lightest bearing)
print("lowest weight bearing dims:", first_row)

# Access specific columns from the first row (adjust indices accordingly)
print("\n\nThe lightest bearing weighs:", first_row[-1], "kg\n")
print("The pot weighs:", pot_weight(first_row), "kg")
print("The piston weighs:", piston_weight(first_row), "kg")
print("The sliding plate weighs:", sp_weight(first_row), "kg")
print("The lugs in total weigh:", lugs_weight(first_row), "kg")
print("The anchor plate on the pot side weighs:", ap_weights(first_row)[0], "kg")
print("The anchor plate on the sliding side weighs:", ap_weights(first_row)[1], "kg\n\n")


print(conc_press_pot(sorted_data_with_weight[0]),"pot ex conc press\n")
print(design_moment(sorted_data_with_weight[0],"ULS",max_vert),"design moment\n")
print(sliding_disc_max_ecc_press_check(sorted_data_with_weight[0]),"sliding disc ex press\n")
print(rs_plus_char_str(site_temp_max)[1]/rs_safety_fact,"allowable sliding disc ecc press\n")
print(pot_base_disc_tension_check(sorted_data_with_weight[0]),"tension in pot base\n")

print("pad dia:", first_row[pad_dia_col], "mm")
print("pad thk:", first_row[pad_thk_col], "mm")
print("main sliding dia:", first_row[main_sliding_dia_col], "mm")
print("stainless long:", first_row[stainless_long_col], "mm")
print("stainless tran:", first_row[stainless_tran_col], "mm")
print("sliding long:", first_row[sliding_long_col], "mm")
print("sliding tran:", first_row[sliding_tran_col], "mm")
print("sliding thk:", first_row[sliding_thk_col], "mm")
print("pot wall thk:", first_row[pot_wall_thk_col], "mm")
print("pot bot thk:", first_row[pot_bot_thk_col], "mm")
print("pot outer dia:", first_row[pad_dia_col]+2*first_row[pot_wall_thk_col], "mm")
print("piston thk:", first_row[piston_thk_col], "mm")
print("bolt sz:", first_row[bolt_sz_col], "mm")
print("bolt qual:", first_row[bolt_qual_col], "")
print("bolt qty:", first_row[bolt_qty_col], "")
print("pot lug qty:", first_row[pot_lug_qty_col], "")
print("pot lug l:", first_row[pot_lug_l_col], "mm")
print("pot lug w:", first_row[pot_lug_w_col], "mm")
print("pot lug t:", first_row[pot_lug_t_col], "mm")
print("sp lug qty:", first_row[sp_lug_qty_col], "")
print("sp lug l:", first_row[sp_lug_l_col], "mm")
print("sp lug w:", first_row[sp_lug_w_col], "mm")
print("sp lug t:", first_row[sp_lug_t_col], "mm")
print("pot ap long:", first_row[pot_ap_long_col], "mm")
print("pot ap tran:", first_row[pot_ap_tran_col], "mm")
print("pot ap thk:", first_row[pot_ap_t_col], "mm")
print("sp ap long:", first_row[sp_ap_long_col], "mm")
print("sp ap tran:", first_row[sp_ap_tran_col], "mm")
print("sp ap thk:", first_row[sp_ap_t_col], "mm\n")


# def bearing_maker(ULS_max, ULS_min, long_mov, tran_mov, long_rot, tran_rot, HP_pad, HP_sliding, i, j):
#     ULS_max = 1
# # Example call to the function (with dummy values for the parameters)
# bearing_maker(1500, 1000, 0, 0, 0, 0, True, False, 0, 0)

end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.2f} seconds")
