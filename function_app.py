import azure.functions as func
import logging
import json
import math

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def find_optimal_combination(diameter_thickness_list, elastomeric_density_kg_m3, max_elastomer_pressure, max_sliding_pressure, vertical_load_kn, x_movement_mm, y_movement_mm):
    optimal_combination = None
    min_weight = float('inf')
    iteration_count = 0
    movement_safety = 25
    sliding_plate_overhang = 20

    logging.info("Starting to find optimal combination...")
    logging.debug(f"Parameters: density_kg_m3={elastomeric_density_kg_m3}, max_elastomer_pressure={max_elastomer_pressure}, max_sliding_pressure={max_sliding_pressure}, vertical_load_kn={vertical_load_kn}, x_movement_mm={x_movement_mm}, y_movement_mm={y_movement_mm}")

    for diameter, thickness in diameter_thickness_list:
        iteration_count += 1
        try:
            diameter_m = float(diameter) / 1000  # Convert mm to meters
            thickness_m = float(thickness) / 1000  # Convert mm to meters

            elastomer_area_m2 = 3.14159 * (diameter_m / 2) ** 2
            volume_m3 = elastomer_area_m2 * thickness_m
            weight_kg = elastomeric_density_kg_m3 * volume_m3
            load_kg = vertical_load_kn * 1000 / 9.81

            if elastomer_area_m2 > 0:
                elastomer_pressure_mpa = vertical_load_kn / elastomer_area_m2 / 1e3
            else:
                elastomer_pressure_mpa = 0

            if elastomer_pressure_mpa > max_elastomer_pressure:
                continue

            sliding_diameter_start = math.ceil((diameter / 2) / 5) * 5
            for sliding_diameter in range(sliding_diameter_start, diameter, 5):
                sliding_diameter_m = sliding_diameter / 1000  # Convert mm to meters
                sliding_area_m2 = 3.14159 * (sliding_diameter_m / 2) ** 2

                if sliding_area_m2 > 0:
                    sliding_pressure_mpa = vertical_load_kn / sliding_area_m2 / 1e3
                else:
                    sliding_pressure_mpa = 0

                stainless_long = sliding_diameter + x_movement_mm + movement_safety
                stainless_tran = sliding_diameter + y_movement_mm + movement_safety
                sliding_plate_long = stainless_long + sliding_plate_overhang
                sliding_plate_tran = stainless_tran + sliding_plate_overhang

                if sliding_pressure_mpa <= max_sliding_pressure:
                    if weight_kg < min_weight:
                        min_weight = weight_kg
                        optimal_combination = {
                            "Diameter (mm)": diameter,
                            "Thickness (mm)": thickness,
                            "Load on Bearing (kg)": round(load_kg, 1),
                            "Elastomer Pressure (MPa)": round(elastomer_pressure_mpa, 1),
                            "Sliding Diameter (mm)": sliding_diameter,
                            "Sliding Plate Longitudional": sliding_plate_long,
                            "Sliding Plate Transverse": sliding_plate_tran,
                            "Sliding Pressure (MPa)": round(sliding_pressure_mpa, 1),
                            "Sliding Pressure (MPa)": round(sliding_pressure_mpa, 1),
                            "Elastomer Weight (kg)": round(weight_kg, 2),
                        }
                        logging.debug(f"Found new optimal combination: {optimal_combination}")

        except ValueError as e:
            logging.error(f"ValueError occurred: {e}")
            continue

    logging.info(f"*** Number of iterations: {iteration_count} ***")
    if optimal_combination:
        logging.info(f"Optimal combination found: {optimal_combination}")
    else:
        logging.warning("No optimal combination found within the given pressure range.")

    return optimal_combination

@app.route(route="bearing_calculator_v1", methods=['POST'])
def bearing_calculator_v1(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    try:
        req_body = req.get_json()
        logging.info(f'Request body received: {json.dumps(req_body)}')

        max_pressure = req_body.get('max_pressure')
        max_sliding_pressure = req_body.get('max_sliding_pressure')
        vertical_load_kn = req_body.get('vertical_load_kn')
        x_movement_mm = req_body.get('x_movement_mm')
        y_movement_mm = req_body.get('y_movement_mm')

        if max_pressure is not None and max_sliding_pressure is not None and vertical_load_kn is not None and x_movement_mm is not None and y_movement_mm is not None:
            try:
                elastomeric_density_kg_m3 = 1522
                diameter_thickness_list = [
                    (152, 16), (215, 16), (282, 19), (349, 24), (416, 28), (484, 33), (551, 37), (619, 42), (687, 46), (754, 51),
                    (822, 55), (890, 60), (957, 64), (1025, 69), (1093, 73), (1160, 78), (1228, 82), (1296, 87), (1363, 91),
                    (1431, 96), (1499, 100), (1566, 105), (1634, 109), (1702, 114), (1769, 118), (1837, 123), (1905, 128), 
                    (1972, 132), (2040, 137), (2108, 141), (183, 16), (248, 16), (314, 21), (381, 26), (449, 30), (516, 35), 
                    (584, 39), (652, 44), (719, 48), (795, 53)
                ]

                optimal_combination = find_optimal_combination(
                    diameter_thickness_list,
                    elastomeric_density_kg_m3,
                    max_pressure,
                    max_sliding_pressure,
                    vertical_load_kn,
                    x_movement_mm,
                    y_movement_mm
                )

                if optimal_combination:
                    logging.info(f'Optimal combination found: {json.dumps(optimal_combination)}')
                    return func.HttpResponse(
                        json.dumps(optimal_combination),
                        mimetype="application/json",
                        headers=headers
                    )
                else:
                    logging.info('No optimal combination found within the pressure range.')
                    return func.HttpResponse("No optimal combination found within the pressure range.", status_code=404, headers=headers)

            except ValueError as ve:
                logging.error(f"ValueError: {ve}")
                return func.HttpResponse("Invalid input. Please provide valid numbers.", status_code=400, headers=headers)
        else:
            logging.error("Missing parameters in the request body.")
            return func.HttpResponse("Please provide 'max_pressure', 'max_sliding_pressure', 'vertical_load_kn', 'x_movement_mm', and 'y_movement_mm' in the request body.", status_code=400, headers=headers)

    except ValueError as e:
        logging.error(f"Invalid JSON input: {e}")
        return func.HttpResponse("Invalid JSON input. Please provide a valid JSON object.", status_code=400, headers=headers)
