import math
from mKAL_inputs import *

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

def stiff_coeff(row):
    cent_press_serv = SLS_max_vert/(math.pi*(row[main_sliding_dia_col]/2)**2)
    # print(min(1.32,1.12+max(0,cent_press_serv-45)/226))
    return min(1.32,1.12+max(0,cent_press_serv-45)/226)