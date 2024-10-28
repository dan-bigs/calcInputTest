import math
import numpy as np
import itertools

np.set_printoptions(threshold=np.inf)

ULS_max = 15000000 #N
long_mov = 150
tran_mov = 20
HP_pad = True
HP_sliding = True
site_temp_min = -5

steel_type = 355

steel_yield_array = [
    [40, 235, 355],  # thickness, S235, S355J2+N
    [80, 215, 335],
    [100, 215, 315],
    [150, 295, 295],
    [200, 185, 285],
    [250, 175, 275],
    [400, 0, 265]
]

designs_above_min = 6

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

pot_wall = np.arange(20,200,10)
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


sliding_disc_dia_array = np.array([disc for disc in sliding_disc_dia_defined_array[sliding_disc_min_dia_position:sliding_disc_min_dia_position + designs_above_min + 4]])

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
#print("New Matrix with Additional Column:\n", combo1)
print("pad dia, h, and disc dia array Size:", combo1.shape)




max_difference_threshold = 50
filtered_combo1 = np.array([
    pair for pair in combo1 if abs(pair[0] - pair[2]) <= max_difference_threshold])

#print("Filtered Combinations:\n", filtered_combo1)
print("filtered to keep pad dia and sliding dia close in size array Size:", filtered_combo1.shape)

sliding_sheet_long = filtered_combo1[:,1]+long_mov+20
sliding_plate_long = sliding_sheet_long+20

sliding_sheet_tran = filtered_combo1[:,1]+tran_mov+20
sliding_plate_tran = sliding_sheet_tran+20

column_add_combo1 = np.column_stack((filtered_combo1, sliding_sheet_long,sliding_sheet_tran,sliding_plate_long,sliding_plate_tran))

#print("Filtered Combinations:\n", column_add_combo1)
print("sliding sheet and plate add array Size:", column_add_combo1.shape)


def ring_tension_force(row):
    pad_thick = row[1]
    pot_bot_thick = row[8]
    pad_dia = row[0]
    tension_force_value = (4*ULS_max*(pad_thick+pot_bot_thick))/(math.pi*pad_dia)
    #print(tension_force_value)
    return(tension_force_value)

def rs_plus_fric(row):
    sliding_sheet_dia = row[0]
    sliding_sheet_area = math.pi*(sliding_sheet_dia/2)**2
    centric_press = ULS_max/sliding_sheet_area
    if -50 <= site_temp_min < -35:
        min_fric = 0.035     # Set the minimum fric value
        max_fric = 0.08     # Set the maximum fric value
        fric = 2.2 / (centric_press + 17)
        fric = max(min_fric, min(fric, max_fric))
    if -35 <= site_temp_min < -5:
        min_fric = 0.035     # Set the minimum fric value
        max_fric = 0.08     # Set the maximum fric value
        fric = 2.2 / (centric_press + 17)
        fric = max(min_fric, min(fric, max_fric))
    if -5 <= site_temp_min < math.inf:
        min_fric = 0.035     # Set the minimum fric value
        max_fric = 0.08     # Set the maximum fric value
        fric = 2.2 / (centric_press + 17)
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
#print("New Matrix with Additional Column:\n", combo3)
print("pot bot added array Size:", combo3.shape)


def design_force_pot_wall(row):

    pot_bot_thick = row[8]
    pot_wall_thick = row[7]
    pot_ring_section_area = pot_bot_thick * pot_wall_thick *2

    pot_wall_h_design_force = (ring_tension_force(row) + (rs_plus_fric(row)*ULS_max))/pot_ring_section_area
    #print("friction force of main sliding surface: ",rs_plus_fric(row)*ULS_max)
    #print(pot_wall_h_design_force)
    #print(pot_wall_thick)
    return yield_calc(pot_wall_thick) < pot_wall_h_design_force < 1.1 * yield_calc(pot_wall_thick) or pot_wall_h_design_force < yield_calc(pot_wall_thick) and pot_wall_thick == pot_wall[0]

def yield_calc(given_thickness):
    if steel_type == 355:
        row = 2
    else:
        row = 1

    yield_given_thickness = next((i[row] for i in steel_yield_array if i[0] >= given_thickness), None)
    #print(yield_given_thickness)
    return yield_given_thickness


filtered_combo3 = np.array([row for row in combo3 if design_force_pot_wall(row)])

# Print the filtered matrix
print("Filtered Matrix with Ring Tension:\n", filtered_combo3)
print("failing pot walls filtered array Size:", filtered_combo3.shape)


def pot_base_proofs(row):
    1==1





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
