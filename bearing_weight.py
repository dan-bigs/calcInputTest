import math
from bearing_variables import *
from bearing_statics import *

def weight_check(row):
    total_weight = (
        pot_weight(row)
        +sp_weight(row)
        +piston_weight(row)
        +lugs_weight(row)
        +ap_weights(row)[0]
        +ap_weights(row)[1]
        )
    return total_weight

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

def rec_steel_weight(l,w,t,qty):
    weight = qty*l*w*t*steel_density
    return weight

def lugs_weight(row):
    pot_lug_weight = rec_steel_weight(
        row[pot_lug_l_col],row[pot_lug_w_col],row[pot_lug_t_col],pot_lug_qty)
    sp_lug_weight = rec_steel_weight(
        row[sp_lug_l_col],row[sp_lug_w_col],row[sp_lug_t_col],sp_lug_qty)
    return int(np.ceil(pot_lug_weight+sp_lug_weight))

def ap_weights(row):
    pot_ap_weight = rec_steel_weight(
        row[pot_ap_long_col],row[pot_ap_tran_col],row[pot_ap_t_col],pot_ap_qty)
    sp_ap_weight = rec_steel_weight(
        row[sp_ap_long_col],row[sp_ap_tran_col],row[sp_ap_t_col],sp_ap_qty)
    return (int(np.ceil(pot_ap_weight)), int(np.ceil(sp_ap_weight)))