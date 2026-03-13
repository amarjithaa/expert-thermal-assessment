import math


die_length_mm = 52.5;   die_length = die_length_mm / 1000       
die_width_mm  = 45.0;   die_width  = die_width_mm  / 1000       
die_thick_mm  = 2.2;    die_thick  = die_thick_mm  / 1000       
die_area      = die_length * die_width                          

sink_length_mm = 90.0;  sink_length = sink_length_mm / 1000     
sink_width_mm  = 116.0; sink_width  = sink_width_mm  / 1000     
base_thick_mm  = 2.5;   base_thick  = base_thick_mm  / 1000     
base_area      = sink_length * sink_width                        

n_fins         = 60
fin_thick_mm   = 0.8;   fin_thick   = fin_thick_mm  / 1000      
overall_h_mm   = 27.0;  overall_h   = overall_h_mm  / 1000      
fin_height     = overall_h - base_thick                         
fin_spacing    = (sink_width - (n_fins * fin_thick)) / (n_fins - 1)  

T_ambient  = 25.0      
Q_tdp      = 150.0     

k_Al       = 167.0     
k_TIM      = 4.0       
t_TIM_mm   = 0.1;       t_TIM = t_TIM_mm / 1000  # m

k_air      = 0.0262   
nu_air     = 1.568e-5   
Pr         = 0.71       
V_air      = 1.0       

R_jc = 0.2 


R_TIM = t_TIM / (k_TIM * die_area)



R_cond = base_thick / (k_Al * die_area)

Re = V_air * fin_spacing / nu_air

if Re < 2300:
    Nu = 1.86 * (Re * Pr * (2 * fin_spacing / sink_length)) ** (1/3)
    flow_regime = "Laminar (Sieder-Tate)"
else:
    Nu = 0.023 * Re**0.8 * Pr**0.3
    flow_regime = "Turbulent (Dittus-Boelter)"


h_conv = Nu * k_air / (2 * fin_spacing)


area_single_fin = (2 * fin_height * sink_length) + (fin_thick * sink_length)
area_fins_total = n_fins * area_single_fin
area_base_exposed = (sink_length * sink_width) - (n_fins * fin_thick * sink_length)
A_total = area_fins_total + area_base_exposed

R_conv = 1.0 / (h_conv * A_total)


R_hs = R_cond + R_conv


R_total = R_jc + R_TIM + R_hs


T_junction = T_ambient + Q_tdp * R_total

print("=" * 55)
print("       HEAT SINK THERMAL MODEL - RESULTS")
print("=" * 55)

print("\n--- Geometry ---")
print(f"  Die Area          : {die_area*1e6:.2f} mm²  ({die_area:.6f} m²)")
print(f"  Fin Height        : {fin_height*1000:.2f} mm")
print(f"  Fin Spacing (Sf)  : {fin_spacing*1000:.4f} mm")

print("\n--- Flow Analysis ---")
print(f"  Reynolds Number   : {Re:.4f}")
print(f"  Flow Regime       : {flow_regime}")
print(f"  Nusselt Number    : {Nu:.4f}")
print(f"  h_conv            : {h_conv:.4f} W/m²·K")
print(f"  A_total (conv)    : {A_total:.6f} m²")

print("\n--- Thermal Resistances ---")
print(f"  R_jc              : {R_jc:.6f} °C/W")
print(f"  R_TIM             : {R_TIM:.6f} °C/W")
print(f"  R_cond (base)     : {R_cond:.6f} °C/W")
print(f"  R_conv            : {R_conv:.6f} °C/W")
print(f"  R_hs (cond+conv)  : {R_hs:.6f} °C/W")

print("\n--- FINAL RESULTS ---")
print(f"  R_total           : {R_total:.6f} °C/W")
print(f"  T_junction        : {T_junction:.5f} °C")

print("\n--- Validation vs Excel Reference ---")
print(f"  Excel R_total     : 0.373043 °C/W  | Python: {R_hs:.6f} °C/W")
print(f"  Excel T_junction  : 80.95652 °C    | Python: {T_junction:.5f} °C")
match_R  = abs(R_total - 0.373043) < 0.0001
match_T  = abs(T_junction - 80.95652) < 0.01
print(f"  R_total match     : {'✓ PASS' if match_R else '✗ CHECK'}")
print(f"  T_junction match  : {'✓ PASS' if match_T else '✗ CHECK'}")
print("=" * 55)
