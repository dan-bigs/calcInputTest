import math
from mKAL_inputs import *
from mKAL_sliding_materials import *

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
    Mx = pad_restraint_moment(row,case)[0]+sliding_fricton_force*(sliding_fric_arm+(steel_steel_fric*steel_arm))
    My = pad_restraint_moment(row,case)[1]+sliding_fricton_force*(sliding_fric_arm+(steel_steel_fric*steel_arm))
    return math.sqrt(Mx**2+My**2)

def sliding_disc_max_ecc_press(row):
    disc_dia = row[main_sliding_dia_col]
    disc_area = math.pi*(disc_dia/2)**2
    eccentricity_ULS = design_moment(row,"ULS",max_vert)/max_vert
    reduced_area = disc_area*(1-0.75*math.pi*eccentricity_ULS/disc_dia)
    return max_vert/reduced_area < rs_plus_char_str(site_temp_max)[1]/rs_safety_fact

def sliding_disc_max_ecc_press_check(row):
    disc_dia = row[main_sliding_dia_col]
    disc_area = math.pi*(disc_dia/2)**2
    eccentricity_ULS = design_moment(row,"ULS",max_vert)/max_vert
    reduced_area = disc_area*(1-0.75*math.pi*eccentricity_ULS/disc_dia)
    return max_vert/reduced_area

def h_force_max_fric(row):
    fric_coeff = rs_plus_fric(row)
    fric_force_x = fric_coeff*max_vert
    fric_force_y = fric_force_x
    fric_force_tot = math.sqrt(fric_force_x**2+fric_force_y**2)
    return fric_force_tot+h_load_test