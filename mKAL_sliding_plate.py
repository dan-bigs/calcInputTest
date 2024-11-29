import math
import time
from mKAL_inputs import *
from mKAL_machining import *
from mKAL_sliding_materials import *
from mKAL_steel_yield import *
from mKAL_machining import *

def sp_4percent_rule(sp_lo,sp_tr):
    sp_t = math.ceil(math.sqrt((sp_lo) ** 2 + (sp_tr) ** 2) * 0.04)  # sliding_plate_thk
    return sp_t

def sp_properties(disc_dia,long_mov,tran_mov):
    ss_lo = disc_dia + long_mov + extra_mov_for_ss
    ss_tr = disc_dia + tran_mov + extra_mov_for_ss
    sp_lo = ss_lo +min_spacing_ss_to_sp
    sp_tr = ss_tr + min_spacing_ss_to_sp
    sp_t = sp_4percent_rule(sp_lo,sp_tr)
    return ss_lo,ss_tr,sp_lo,sp_tr,sp_t

def sp_t_deformation(row):
    # start_time = time.time()
    sp_t = row[sliding_thk_col]
    # Econc is in GPa so converting to MPa
    Econ = Econc*1000
    sliding_dia = row[main_sliding_dia_col]
    sp_long = row[sliding_long_col]
    sp_tran = row[sliding_tran_col]
    sp_diag = math.sqrt(sp_long**2+sp_tran**2)

    if not piston_side_surf_conc:
        sp_t = mach_add("sp",sp_diag,sp_t)[0]
        # print("SP deformation proof skipped in the absence on concrete at piston side")
        return(sp_t)

    SLS_dynamic = SLS_max_vert-Perm_load
    min_dim = min(sp_long,sp_tran)
    delta_w = math.inf
    delta_w_max = 0
    if min_dim > 531:
        kc = 1.1
    else: kc = 1.1+(1.7-0.85*1.13*min_dim/sliding_dia)*(2-(1.13*min_dim)/300)
    while sp_t <= sp_tmax and delta_w >= delta_w_max:
        alpha_c = SLS_dynamic/Econ + Perm_load/(Econ*0.33)
        kb = 0.3+0.62*min_dim/sliding_dia
        alpha_b = (sliding_dia/(sliding_dia+2*sp_t))**2 * (796/min_dim)**0.4
        delta_w = 0.55*kc*alpha_c*kb*alpha_b/sliding_dia
        delta_w_max = sliding_protru*(0.45-1.708*stiff_coeff(row)*(
            math.sqrt(sliding_protru/sliding_dia)))
        sp_t = sp_t +1
        # print(sp_t)
    # end_time = time.time()
    # Calculate and print the runtime
    # execution_time = end_time - start_time

    sp_t = mach_add("sp",sp_diag,sp_t)[0]

    # print(f"Runtime sp_t_deformation: {execution_time:.5f} seconds")
    # return(delta_w,delta_w_max,sp_t,kc,alpha_c,kb,alpha_b)
    return(sp_t)

def sp_t_ring(row):
    sliding_disc_dia = row[main_sliding_dia_col]
    inner_dia = sliding_disc_dia
    sp_t = row[sliding_thk_col]
    outer_dia = 2*(inner_dia/2+sp_t*math.tan(60))
    a = inner_dia/2
    b = outer_dia/2
    uni_press = max_vert/(b**2*math.pi)
    ratio = b/a
    shape_factor = 2-4*ratio**2+((1.3*ratio**2)/(0.54+ratio**2))*(
        1.54+0.83*ratio**2+6.16*math.log(ratio)*ratio**2)
    eff_stress = (3*uni_press*a**2*shape_factor)/(8*sp_t**2)
    while eff_stress > yield_calc_w_sf(sp_t) and sp_t <= sp_tmax:
        sp_t = sp_t +1
        outer_dia = 2*(inner_dia/2+sp_t*math.tan(60))
        a = inner_dia/2
        b = outer_dia/2
        uni_press = max_vert/(b**2*math.pi)
        ratio = b/a
        shape_factor = 2-4*ratio**2+((1.3*ratio**2)/(0.54+ratio**2))*(
            1.54+0.83*ratio**2+6.16*math.log(ratio)*ratio**2)
        eff_stress = (3*uni_press*a**2*shape_factor)/(8*sp_t**2)
    return (sp_t)