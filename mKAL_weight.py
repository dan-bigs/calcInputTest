import math
from mKAL_inputs import *
from mKAL_pot_piston import *
from mKAL_machining import *

def total_price(row):
    total_price = (
        weight_cost(row)
        +mach_cost(row)
    )
    return total_price

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

def weight_cost(row):
    steel_weight = raw_weights(row)
    price_EUR_kg = Steel_EUR_per_kg
    cost_steel = steel_weight*price_EUR_kg
    return cost_steel

def raw_weights(row):
    total_weight = (
        pot_mach(row,False)[0]
        +sp_mach(row,False)[0]
        +piston_mach(row,False)[0]
        +lugs_weight(row)
        +ap_mach(row,False)[0]
        +ap_mach(row,False)[1]
        )
    return total_weight

def removed_weights(row):
    total_weight = (
        pot_mach(row,False)[2]
        +sp_mach(row,False)[2]
        +piston_mach(row,False)[2]
        +ap_mach(row,False)[4]
        +ap_mach(row,False)[5]
        )
    return total_weight

def mach_cost(row):
    rem_steel_weight = removed_weights(row)
    price_EUR_kg = mach_EUR_per_kg
    cost_mach = rem_steel_weight*price_EUR_kg
    return cost_mach

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
        row[pot_lug_l_col],row[pot_lug_w_col],row[pot_lug_t_col],row[sp_lug_qty_col])
    sp_lug_weight = rec_steel_weight(
        row[sp_lug_l_col],row[sp_lug_w_col],row[sp_lug_t_col],row[sp_lug_qty_col])
    return int(np.ceil(pot_lug_weight+sp_lug_weight))

def ap_weights(row):
    pot_ap_weight = rec_steel_weight(
        row[pot_ap_long_col],row[pot_ap_tran_col],row[pot_ap_t_col],pot_ap_qty)
    sp_ap_weight = rec_steel_weight(
        row[sp_ap_long_col],row[sp_ap_tran_col],row[sp_ap_t_col],sp_ap_qty)
    return (int(np.ceil(pot_ap_weight)), int(np.ceil(sp_ap_weight)))

def pot_mach(row,pot_print):
    pot_od = row[pad_dia_col]+2*row[pot_wall_thk_col]
    pot_wall_h = pot_wall_interior_height(row)
    pot_bot_thk = row[pot_bot_thk_col]
    pot_mach_h = pot_wall_h +  pot_bot_thk
    piston_dia = row[pad_dia_col]
    pot_starting_h = mach_reverse(1,pot_od,pot_mach_h)
    pot_area = math.pi*((pot_od/2)**2)
    pot_starting_weight = pot_area*pot_starting_h*steel_density
    finished_vol = (pot_area*pot_mach_h)-(math.pi*((piston_dia/2)**2)*pot_wall_h)
    surf_mach_vol = (math.pi*((pot_od/2)**2)*pot_mach_h)
    surf_mach_weight = int(np.ceil(surf_mach_vol*steel_density))
    finished_weight = pot_weight(row)
    surface_mm_removed = pot_starting_h-pot_mach_h
    surface_mm3_removed = pot_area*surface_mm_removed
    inner_mm3_removed = surf_mach_vol-finished_vol
    surface_kg_removed = surface_mm3_removed*steel_density
    inner_kg_removed = inner_mm3_removed*steel_density
    total_mm3 = surface_mm3_removed+inner_mm3_removed
    total_kg = surface_kg_removed+inner_kg_removed

    if  pot_print:
        print("\nThe delivered pot height is",pot_starting_h,"mm")
        print("The pot initially weighs",pot_starting_weight,"kg")
        print("To reach final",pot_mach_h,"mm pot height,",surface_mm_removed,"mm are removed")
        print(surface_kg_removed,"kg of surface material is removed via machining from one face")
        print(surface_mm3_removed/1000,"cm3 of surface material is removed via machining")

        print("The pot now weighs",surf_mach_weight,"kg")
        print("The finished pot weighs",finished_weight,"kg")
        print(inner_kg_removed,"kg of inner material is removed via machining")
        print(inner_mm3_removed/1000,"cm3 of inner material is removed via machining")
        
        print(total_kg,"TOTAL kg of material is removed via machining")
        print(total_mm3/1000,"TOTAL cm3 of material is removed via machining")

    return (pot_starting_weight,finished_weight,total_kg)

def piston_mach(row,piston_print):
    dia = row[pad_dia_col]
    finished_h = row[piston_thk_col]
    area = math.pi*((dia/2)**2)
    starting_h = mach_reverse(2,dia,finished_h)
    starting_vol = (area*starting_h)
    finished_vol = (area*finished_h)
    mm_removed = starting_h-finished_h
    removed_vol = starting_vol-finished_vol
    starting_weight = starting_vol*steel_density
    finished_weight = finished_vol*steel_density
    removed_weight = starting_weight-finished_weight

    if piston_print:
        print("\nThe delivered piston height is",starting_h,"mm")
        print("The piston initially weighs",starting_weight,"kg")
        print("To reach final",finished_h,"mm piston height,",mm_removed,"mm are removed",mm_removed/2,"per face")
        print(removed_weight,"kg of surface material is removed via machining")
        print(removed_vol/1000,"cm3 of surface material is removed via machining")
        print("The piston now weighs",finished_weight,"kg")

    return (starting_weight,finished_weight,removed_weight)

def ap_mach(row,ap_print):
    pot_ap_l = row[pot_ap_long_col]
    pot_ap_w = row[pot_ap_tran_col]
    pot_ap_dia = math.sqrt(pot_ap_l**2+pot_ap_w**2)
    pot_ap_t_finished = row[pot_ap_t_col]
    pot_ap_t_starting = mach_add("pot_ap",pot_ap_dia,pot_ap_t_finished)[1]
    pot_ap_starting_vol = pot_ap_l*pot_ap_w*pot_ap_t_starting
    pot_ap_finish_vol = pot_ap_l*pot_ap_w*pot_ap_t_finished
    pa_starting_weight = pot_ap_starting_vol*steel_density
    pa_finish_weight = pot_ap_finish_vol*steel_density
    pa_mm_rem = pot_ap_t_starting - pot_ap_t_finished
    pa_vol_rem = pot_ap_starting_vol - pot_ap_finish_vol
    pa_weight_rem = pa_starting_weight - pa_finish_weight

    if ap_print:
        print("\nThe delivered pot-side ap height is",pot_ap_t_starting,"mm")
        print("The pot-side ap initially weighs",pa_starting_weight,"kg")
        print("To reach final",pot_ap_t_finished,"mm height,",pa_mm_rem,"mm are removed")
        print(pa_weight_rem,"kg of surface material is removed via machining")
        print(pa_vol_rem/1000,"cm3 of surface material is removed via machining")
        print("The pot-side ap now weighs",pa_finish_weight,"kg")


    sp_ap_l = row[sp_ap_long_col]
    sp_ap_w = row[sp_ap_tran_col]
    sp_ap_dia = math.sqrt(sp_ap_l**2+sp_ap_w**2)
    sp_ap_t_finished = row[sp_ap_t_col]
    sp_ap_t_starting = mach_add("piston_ap",sp_ap_dia,sp_ap_t_finished)[1]
    sp_ap_starting_vol = sp_ap_l*sp_ap_w*sp_ap_t_starting
    sp_ap_finish_vol = sp_ap_l*sp_ap_w*sp_ap_t_finished
    sa_starting_weight = sp_ap_starting_vol*steel_density
    sa_finish_weight = sp_ap_finish_vol*steel_density
    sa_mm_rem = sp_ap_t_starting - sp_ap_t_finished
    sa_vol_rem = sp_ap_starting_vol - sp_ap_finish_vol
    sa_weight_rem = sa_starting_weight - sa_finish_weight

    if ap_print:
        print("\nThe delivered piston-side ap height is",sp_ap_t_starting,"mm")
        print("The piston-side ap initially weighs",sa_starting_weight,"kg")
        print("To reach final",sp_ap_t_finished,"mm height,",sa_mm_rem,"mm are removed")
        print(sa_weight_rem,"kg of surface material is removed via machining")
        print(sa_vol_rem/1000,"cm3 of surface material is removed via machining")
        print("The piston-side ap now weighs",sa_finish_weight,"kg")

    return (pa_starting_weight,sa_starting_weight,
            pa_finish_weight,sa_finish_weight,pa_weight_rem,pa_weight_rem)

def sp_mach(row,sp_print):
    sp_long = row[sliding_long_col]
    sp_tran = row[sliding_tran_col]
    sp_thk_finished = row[sliding_thk_col]
    sp_dia = math.sqrt(sp_long**2+sp_tran**2)
    thk_raw = mach_add("sp",sp_dia,sp_thk_finished)[1]
    vol_fin = sp_long*sp_tran*sp_thk_finished
    vol_raw = sp_long*sp_tran*thk_raw
    weight_fin = vol_fin*steel_density
    weight_raw = vol_raw*steel_density
    mm_rem = thk_raw-sp_thk_finished
    vol_rem = vol_raw-vol_fin
    weight_rem = weight_raw-weight_fin

    if sp_print:
        print("\nThe delivered sp height is",thk_raw,"mm")
        print("The sp initially weighs",weight_raw,"kg")
        print("To reach final",sp_thk_finished,"mm height,",mm_rem,"mm are removed")
        print(weight_rem,"kg of surface material is removed via machining")
        print(vol_rem/1000,"cm3 of surface material is removed via machining")
        print("The sp now weighs",weight_fin,"kg")

    return (weight_raw,weight_fin,weight_rem)