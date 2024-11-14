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
    centric_press = max_vert/sliding_sheet_area
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
    # print("rsplus fric: ",fric)
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
    eccentricity_ULS = design_moment(row,"ULS",max_vert)/max_vert
    reduced_area = disc_area*(1-0.75*math.pi*eccentricity_ULS/disc_dia)
    return max_vert/reduced_area < rs_plus_char_str(site_temp_max)[1]/rs_safety_fact

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
    fric_force = max_vert*rs_plus_fric(row)
    total_h_fric = math.sqrt(fric_force**2+fric_force**2)
    force_related_h = (1.5*total_h_fric)/(piston_dia*yield_calc(40))
    rotation_deflection = ULS_rotation_tot*0.5*piston_dia
    total_min_height = math.ceil(max(force_related_h + rotation_deflection,min_contact_h_pot_piston))
    return total_min_height

def hydrostatic_force(row):
    pad_thick = row[pad_thk_col]
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    rotation_deflection = ULS_rotation_tot*0.5*piston_dia
    hydrostatic_force_value = (4*max_vert*(pad_thick+rotation_deflection))/(math.pi*pad_dia)
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
    pot_wall_h_design_force = (hydrostatic_force(row) + (rs_plus_fric(row)*max_vert))/pot_ring_section_area
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
    base_tension = (hydrostatic_force(row) + (rs_plus_fric(row)*max_vert))/base_area

    base_tension_pass = base_tension < yield_calc(pot_bot_thick)*1.3
    base_too_thick = base_tension < yield_calc(pot_bot_thick)*1.3*0.7
    if base_too_thick: base_tension_pass = False
    if base_too_thick and pot_bot_thick == pot_bot[0]:
        return True
    else:return base_tension_pass

def h_shear_stress_wall(row):
    pot_wall_thick = row[pot_wall_thk_col]
    pad_dia = row[pad_dia_col]
    h_shear_stress = (hydrostatic_force(row) + 1.5*(rs_plus_fric(row)*max_vert))/(pad_dia*pot_wall_thick/2)/math.sqrt(3)
    #print(h_shear_stress)
    return h_shear_stress < yield_calc(pot_wall_thick)

def piston_h(row):
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    piston_h = min(piston_min,0.04*piston_dia)
    piston_h = pot_piston_contact_h(row)+piston_h+sliding_mat_recess
    return int(np.ceil(piston_h))

def bolt_qty(row):
    fric_coeff = rs_plus_fric(row)
    fric_force_x = max_vert*fric_coeff
    fric_force_y = max_vert*fric_coeff
    fric_force_tot = math.sqrt(fric_force_x**2+fric_force_y**2)/1000

    bolt_cap_row = next(filter(lambda brow: brow[0] == row[bolt_sz_col] and brow[1] == row[bolt_qual_col], bolt_shear_ULS_thread), None)
    bolt_cap = bolt_cap_row[-1] if bolt_cap_row else None

    qty = np.ceil(fric_force_tot/bolt_cap)
    return qty

def h_force_max_fric(row):
    fric_coeff = rs_plus_fric(row)
    fric_force_x = fric_coeff*max_vert
    fric_force_y = fric_force_x
    fric_force_tot = math.sqrt(fric_force_x**2+fric_force_y**2)
    return fric_force_tot

def lug_builder(row,lug_qty):
    bolt_sz = row[bolt_sz_col]
    bolt_qual = row[bolt_qual_col]
    result = next(filter(
        lambda row: row[0] == "EN" and row[1] == bolt_sz and row[2] == bolt_qual, lug_thk_min
        ), None)
    min_thk = result[-1] if result else None
    row_qty = 1
    edge_dist = bolt_sz*lug_edge_factor
    bolt_sep_dist = bolt_sz*bolt_sep_perp_to_force_factor
    bolts_per_lug = (np.ceil(bolt_qty(row)/lug_qty))
    # print("bolts per lug: ",bolts_per_lug)
    lug_bolt_line_dim = math.ceil(((bolts_per_lug-1)*bolt_sep_dist+2*edge_dist)/5)*5
    lug_dim_away_from_weld = math.ceil(edge_dist*(row_qty+1)/5)*5
    # print("l and w: ",lug_bolt_line_dim,lug_dim_away_from_weld)
    lug_thk = min_thk

    # assuming simple weld stress
    weld_area = (lug_thk-2)*lug_bolt_line_dim*lug_qty
    fric_force = max_vert*rs_plus_fric(row)
    total_h_force_fric = math.sqrt(fric_force**2+fric_force**2)
    weld_stress = total_h_force_fric/weld_area

    while weld_stress > yield_calc(lug_thk) or lug_thk > 100:
        lug_thk = lug_thk+5
        weld_area = (lug_thk-2)*lug_bolt_line_dim*lug_qty
        weld_stress = total_h_force_fric/weld_area
        print("weld stress",weld_stress)
        print ("lug thick",lug_thk)

    return lug_qty,lug_bolt_line_dim,lug_dim_away_from_weld,lug_thk

def anchor_plate_builder(row):
    pot_dia = row[pad_dia_col]+2*row[pot_wall_thk_col]
    pot_ap_length = pot_dia+2*ap_perimeter
    pot_ap_length = math.ceil(pot_ap_length/5)*5
    pot_ap_width = pot_dia+2*row[pot_lug_w_col]+2*ap_perimeter
    pot_ap_width = math.ceil(pot_ap_width/5)*5
    pot_ap_diag = np.sqrt(pot_ap_length**2+pot_ap_width**2)
    pot_ap_thk = int(max(15,0.015*pot_ap_diag))
    
    sliding_ap_length = row[sliding_long_col]+2*row[sp_lug_w_col]+2*ap_perimeter
    sliding_ap_length = math.ceil(sliding_ap_length/5)*5
    sliding_ap_width = row[sliding_tran_col]+2*ap_perimeter
    sliding_ap_width = math.ceil(sliding_ap_width/5)*5
    sliding_ap_diag = np.sqrt(sliding_ap_length**2+sliding_ap_width**2)
    sliding_ap_thk = int(max(15,0.01*sliding_ap_diag))

    return pot_ap_length,pot_ap_width,pot_ap_thk,sliding_ap_length,sliding_ap_width,sliding_ap_thk

def conc_press_pot(row):
    pad_dia = row[pad_dia_col]
    pad_thk = row[pad_thk_col]
    pot_bot_thk = row[pot_bot_thk_col]
    pot_wall_thk = row[pot_wall_thk_col]
    pot_dia = pad_dia+2*pot_wall_thk
    pot_pist_cont_h = pot_piston_contact_h(row)
    pot_ap_long = row[pot_ap_long_col]
    pot_ap_tran = row[pot_ap_tran_col]
    pot_ap_t = row[pot_ap_t_col]
    lat_elast_force = 4*max_vert*pad_thk/pad_dia
    elast_arm = 0.5*(pad_thk+pot_bot_thk)
    h_load = h_force_max_fric(row)
    h_load_arm = 0.5*(pad_thk+pot_bot_thk+pot_pist_cont_h)

    if pot_ap_qty > 0:
        loaded_l = min(pot_ap_long,pot_dia+2*pot_ap_t)
        loaded_b = min(pot_ap_tran,pot_dia+2*pot_ap_t)
        eff_plate_width = min(loaded_l,loaded_b)
    else: eff_plate_width = pot_dia
    
    con_react_width = 0.5*eff_plate_width-(0.5*pad_dia+pot_bot_thk+pot_ap_t)
    conc_react_arm = pot_bot_thk+pot_ap_t+0.5*con_react_width

    elast_ecc_load = lat_elast_force*elast_arm/conc_react_arm
    h_ecc_load = h_load*h_load_arm/conc_react_arm

    core_conc_load = max_vert-elast_ecc_load-h_ecc_load
    core_conc_area = (pad_dia+2*pot_bot_thk+2*pot_ap_t)**2*math.pi/4
    core_press = core_conc_load/core_conc_area

    exc_area = (pot_dia+2*pot_ap_t)**2*math.pi/4-core_conc_area
    # print(exc_area)
    exc_press = (elast_ecc_load+4*h_ecc_load)/exc_area

    return exc_press