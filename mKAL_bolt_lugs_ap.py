import math
from mKAL_inputs import *
from mKAL_sliding_materials import *
from mKAL_pad_and_disc import *
from mKAL_machining import *
from mKAL_sliding_plate import *
from mKAL_steel_yield import *
from mKAL_pot_piston import *

def bolt_qty(row):
    fric_force_tot = h_force_max_fric(row)/1000

    bolt_cap_row = next(filter(lambda brow: brow[0] == row[bolt_sz_col] and brow[1] == row[bolt_qual_col], bolt_shear_ULS_thread), None)
    bolt_cap = bolt_cap_row[-1] if bolt_cap_row else None

    qty = np.ceil(fric_force_tot/bolt_cap)
    return qty

def bolt_qual():
    bolt_qual = (8.8,)
    if sp_ap_qty == 1 or pot_ap_qty == 1:
        bolt_qual = (10.9,)
    else:
        bolt_qual = (8.8,)
    return bolt_qual

def weld_builder(weld_l,lug_thk,lug_qty):
    start_root = 4
    start_leg = 4*math.sqrt(2)
# def h_force_max_fric(row):
#     fric_coeff = rs_plus_fric(row)
#     fric_force_x = fric_coeff*max_vert
#     fric_force_y = fric_force_x
#     fric_force_tot = math.sqrt(fric_force_x**2+fric_force_y**2)
#     return fric_force_tot

def lug_builder(row,lug_qty):
    pot_dia = row[pad_dia_col]+2*row[pot_wall_thk_col]
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

    # assume fulcrum at pot edge opposite the lug
    bending = design_moment(row,"ULS",max_vert)/(pot_dia+edge_dist)
    # print("lug bending",bending)
    weld_area = (lug_thk-2)*lug_bolt_line_dim*lug_qty
    comb_force = math.sqrt(bending**2+(3*h_force_max_fric(row))**2)
    weld_stress = comb_force/weld_area
    # print(weld_stress)

    while weld_stress > yield_calc_w_sf(lug_thk) and lug_thk < 100:
        lug_thk = lug_thk+5
        weld_area = (lug_thk-2)*lug_bolt_line_dim*lug_qty
        comb_force = math.sqrt(bending**2+(3*h_force_max_fric(row))**2)
        weld_stress = comb_force/weld_area
        # print("weld stress",weld_stress)
        # print ("lug thick",lug_thk)

    return lug_qty,lug_bolt_line_dim,lug_dim_away_from_weld,lug_thk

def lug_length_filter(row):
    pot_dia = row[pad_dia_col]+2*row[pot_wall_thk_col]
    lug_leng_ok_pot = True
    lug_leng_ok_sp = True
    lug_leng_ok_pot = row[pot_lug_l_col] < pot_dia*lug_pot_ratio
    lug_leng_ok_sp = row[sp_lug_l_col] < row[sliding_tran_col]
    return lug_leng_ok_pot and lug_leng_ok_sp

def anchor_plate_builder(row):
    pot_dia = row[pad_dia_col]+2*row[pot_wall_thk_col]
    sliding_dia = row[main_sliding_dia_col]
    lug_l = row[pot_lug_l_col] # this is the longer dimension of the lug (bolt line)
    lug_w = row[pot_lug_w_col] # shorter side of lug
    sp_l = row[sliding_long_col]
    sp_w = row[sliding_tran_col]
    sp_lug_l = row[sp_lug_l_col]
    sp_lug_w = row[sp_lug_w_col]
    pot_dist_to_corner = 0.5*pot_dia/math.sqrt(2)+lug_w/math.sqrt(2)+0.5*lug_l/math.sqrt(2)
    sliding_dist_to_corner = 0.5*sliding_dia/math.sqrt(2)+lug_w/math.sqrt(2)+0.5*lug_l/math.sqrt(2)
    # sliding_ap_length = 0
    # sliding_ap_width = 0

    if row[pot_lug_qty_col] == 2:
        pot_ap_length = pot_dia+2*ap_perimeter
        pot_ap_length = math.ceil(pot_ap_length/5)*5
        pot_ap_width = pot_dia+2*lug_w+2*ap_perimeter
        pot_ap_width = math.ceil(pot_ap_width/5)*5

    if row[pot_lug_qty_col] == 4:
        min_dim = pot_dia + 2*ap_perimeter
        pot_ap_length = max(min_dim,2*pot_dist_to_corner+2*ap_perimeter)
        pot_ap_length = math.ceil(pot_ap_length/5)*5
        pot_ap_width = pot_ap_length
        pot_ap_width = math.ceil(pot_ap_width/5)*5
        
    pot_ap_diag = np.sqrt(pot_ap_length**2+pot_ap_width**2)
    pot_ap_thk = int(max(15,0.015*pot_ap_diag))
    pot_ap_thk = mach_add("pot_ap",pot_ap_diag,pot_ap_thk)[0]
    
    if row[sp_lug_qty_col] == 2:
        sliding_ap_length = sp_l+2*sp_lug_w+2*ap_perimeter
        sliding_ap_length = math.ceil(sliding_ap_length/5)*5
        sliding_ap_width = sp_w+2*ap_perimeter
        sliding_ap_width = math.ceil(sliding_ap_width/5)*5

    if row[sp_lug_qty_col] == 4:
        sliding_ap_length = long_mov_tot+extra_mov_for_ss/math.sqrt(2)+2*sliding_dist_to_corner+2*ap_perimeter
        sliding_ap_length = max(sliding_ap_length,sp_l+2*ap_perimeter)
        sliding_ap_length = math.ceil(sliding_ap_length/5)*5
        sliding_ap_width = tran_mov_tot+extra_mov_for_ss/math.sqrt(2)+2*sliding_dist_to_corner+2*ap_perimeter
        sliding_ap_width = max(sliding_ap_width,sp_w+2*ap_perimeter)
        sliding_ap_width = math.ceil(sliding_ap_width/5)*5
    
    sliding_ap_diag = np.sqrt(sliding_ap_length**2+sliding_ap_width**2)
    sliding_ap_thk = int(max(15,0.01*sliding_ap_diag))
    sliding_ap_thk = mach_add("piston_ap",sliding_ap_diag,sliding_ap_thk)[0]

    return pot_ap_length,pot_ap_width,pot_ap_thk,sliding_ap_length,sliding_ap_width,sliding_ap_thk

def conc_press_pot(row):
    pad_dia = row[pad_dia_col]
    pad_thk = row[pad_thk_col]
    pot_bot_thk = row[pot_bot_thk_col]
    pot_wall_thk = row[pot_wall_thk_col]
    pot_dia = pad_dia+2*pot_wall_thk
    pot_pist_cont_h = pot_piston_contact_h(row)
    if pot_ap_qty > 0 and  0 <= pot_ap_long_col < len(row):
        pot_ap_long = row[pot_ap_long_col]
        pot_ap_tran = row[pot_ap_tran_col]
        pot_ap_t = row[pot_ap_t_col]
    else:
        pot_ap_long = 0
        pot_ap_tran = 0
        pot_ap_t = 0
    lat_elast_force = 4*max_vert*pad_thk/pad_dia
    elast_arm = 0.5*(pad_thk+pot_bot_thk)
    h_load = h_force_max_fric(row)
    h_load_arm = 0.5*(pad_thk+pot_bot_thk+pot_pist_cont_h)

    if pot_ap_qty > 0 and  0 <= pot_ap_long_col < len(row):
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