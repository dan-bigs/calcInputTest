import math
import numpy as np
import itertools
import pandas as pd

np.set_printoptions(threshold=np.inf) #show an infinite amount in print window

#Inputs -----------------------

ULS_max = 15000000 #N
long_mov = 150
tran_mov = 20
HP_pad = True
HP_sliding = True
site_temp_min = -5
ULS_rotation = 0.02 #rad

#Inputs -----------------------

#Static assumptions -----------------------

steel_material_safety_factor = 1.3

dust_seal_h = 10

steel_type = 355

designs_above_min = 7

piston_min = 25

steel_density = .00785 #g/mm3
steel_density = steel_density/1000 #convert to kg/mm3

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
bearing_kg_col = 11
#component positions in the final matrix -----------------------


# steel_yield_array = [
#     [40, 235, 355],  # thickness, S235, S355J2+N
#     [80, 215, 335],
#     [100, 215, 315],
#     [150, 295, 295],
#     [200, 185, 285],
#     [250, 175, 275],
#     [400, 0, 265]
# ]

# column_names = ['thk','S235', 'S355']
# steel_yield_array = pd.DataFrame(steel_yield_array, columns=column_names)
# # steel_yield_array.index.name = 'thickness'
# print(steel_yield_array)

steel_yield_array = [
    [40, 235, 355],  # thickness, S235, S355J2+N
    [80, 215, 335],
    [100, 215, 315],
    [150, 295, 295],
    [200, 185, 285],
    [250, 175, 275],
    [400, 0, 265]
]


if HP_sliding: sliding_press_allow_centric = 90 #MPa

if HP_pad: char_press_pad = 120 #MPa
else: char_press_pad = 60 #MPa
allow_press_pad = char_press_pad/1.3 #Mpa

# Given pad data
pad_defined_array = [
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
]

# determination of minimum values from the predefined groups START

pad_min_dia = math.sqrt((ULS_max/allow_press_pad)/3.142)*2
pad_min_dia_position = next((i for i, pad in enumerate(pad_defined_array) if pad[1] > pad_min_dia), None)

sliding_disc_dia_defined_array = [140,170,200,235,270,300,335,365,400,435,465,500,535,570,600,635,670,705,740,775,805,840]
sliding_disc_min_dia_position = next((i for i, disc in enumerate(sliding_disc_dia_defined_array) if disc > pad_min_dia*.8), None)
sliding_disc_min_dia = sliding_disc_dia_defined_array[sliding_disc_min_dia_position]

# determination of minimum values from the predefined groups END

pot_wall = np.arange(20,200,5)
pot_bot = np.arange(12,50,1)

# define arrays for geometry

pad_dia_array = np.array([pad[1] for pad in pad_defined_array[pad_min_dia_position:pad_min_dia_position + designs_above_min]])

if HP_pad: column_ref = 3
else: column_ref = 2

pad_h_array = np.array([pad[column_ref] for pad in pad_defined_array[pad_min_dia_position:pad_min_dia_position + designs_above_min]])


# Combine pad diameter and height into a 2D array
pad_dia_h_comb = np.column_stack((pad_dia_array, pad_h_array))
#print("Pad Diameter and Height Combination:\n", pad_dia_h_comb)
print("pad dia and h array Size:", pad_dia_h_comb.shape)


sliding_disc_dia_array = np.array([disc for disc in sliding_disc_dia_defined_array[sliding_disc_min_dia_position:sliding_disc_min_dia_position + designs_above_min]])

#combo1 = np.kron(pad_dia_h_comb,sliding_disc_dia_array)

# Prepare to store the final result
# combining pad diameter and thickness with main sliding disc diameter
combo1 = []
# Repeat each block with the same value from new_1d_matrix
for value in sliding_disc_dia_array:
    # Repeat the existing matrix and add the new column with the same value
    repeated_matrix = np.hstack((pad_dia_h_comb, np.full((pad_dia_h_comb.shape[0], 1), value)))
    combo1.append(repeated_matrix)

# Stack all the repeated matrices vertically
combo1 = np.vstack(combo1)

# column_names = ['pad thick', 'main sliding dia']
# combo1 = pd.DataFrame(combo1, columns=column_names)
# combo1.index.name = 'pad dia'

# print("New Matrix with Additional Column:\n", combo1)
print("pad dia, h, and disc dia array Size:", combo1.shape)


max_difference_threshold = 70
filtered_combo1 = np.array([
    pair for pair in combo1 if abs(pair[0] - pair[2]) <= max_difference_threshold and (pair[0] - pair[2])>= 10])

# print("Filtered Combinations:\n", filtered_combo1)
print("filtered to keep pad dia and sliding dia close in size array Size:", filtered_combo1.shape)

sliding_sheet_long = filtered_combo1[:,2]+long_mov+50
sliding_plate_long = sliding_sheet_long+20

sliding_sheet_tran = filtered_combo1[:,2]+tran_mov+50
sliding_plate_tran = sliding_sheet_tran+20

sliding_plate_thk = np.ceil(np.sqrt(sliding_plate_long**2+sliding_plate_tran**2)*.04)

column_add_combo1 = np.column_stack((filtered_combo1, sliding_sheet_long,sliding_sheet_tran,sliding_plate_long,sliding_plate_tran,sliding_plate_thk))

# print("Filtered Combinations:\n", column_add_combo1)
print("sliding sheet and plate add array Size:", column_add_combo1.shape)


def rs_plus_fric(row):
    sliding_mat_dia = row[main_sliding_dia_col]
    sliding_sheet_area = math.pi*(sliding_mat_dia/2)**2
    centric_press = ULS_max/sliding_sheet_area
    if -50 <= site_temp_min < -35:
        min_fric = 0.035     # Set the minimum fric value
        max_fric = 0.08     # Set the maximum fric value
        fric = 2.8 / (centric_press + 20)
        fric = max(min_fric, min(fric, max_fric))
    if -35 <= site_temp_min < -5:
        min_fric = 0.035     # Set the minimum fric value
        max_fric = 0.08     # Set the maximum fric value
        fric = 2.2 / (centric_press + 17)
        fric = max(min_fric, min(fric, max_fric))
    if -5 <= site_temp_min < math.inf:
        min_fric = 0.035     # Set the minimum fric value
        max_fric = 0.08     # Set the maximum fric value
        fric = 1.8 / (centric_press + 16)
        fric = max(min_fric, min(fric, max_fric))
    #print("rsplus fric: ",fric)
    return fric

# fric = 0.05 #testing value

# Prepare to store the final result
combo2 = []
# adding pot wall values to combo1
for value in pot_wall:
    # Repeat the existing matrix and add the new column with the same value
    repeated_matrix = np.hstack((column_add_combo1, np.full((column_add_combo1.shape[0], 1), value)))
    combo2.append(repeated_matrix)

# Stack all the repeated matrices vertically
combo2 = np.vstack(combo2)
#print("New Matrix with Additional Column:\n", combo2)
print("pot wall added array Size:", combo2.shape)


combo3 = []
for value in pot_bot:
    repeated_matrix = np.hstack((combo2, np.full((combo2.shape[0], 1), value)))
    combo3.append(repeated_matrix)
combo3 = np.vstack(combo3)
# print("New Matrix with Additional Column:\n", combo3)
print("pot bot added array Size:", combo3.shape)

def pot_piston_contact_h(row):
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    fric_force = rs_plus_fric(row)
    total_h_fric = math.sqrt(fric_force**2+fric_force**2)
    force_related_h = (1.5*total_h_fric)/(piston_dia*yield_calc(40))
    rotation_deflection = ULS_rotation*0.5*piston_dia
    total_min_height = max(force_related_h + rotation_deflection,5)
    return total_min_height

def hydrostatic_force(row):
    pad_thick = row[pad_thk_col]
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    rotation_deflection = ULS_rotation*0.5*piston_dia
    hydrostatic_force_value = (4*ULS_max*(pad_thick+rotation_deflection))/(math.pi*pad_dia)
    # print(hydrostatic_force_value)
    return hydrostatic_force_value

def pot_wall_interior_height(row):
    pad_thick = row[pad_thk_col]
    return pad_thick+pot_piston_contact_h(row)

def design_force_pot_wall(row):

    pot_wall_thick = row[pot_wall_thk_col]
    # print(pot_wall_thick)
    pot_wall_h = pot_wall_interior_height(row)
    pot_ring_section_area = pot_wall_h * pot_wall_thick * 2
    pot_wall_h_design_force = (hydrostatic_force(row) + (rs_plus_fric(row)*ULS_max))/pot_ring_section_area
    #print("friction force of main sliding surface: ",rs_plus_fric(row)*ULS_max)
    # print(pot_wall_thick)
    # print(pot_wall_h_design_force)
    #print(pot_wall_thick)
    # print("pot wall height", pot_wall_h)
    # print(yield_calc(pot_wall_thick)*.5 < pot_wall_h_design_force < yield_calc(pot_wall_thick)*1.3)
    wall_yield_pass = pot_wall_h_design_force < yield_calc(pot_wall_thick)*1.3
    wall_too_thick = pot_wall_h_design_force < yield_calc(pot_wall_thick)*1.3*0.7
    if wall_too_thick: wall_yield_pass = False
    if wall_too_thick and pot_wall_thick == pot_wall[0]:
        return True
    else: return wall_yield_pass
    # return yield_calc(pot_wall_thick)*.5 < pot_wall_h_design_force < yield_calc(pot_wall_thick)*1.3

def yield_calc(given_thickness):
    # Determine the correct column based on the steel type
    if steel_type == 355:
        column = 2  # S355 yield strength
    else:
        column = 1  # S235 yield strength

    # Find the first row where thickness is sufficient
    matching_row = next((i for i in steel_yield_array if i[0] >= given_thickness), None)

    # Check if a matching row was found
    if matching_row is not None:
        # Calculate the yield strength and divide by the safety factor
        yield_given_thickness = matching_row[column]  # Get the yield strength value
        yield_given_thickness /= steel_material_safety_factor  # Now perform the division
        # print("Yield given thickness:", yield_given_thickness)  # Debug output
        return yield_given_thickness
    else:
        # print("No matching thickness found.")
        return None  # Handle the case where no matching thickness is found

# test = pot_wall_interior_height(combo3[1])
# print ("tester",test)

def pot_base_disc_tension(row):
    pot_bot_thick = row[pot_bot_thk_col]
    pad_dia = row[pad_dia_col]
    pot_bot_dia = pad_dia
    base_area = pot_bot_dia * pot_bot_thick
    base_tension = (hydrostatic_force(row) + (rs_plus_fric(row)*ULS_max))/base_area

    base_tesion_pass = base_tension < yield_calc(pot_bot_thick)*1.3
    base_too_thick = base_tension < yield_calc(pot_bot_thick)*1.3*0.7
    if base_too_thick: base_tesion_pass = False
    if base_too_thick and pot_bot_thick == pot_bot[0]:
        return True
    else:return base_tesion_pass
    
    return base_tension < yield_calc(pot_bot_thick)

# test = pot_base_disc_tension(combo3[1])
# print ("tester",test)

combo3 = np.array([row for row in combo3 if pot_base_disc_tension(row)])

# Print the filtered matrix
# print("Filtered Matrix with Ring Tension:\n", combo3)
print("remove bases failing disc tension:", combo3.shape)

filtered_combo3 = np.array([row for row in combo3 if design_force_pot_wall(row)])

# Print the filtered matrix
# print("Filtered Matrix with Ring Tension:\n", filtered_combo3)
print("remove pot walls failing RING TENSION array Size:", filtered_combo3.shape)


def h_shear_stress_wall(row):
    pot_wall_thick = row[pot_wall_thk_col]
    pad_dia = row[pad_dia_col]
    h_shear_stress = (hydrostatic_force(row) + 1.5*(rs_plus_fric(row)*ULS_max))/(pad_dia*pot_wall_thick/2)/math.sqrt(3)
    #print(h_shear_stress)
    return h_shear_stress < yield_calc(pot_wall_thick)


filtered_filtered_combo3 = np.array([row for row in filtered_combo3 if h_shear_stress_wall(row)])
combo4 = filtered_filtered_combo3
# Print the filtered matrix
# print("Filtered Matrix with Shear Stress:\n", filtered_filtered_combo3)
print("remove pot walls failing SHEAR STRESS array Size:", filtered_filtered_combo3.shape)

def piston_h(row):
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    piston_h = min(piston_min,0.04*piston_dia)
    piston_h = pot_piston_contact_h(row)+piston_h
    return int(np.ceil(piston_h))

def weight_check(row):
    pot_od = row[pad_dia_col]+2*row[pot_wall_thk_col]
    pot_wall_h = pot_wall_interior_height(row)
    pot_bot_thk = row[pot_bot_thk_col]
    pot_total_h = pot_wall_h +  pot_bot_thk
    piston_dia = row[pad_dia_col]
    piston_thk = row[piston_thk_col]
    sp_long = row[sliding_long_col]
    sp_tran = row[sliding_tran_col]
    sp_thk = row[sliding_thk_col]

    pot_vol = (math.pi*((pot_od/2)**2)*pot_total_h)-(math.pi*((piston_dia/2)**2)*pot_wall_h)
    piston_vol = (math.pi*((piston_dia/2)**2)*piston_thk)
    sp_vol = sp_long*sp_tran*sp_thk
    total_vol = pot_vol+piston_vol+sp_vol
    weight = total_vol*steel_density
    return int(np.ceil(weight))

def pot_weight(row):
    pot_od = row[pad_dia_col]+2*row[pot_wall_thk_col]
    pot_wall_h = pot_wall_interior_height(row)
    pot_bot_thk = row[pot_bot_thk_col]
    pot_total_h = pot_wall_h +  pot_bot_thk
    piston_dia = row[pad_dia_col]
    pot_vol = (math.pi*((pot_od/2)**2)*pot_total_h)-(math.pi*((piston_dia/2)**2)*pot_wall_h)
    total_vol = pot_vol
    weight = total_vol*steel_density
    return int(np.ceil(weight))
def sp_weight(row):
    sp_long = row[sliding_long_col]
    sp_tran = row[sliding_tran_col]
    sp_thk = row[sliding_thk_col]
    sp_vol = sp_long*sp_tran*sp_thk
    total_vol = sp_vol
    weight = total_vol*steel_density
    return int(np.ceil(weight))
def piston_weight(row):
    piston_dia = row[pad_dia_col]
    piston_thk = row[piston_thk_col]
    piston_vol = (math.pi*((piston_dia/2)**2)*piston_thk)
    total_vol = piston_vol
    weight = total_vol*steel_density
    return int(np.ceil(weight))

piston_h_values = np.array([piston_h(row) for row in combo4])
data_with_piston_h = np.column_stack((combo4, piston_h_values))
# print("piston h added:\n", data_with_piston_h)
print("piston h added:", data_with_piston_h.shape)

weight = np.array([weight_check(row) for row in data_with_piston_h])
data_with_weight = np.column_stack((data_with_piston_h, weight))

# print("weight added:\n", data_with_weight)
print("weight added:", data_with_weight.shape)

# Get indices of the sorted column in descending order
sorted_indices = np.argsort(data_with_weight[:, bearing_kg_col])[::1]

# Reorder the matrix based on these indices
sorted_matrix = data_with_weight[sorted_indices]

# print("weight sorted:\n", sorted_matrix)
print("weight sorted:", sorted_matrix.shape)

print("\n\nThe smallest bearing weighs:",sorted_matrix[0,11],"kg")
print("The pot weighs:",pot_weight(sorted_matrix[0]),"kg")
print("The piston weighs:",piston_weight(sorted_matrix[0]),"kg")
print("The sliding plate weighs:",sp_weight(sorted_matrix[0]),"kg\n\n")

def bearing_maker(ULS_max, ULS_min, long_mov, tran_mov, long_rot, tran_rot, HP_pad, HP_sliding, i, j):
    ULS_max = 1
# Example call to the function (with dummy values for the parameters)
bearing_maker(1500, 1000, 0, 0, 0, 0, True, False, 0, 0)








# # Function to calculate the area from diameter
# # Function to calculate the ULS max pressure from diameter
# def calculate_ULS_max_pressure(diameter):
#     radius = diameter / 2
#     area = math.pi * (radius ** 2)
#     ULS_max_pressure = ULS_max / area
#     return ULS_max_pressure

# # Main function to find the smallest diameter at or below allowable pressure
# def find_smallest_diameter(ULS_max):

#     # Initialize variables to store the result
#     smallest_pad_diameter = None

#     print(f"Allowable pressure: {allow_press_pad:.2f} MPa\n")

#     # Loop through pad_defined_array to find the smallest diameter that satisfies the condition
#     for pad in pad_defined_array:
#         diameter = pad[1]
#         ULS_max_pressure = calculate_ULS_max_pressure(diameter)

#         if ULS_max_pressure <= allow_press_pad:
#             if smallest_pad_diameter is None or diameter < smallest_pad_diameter:
#                 smallest_pad_diameter = diameter
#     return smallest_pad_diameter

# # Find and print the smallest diameter that fulfills the condition
# smallest_pad_diameter = find_smallest_diameter(ULS_max)
# if smallest_pad_diameter:
#     print(f"The smallest diameter that fulfills the pressure condition is: {smallest_pad_diameter} mm")
# else:
#     print("No pad diameter fulfills the pressure condition.")
