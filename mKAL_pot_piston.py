import math
from mKAL_inputs import *
from mKAL_sliding_materials import *
from mKAL_steel_yield import *
from mKAL_pad_and_disc import *
#from bearing_statics import *

def pot_walls(row):
    pad_dia = row[pad_dia_col]
    min_thk = ((math.ceil(pad_dia/10)*10)-pad_dia)/2+pot_wall_min
    max_thk = min_thk+pot_wall_max
    step = pot_wall_step

    pot_wall = tuple(min_thk + i * step for i in range(int((max_thk - min_thk) / step)))
    return pot_wall

def pot_base_disc_tension(row):
    pot_bot_thick = row[pot_bot_thk_col]
    pad_dia = row[pad_dia_col]
    pot_bot_dia = pad_dia
    base_area = pot_bot_dia * pot_bot_thick
    base_tension = (hydrostatic_force(row) + (h_force_max_fric(row)))/base_area

    base_tension_pass = base_tension < yield_calc_w_sf(pot_bot_thick)
    base_too_thick = base_tension < yield_calc_w_sf(pot_bot_thick)*proof_low_bound_pot_bot
    if base_too_thick: base_tension_pass = False
    if base_too_thick and pot_bot_thick == pot_bot[0]:
        return True
    else:return base_tension_pass

def pot_base_disc_tension_check(row):
    pot_bot_thick = row[pot_bot_thk_col]
    pad_dia = row[pad_dia_col]
    pot_bot_dia = pad_dia
    base_area = pot_bot_dia * pot_bot_thick
    base_tension = (hydrostatic_force(row) + (h_force_max_fric(row)))/base_area
    return base_tension

def h_shear_stress_wall(row):
    pot_wall_thick = row[pot_wall_thk_col]
    pad_dia = row[pad_dia_col]
    h_shear_stress = (hydrostatic_force(row) + 1.5*(h_force_max_fric(row)))/(pad_dia*pot_wall_thick/2)/math.sqrt(3)
    #print(h_shear_stress)
    return h_shear_stress < yield_calc_w_sf(pot_wall_thick)

def piston_h(row):
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    piston_h = min(piston_min,0.04*piston_dia)
    piston_h = pot_piston_contact_h(row)+piston_h+sliding_mat_recess
    return int(np.ceil(piston_h))

def pot_piston_contact_h(row):
    pad_dia = row[pad_dia_col]
    piston_dia = pad_dia
    fric_force = h_force_max_fric(row)
    total_h_fric = math.sqrt(fric_force**2+fric_force**2)
    force_related_h = (1.5*total_h_fric)/(piston_dia*yield_calc_w_sf(40))
    rotation_deflection = ULS_rotation_tot*0.5*piston_dia
    total_min_height = math.ceil(max(force_related_h + rotation_deflection,min_contact_h_pot_piston))
    # print("pot piston contact h",total_min_height)
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
    pot_wall_h_design_force = (hydrostatic_force(row) + (h_force_max_fric(row)))/pot_ring_section_area
    wall_yield_pass = pot_wall_h_design_force < yield_calc_no_sf(pot_wall_thick)
    wall_too_thick = pot_wall_h_design_force < yield_calc_no_sf(pot_wall_thick)*proof_low_bound_pot_wall
    if wall_too_thick: wall_yield_pass = False
    # if wall_too_thick and pot_wall_thick == pot_wall[0]:
    #     return True
    else: return wall_yield_pass
    # return yield_calc(pot_wall_thick)*.5 < pot_wall_h_design_force < yield_calc(pot_wall_thick)*1.3