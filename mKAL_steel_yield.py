import math
from mKAL_inputs import *

def yield_calc_w_sf(given_thickness):
    # Determine the correct column based on the steel type
    if steel_type == 355:
        column = 2  # S355 yield strength
    else:
        column = 1  # S235 yield strength

    # Find the first row where thickness is sufficient
    matching_row = next((i for i in steel_yield_tuple if i[0] >= given_thickness), None)

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
    
def yield_calc_no_sf(given_thickness):
    if steel_type == 355:
        column = 2  # S355 yield strength
    else:
        column = 1  # S235 yield strength
    matching_row = next((i for i in steel_yield_tuple if i[0] >= given_thickness), None)
    if matching_row is not None:
        yield_given_thickness = matching_row[column]  # Get the yield strength value
        return yield_given_thickness
    else:
        return None