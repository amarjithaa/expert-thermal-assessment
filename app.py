from flask import Flask, request, jsonify
app = Flask(__name__)

def compute_thermal_model(params):

    die_length  = params.get("die_length_mm",  52.5)  / 1000
    die_width   = params.get("die_width_mm",   45.0)  / 1000
    base_thick  = params.get("base_thick_mm",   2.5)  / 1000
    sink_length = params.get("sink_length_mm", 90.0)  / 1000
    sink_width  = params.get("sink_width_mm", 116.0)  / 1000
    n_fins      = params.get("n_fins",          60)
    fin_thick   = params.get("fin_thick_mm",    0.8)  / 1000
    overall_h   = params.get("overall_height_mm", 27.0) / 1000
    t_TIM       = params.get("tim_thickness_mm", 0.1) / 1000
    Q           = params.get("tdp_w",          150.0)
    T_amb       = params.get("t_ambient_c",     25.0)
    R_jc        = params.get("r_jc",             0.2)

    k_Al   = params.get("k_al",   167.0)
    k_TIM  = params.get("k_tim",    4.0)
    k_air  = params.get("k_air",  0.0262)
    nu_air = params.get("nu_air", 1.568e-5)
    Pr     = params.get("prandtl", 0.71)
    V_air  = params.get("v_air",   1.0)

    die_area    = die_length * die_width
    fin_height  = overall_h - base_thick
    fin_spacing = (sink_width - (n_fins * fin_thick)) / (n_fins - 1)

    R_TIM = t_TIM / (k_TIM * die_area)

    R_cond = base_thick / (k_Al * die_area)

    Re = V_air * fin_spacing / nu_air
    if Re < 2300:
        Nu = 1.86 * (Re * Pr * (2 * fin_spacing / sink_length)) ** (1 / 3)
        flow_regime = "Laminar"
    else:
        Nu = 0.023 * Re ** 0.8 * Pr ** 0.3
        flow_regime = "Turbulent"

    h_conv = Nu * k_air / (2 * fin_spacing)

    area_single_fin   = (2 * fin_height * sink_length) + (fin_thick * sink_length)
    area_fins_total   = n_fins * area_single_fin
    area_base_exposed = (sink_length * sink_width) - (n_fins * fin_thick * sink_length)
    A_total = area_fins_total + area_base_exposed

    R_conv = 1.0 / (h_conv * A_total)
    R_hs   = R_cond + R_conv
    R_total = R_jc + R_TIM + R_hs
    T_junction = T_amb + Q * R_total

    return {
        "inputs": {
            "die_area_m2":        round(die_area, 6),
            "fin_height_mm":      round(fin_height * 1000, 4),
            "fin_spacing_mm":     round(fin_spacing * 1000, 4),
            "tdp_w":              Q,
            "t_ambient_c":        T_amb,
        },
        "flow": {
            "reynolds_number":    round(Re, 4),
            "flow_regime":        flow_regime,
            "nusselt_number":     round(Nu, 4),
            "h_conv_W_m2K":       round(h_conv, 4),
            "A_total_m2":         round(A_total, 6),
        },
        "resistances_degC_per_W": {
            "R_jc":   round(R_jc,    6),
            "R_TIM":  round(R_TIM,   6),
            "R_cond": round(R_cond,  6),
            "R_conv": round(R_conv,  6),
            "R_hs":   round(R_hs,    6),
            "R_total":round(R_total, 6),
        },
        "results": {
            "T_junction_degC": round(T_junction, 5),
        },
    }



@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "api": "Heat Sink Thermal Model API",
        "endpoints": {
            "GET  /health":   "Health check",
            "GET  /default":  "Run model with reference design values",
            "POST /calculate":"Run model with custom parameters (JSON body)",
        }
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/default", methods=["GET"])
def default():
    """Run model with all reference design defaults."""
    result = compute_thermal_model({})
    return jsonify({"status": "success", "data": result})


@app.route("/calculate", methods=["POST"])
def calculate():
    """
    Run model with custom parameters.
    Send a JSON body with any subset of parameters to override defaults.
    Example:
        { "tdp_w": 200, "v_air": 2.0, "n_fins": 80 }
    """
    try:
        params = request.get_json(force=True) or {}
        result = compute_thermal_model(params)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
