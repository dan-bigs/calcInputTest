import math
import numpy
from bearing_variables import *

def terminal_print(combo,name):
    total_elements = sum(len(row) for row in combo)
    row_num = len(combo)
    # print("pot walls added:\n", combo2)
    print(f"{name} tuple Rows:", row_num)
    print(f"{name} tuple Elements:", total_elements,"\n")

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

def rs_plus_char_str(temp):
    degC = [row[0] for row in rs_char_str_values]  # Temperature values
    rs_values = [row[1] for row in rs_char_str_values]  # rs values
    rs75_values = [row[2] for row in rs_char_str_values]  # rs75 values
    return (np.interp(temp,degC,rs_values),np.interp(temp,degC,rs75_values))

def get_value(table, name, category,ref):
    for row in table:
        if row[0] == name and row[1] == category:
            return row[ref]  # You can also choose to return specific columns if needed
    return None  # Return None if no match is found


def pad_restraint_moment(row,case):
    F0 = get_value(F_values,pad_manufacturer,pad_type,2)
    F1 = get_value(F_values,pad_manufacturer,pad_type,3)
    F2 = get_value(F_values,pad_manufacturer,pad_type,4)
    pad_dia = row[pad_dia_col]
    if case == "ULS": a2x = ULS_rotation_x_var
    if case == "SLS": a2x = 0
    if case == "ULS": a2y = ULS_rotation_y_var
    if case == "SLS": a2y = 0
    a1y = ULS_rotation_y_perm
    a1x = ULS_rotation_x_perm
    F0rotx = ULS_rotation_x/ULS_rotation_tot
    F0roty = ULS_rotation_y/ULS_rotation_tot
    res_moment_x = 0.032*pad_dia**3*(F0*F0rotx+F1*a1x+F2*a2x)
    res_moment_y = 0.032*pad_dia**3*(F0*F0roty+F1*a1y+F2*a2y)
    return (res_moment_x,res_moment_y)

def design_moment(row,case,vload):
    pad_dia = row[pad_dia_col]
    piston_thk = row[piston_thk_col]
    sliding_fricton_force = vload*rs_plus_fric(row)
    sliding_fric_arm = piston_thk+sliding_mat_thk-sliding_mat_recess
    steel_arm = pad_dia/2
    Mx = pad_restraint_moment(row,case)[0]
    My = pad_restraint_moment(row,case)[1]+sliding_fricton_force*(sliding_fric_arm+(steel_steel_fric*steel_arm))
    return math.sqrt(Mx**2+My**2)

def sliding_disc_max_ecc_press(row):
    disc_dia = row[main_sliding_dia_col]
    disc_area = math.pi*(disc_dia/2)**2
    eccentricity_ULS = design_moment(row,"ULS",ULS_max)/ULS_max
    reduced_area = disc_area*(1-0.75*math.pi*eccentricity_ULS/disc_dia)
    return ULS_max/reduced_area < rs_plus_char_str(site_temp_max)[1]/rs_safety_fact

def sp_4percent_rule(sp_lo,sp_tr):
    sp_t = math.ceil(math.sqrt((sp_lo) ** 2 + (sp_tr) ** 2) * 0.04)  # sliding_plate_thk
    return sp_t

def sp_properties(disc_dia,long_mov,tran_mov):
    ss_lo = disc_dia + long_mov + extra_mov_for_ss
    ss_tr = disc_dia + tran_mov + extra_mov_for_ss
    sp_lo = ss_lo +min_spacing_ss_to_sp
    sp_tr = ss_tr + min_spacing_ss_to_sp
    sp_t = math.ceil(math.sqrt((sp_lo) ** 2 + (sp_tr) ** 2) * 0.04)  # sliding_plate_thk
    return ss_lo,ss_tr,sp_lo,sp_tr,sp_t

def pot_piston_contact_h(row):
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    fric_force = rs_plus_fric(row)
    total_h_fric = math.sqrt(fric_force**2+fric_force**2)
    force_related_h = (1.5*total_h_fric)/(piston_dia*yield_calc(40))
    rotation_deflection = ULS_rotation_tot*0.5*piston_dia
    total_min_height = max(force_related_h + rotation_deflection,min_contact_h_pot_piston)
    return total_min_height

def hydrostatic_force(row):
    pad_thick = row[pad_thk_col]
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    rotation_deflection = ULS_rotation_tot*0.5*piston_dia
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
    wall_yield_pass = pot_wall_h_design_force < yield_calc(pot_wall_thick)*steel_material_safety_factor
    wall_too_thick = pot_wall_h_design_force < yield_calc(pot_wall_thick)*steel_material_safety_factor*0.7
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

# test = pot_wall_interior_height(combo3[1])
# print ("tester",test)

def pot_base_disc_tension(row):
    pot_bot_thick = row[pot_bot_thk_col]
    pad_dia = row[pad_dia_col]
    pot_bot_dia = pad_dia
    base_area = pot_bot_dia * pot_bot_thick
    base_tension = (hydrostatic_force(row) + (rs_plus_fric(row)*ULS_max))/base_area

    base_tension_pass = base_tension < yield_calc(pot_bot_thick)*1.3
    base_too_thick = base_tension < yield_calc(pot_bot_thick)*1.3*0.7
    if base_too_thick: base_tension_pass = False
    if base_too_thick and pot_bot_thick == pot_bot[0]:
        return True
    else:return base_tension_pass

def h_shear_stress_wall(row):
    pot_wall_thick = row[pot_wall_thk_col]
    pad_dia = row[pad_dia_col]
    h_shear_stress = (hydrostatic_force(row) + 1.5*(rs_plus_fric(row)*ULS_max))/(pad_dia*pot_wall_thick/2)/math.sqrt(3)
    #print(h_shear_stress)
    return h_shear_stress < yield_calc(pot_wall_thick)

def piston_h(row):
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    piston_h = min(piston_min,0.04*piston_dia)
    piston_h = pot_piston_contact_h(row)+piston_h+sliding_mat_recess
    return int(np.ceil(piston_h))