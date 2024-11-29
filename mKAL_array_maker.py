import math
import numpy as np
import time

from mKAL_inputs import *
from mKAL_sliding_materials import *
from mKAL_pad_and_disc import *
from mKAL_machining import *
from mKAL_sliding_plate import *
from mKAL_steel_yield import *
from mKAL_pot_piston import *
from mKAL_bolt_lugs_ap import *
from mKAL_weight import *


start_time = time.time()

np.set_printoptions(threshold=np.inf) #show an infinite amount in print window


# determination of minimum values of pad and disc dia from the predefined groups ----------------------

pad_min_dia = math.sqrt((max_vert/allow_press_pad)/3.142)*2
pad_min_dia_position = next((i for i, pad in enumerate(pad_defined_tuple) if pad[1] > pad_min_dia), None)

sliding_disc_min_dia_position = next((i for i, disc in enumerate(
    sliding_disc_dia_defined_array) if disc > pad_min_dia-pad_disc_diff_ceil), None)
sliding_disc_min_dia = sliding_disc_dia_defined_array[sliding_disc_min_dia_position]

# determination of minimum values of pad and disc dia from the predefined groups ----------------------


# define arrays for geometry

# pad_dia_tuple = tuple([pad[1] for pad in pad_defined_tuple[pad_min_dia_position:pad_min_dia_position + designs_above_min]])
# for row in pad_dia_tuple:
#     print(row)


pad_dia_tuple = tuple([pad[1] for pad in pad_defined_tuple[pad_min_dia_position:pad_min_dia_position + designs_above_min]])
# for row in pad_dia_tuple:
#     print(row)
if HP_pad: column_ref = 3
else: column_ref = 2

pad_h_tuple = tuple([pad[column_ref] for pad in pad_defined_tuple[pad_min_dia_position:pad_min_dia_position + designs_above_min]])
# for row in pad_h_tuple:
#     print(row)

# Combine pad diameter and height into a 2D array
# pad_dia_h_comb = np.column_stack((pad_dia_tuple, pad_h_tuple))
pad_dia_h_comb = tuple(zip(pad_dia_tuple, pad_h_tuple))
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("pad_dia_h_comb")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(pad_dia_h_comb,"pad_dia_h_comb")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

sliding_disc_dia_tuple = (
    [disc for disc in sliding_disc_dia_defined_array[
        sliding_disc_min_dia_position:sliding_disc_min_dia_position + designs_above_min]])
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("sliding_disc_dia_tuple")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
# terminal_print(sliding_disc_dia_tuple,"sliding_disc_dia_tuple")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

pad_and_disc = []

# Repeat each block with the same value from `sliding_disc_dia_array`
for value in sliding_disc_dia_tuple:
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((dia, height, value) for dia, height in pad_dia_h_comb)
    pad_and_disc.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("pad_and_disc")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(pad_and_disc,"pad_and_disc")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
# for row in pad_and_disc:
#     print(row)

pad_disc_dia_relation = tuple(
    pair for pair in pad_and_disc if abs(pair[pad_dia_col] - pair[main_sliding_dia_col]) <= pad_disc_diff_ceil
)
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("pad_disc_dia_relation")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(pad_disc_dia_relation,"pad_disc_dia_relation")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

# for row in pad_disc_dia_relation:
#     print(row)

sp_prop_add = tuple(
    (
        pad_dia, height, disc_dia,
        *sp_properties(disc_dia,long_mov_tot,tran_mov_tot)
    )
    for pad_dia, height, disc_dia in pad_disc_dia_relation
)
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("sp_prop_add")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(sp_prop_add,"sp_prop_add")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------


pot_walls_added = []
for row in sp_prop_add:
    first_col_value = row[0]  # Use the first column value
    
    # Calculate the new tuple
    new_tuple = pot_walls(row)
    
    # Create rows by appending each value of the new tuple to the original tuple
    for value in new_tuple:
        pot_walls_added.append((*row, value))
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("pot_walls_added")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(pot_walls_added,"pot_walls_added")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------


pot_bot_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in pot_bot:
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, value) for row in pot_walls_added)
    pot_bot_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("pot_bot_added")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(pot_bot_added,"pot_bot_added")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------


pot_wall_bot_relation = tuple(
    pair for pair in pot_bot_added if abs(pair[pot_bot_thk_col] / pair[pot_wall_thk_col]) <= pot_bot_to_wall
)
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("pot_wall_bot_relation")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(pot_wall_bot_relation,"pot_wall_bot_relation")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------



pot_bases_passing_disc_tension = tuple(row for row in pot_wall_bot_relation if pot_base_disc_tension(row))
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("pot_bases_passing_disc_tension")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(pot_bases_passing_disc_tension,"pot_bases_passing_disc_tension")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------


walls_passing_design_force = tuple(row for row in pot_bases_passing_disc_tension if design_force_pot_wall(row))
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("walls_passing_design_force")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(walls_passing_design_force,"walls_passing_design_force")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------


walls_passing_shear_stress = tuple(row for row in walls_passing_design_force if h_shear_stress_wall(row))
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("walls_passing_shear_stress")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(walls_passing_shear_stress,"walls_passing_shear_stress")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

conc_press_first_pass = tuple(
    row for row in walls_passing_shear_stress if max_press_lower_contact/2<conc_press_pot(row)<max_press_lower_contact)
if not conc_press_first_pass:
    conc_press_first_pass = walls_passing_shear_stress

#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("conc_press_first_pass")
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")

terminal_print(conc_press_first_pass,"conc_press_first_pass")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

data_with_piston_h = tuple((*row, piston_h(row)) for row in conc_press_first_pass)
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("data_with_piston_h")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(data_with_piston_h,"data_with_piston_h")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------


discs_passing_excentric_press = tuple(row for row in data_with_piston_h if sliding_disc_max_ecc_press(row))
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("discs_passing_excentric_press")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(discs_passing_excentric_press,"discs_passing_excentric_press")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

# print(rs_plus_char_str(site_temp_max)[1],"ex press")

bolt_sizes_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in bolt_size:
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, value) for row in discs_passing_excentric_press)
    bolt_sizes_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("bolt_sizes_added")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(bolt_sizes_added,"bolt_sizes_added")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

bolt_qual_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in bolt_qual():
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, value) for row in bolt_sizes_added)
    bolt_qual_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("bolt_qual_added")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(bolt_qual_added,"bolt_qual_added")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

bolt_qty_added = tuple((*row, bolt_qty(row)) for row in bolt_qual_added)
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("bolt_qty_added")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(bolt_qty_added,"bolt_qty_added")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

bolt_qty_considering_max = tuple(
    row for row in bolt_qty_added if row[bolt_qty_col] <= bolt_qty_max 
    and row[bolt_sz_col] >= bolt_sz_min(row)
    and row[bolt_sz_col] <= bolt_sz_max(row))
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("bolt_qty_considering_max")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(bolt_qty_considering_max,"bolt_qty_considering_max")

# for row in bolt_qty_considering_max:
#     print(row)

#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

# pot_lug_dims_add = tuple((*row, *lug_builder(row,2)) for row in bolt_qty_considering_max)
# terminal_print(pot_lug_dims_add,"pot_lug_dims_add")



pot_lugs_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in (2,4):
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, *lug_builder(row,value)) for row in bolt_qty_considering_max)
    pot_lugs_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("pot_lugs_added")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(pot_lugs_added,"pot_lugs_added")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

# sp_lug_dims_add = tuple((*row, *lug_builder(row,sp_lug_qty)) for row in pot_lugs_added)
# terminal_print(sp_lug_dims_add,"sp_lug_dims_add")

sp_lugs_added = []
# Repeat each block with the same value from `sliding_disc_dia_array`
for value in (2,4):
    # Add the new value to each pair in `pad_dia_h_comb`
    repeated_matrix = tuple((*row, *lug_builder(row,value)) for row in pot_lugs_added)
    sp_lugs_added.extend(repeated_matrix)  # Append all tuples from repeated_matrix to combo1
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("sp_lugs_added")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(sp_lugs_added,"sp_lugs_added")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

lugs_sizes = tuple(row for row in sp_lugs_added if lug_length_filter(row))
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("lugs_sizes")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(lugs_sizes,"lugs_sizes")
# # Print each row on its own line
# for row in sp_lug_dims_add:
#     print(row)
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

anchor_plates_add = tuple((*row, *anchor_plate_builder(row)) for row in lugs_sizes)
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("anchor_plates_add")
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")
terminal_print(anchor_plates_add,"anchor_plates_add")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

passing_lower_conc_press = tuple(
    row for row in anchor_plates_add if conc_press_pot(row)<max_press_lower_contact)
if not passing_lower_conc_press:
    print("no passing conc press")

#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("passing_lower_conc_press")
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")

column_values = [row[sliding_thk_col] for row in passing_lower_conc_press]
average = sum(column_values) / len(column_values)

print(f"The average of spts is {average}")
terminal_print(passing_lower_conc_press,"passing_lower_conc_press")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

sp_ring_check=()
for row in passing_lower_conc_press:
    updated_row = tuple(
        value if i != sliding_thk_col else sp_t_ring(row) 
        for i, value in enumerate(row)
    )
    sp_ring_check += (updated_row,)

#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("sp_ring_check")
# for row in sp_def_check:
#     print(row)
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")

column_values = [row[sliding_thk_col] for row in sp_ring_check]
average = sum(column_values) / len(column_values)

print(f"The average of spts is {average}")
terminal_print(passing_lower_conc_press,"passing_lower_conc_press")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------

sp_def_check=()
for row in sp_ring_check:
    updated_row = tuple(
        value if i != sliding_thk_col else sp_t_deformation(row) 
        for i, value in enumerate(row)
    )
    sp_def_check += (updated_row,)

#### TERMINAL PRINTS AND OTHER CHECKS ------------------------
print("sp_def_check")
# for row in sp_def_check:
#     print(row)
end_time = time.time()
duration = end_time - start_time
print(f"Execution Time: {duration:.3f} seconds")

column_values = [row[sliding_thk_col] for row in sp_def_check]
average = sum(column_values) / len(column_values)

print(f"The average of spts is {average}")
terminal_print(sp_def_check,"sp_def_check")
#### TERMINAL PRINTS AND OTHER CHECKS ------------------------


# Calculate and stack weight into the tuple
data_with_weight = tuple((*row, weight_check(row)) for row in sp_def_check)
# for row in data_with_weight:
#     print(row)

raw_weight_added = tuple((*row, raw_weights(row)) for row in data_with_weight)
# for row in raw_weight_added:
#     print(row)

removed_weight_added = tuple((*row, removed_weights(row)) for row in raw_weight_added)
# for row in removed_weight_added:
#     print(row)

price_EUR_added = tuple((*row, total_price(row)) for row in removed_weight_added)
# for row in removed_weight_added:
#     print(row)

# Sort the tuple based on the specific column (bearing_kg_col) in ascending order
sorted_data_with_weight = tuple(
    row for row in sorted(price_EUR_added, key=lambda x: x[-4], reverse=False)
)

sorted_raw = tuple(
    row for row in sorted(price_EUR_added, key=lambda x: x[-3], reverse=False)
)

sorted_removed = tuple(
    row for row in sorted(price_EUR_added, key=lambda x: x[-2], reverse=False)
)

sorted_price = tuple(
    row for row in sorted(price_EUR_added, key=lambda x: x[-1], reverse=False)
)

# print(design_moment(sorted_data_with_weight[0],"ULS",ULS_max),"design mom")

# print(sliding_disc_max_ecc_press(sorted_data_with_weight[0]),"ex press")

# Accessing first row in sorted data
first_row = sorted_data_with_weight[0]
first_row_raw = sorted_raw[0]
first_row_removed = sorted_removed[0]
first_row_price = sorted_price[0]

# print(sp_t_ring(first_row))

# print(sp_t_deformation(first_row))

# Print the first row (lightest bearing)
print("lowest weight bearing dims:", first_row,"\n")
print("lowest weight raw dims:", first_row_raw,"\n")
print("lowest weight removed material:", first_row_removed,"\n")
print("lowest price:", first_row_price,"\n")

pot_mach(first_row,True)
piston_mach(first_row,True)
ap_mach(first_row,True)
sp_mach(first_row,True)

# Access specific columns from the first row (adjust indices accordingly)
print("\n\nThe lightest bearing weighs:", first_row[-4], "kg\n")
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
print("pot height:", first_row[pot_bot_thk_col]+pot_wall_interior_height(row), "mm")
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
print(f"Execution Time: {duration:.3f} seconds")
