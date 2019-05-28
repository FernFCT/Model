# Estimate direct operating costs per flight including: acquisition cost,
# insurance cost, operating facility cost, energy cost, and maintenance. 
#
# Inputs:
#  rProp        - Propeller or rotor radius [m]
#  cruiseSpeed  - Cruise Speed [m/s]
#  avgDist      - Nominal trip distance [m]
#  shaftPower   - [kW]
#  mass         - Maximum takeoff mass [kg]
#                 structure w/ mass.structural, mass.battery, mass.motors
#  instead use: massStruct, massBatt, massMotor
#  cruiseOutput - Structure containing cruise performance outputs
#                 structure w/ span = .bRef, chord = .cRef
#  instead use: bRef, cRef
#  powerToWeight- power to weight ratio [kW / kg]
# Functions Called
#               costBuildup - calculate tooling cost
# Outputs:
#  C - Operating cost per flight [$]
# Data to check:
#   cost of material/kg
#   cost of battery ($/kW-hr)
#   cost of motor ($1500 for 10 kg motor) (check data here)
#   cost of servo ($800 each)
#   avionics cost = $30,000
#   energy cost [$ per kW-hr], check for in LA
#   2000 battery life cycles
#   6000 motor life hours
#   6000 servo life hours
# Assumed inputs
#   600 flight hours per year (w/ flight time, calc flights per year)
#   10 vehicle life years
#   200 vehicles per facility

# From PDR:
#   rProp = 1m, cruiseSpeed = 102.82 m/s, avgDist = 193121 m, 
#   shaftPower = 156, mass.structural = 819, mass.battery = 627.66, mass.motors = 635.8
#   cruiseOutput.bRef = 13.21 m, cruiseOutput.cRef = 1 m, powerToWeight = 0.22 kW/kg
# mass.structural = 819; mass.battery = 627.66; mass.motors = 635.8;
# cruiseOutput.bRef = 13.21; cruiseOutput.cRef = 1;
# [C] = operatingCost(1,102.82,193121,156,mass,cruiseOutput,0.22);

#def operatingCost2( r_prop, cruise_speed, avg_dist, shaft_power, mass_struct, mass_batt, mass_motor, b_ref, cRef, power_to_weight ):
# function inputs
r_prop = 1
cruise_speed = 102.82 
avg_dist = 193121
shaft_power = 156
mass_struct = 180
mass_batt = 627.66
mass_motor = 635.8
b_ref = 13.21
c_ref = 1
power_to_weight = 0.22

from costanalysis.CostBuildup import CostBuildup

# Assumptions
flight_hours_per_year = 600
flight_time = avg_dist/cruise_speed
flights_per_year = flight_hours_per_year / (flight_time / 3600)
vehicle_life_years = 10
n_vehicles_per_facility = 200


# def CostBuildup( r_prop,c_ref, b_ref ):
#     # Inputs
#     fuselage_width = 1
#     fuselage_length = 5
#     toc = 0.15  # Wing / canard thickness
#     prop_radius = r_prop
#     prop_chord = 0.15 * prop_radius
#     x_hinge = 0.8
#     winglet =  0.2

#     parts_per_tool = 1000

#     fuselage_height = 1.3 # Guess
#     span = b_ref
#     chord = c_ref

#     tool_cost_per_vechile = 100

#     return tool_cost_per_vechile

# Tooling Cost
tool_cost_per_vehicle = CostBuildup(r_prop,b_ref, c_ref)

# Material Cost
material_cost_per_kg = 220
material_cost = material_cost_per_kg * mass_struct
# Battery Cost
power_to_weight_hr = power_to_weight * flight_time / 3600
battery_cost_per_kg = 700 * power_to_weight_hr   # Roughly $700/kW-hr * P/W [kW-hr /kg]
battery_cost = battery_cost_per_kg * mass_batt
# Motor Cost
motor_cost_per_kg = 150   # Approx $1500 for 10 kg motor +  controller ?
motor_cost = motor_cost_per_kg * mass_motor

# Servo cost
n_servo = 14   # 8 props, 4 surfaces, 2 tilt
servo_cost = n_servo * 800 # Estimate $800 per servo in large quantities

# Avionics cost
avionics_cost = 30000

# BRS (Ballistics Recovery System) cost
BRS_cost = 5200

# Total acquisition cost
acquisition_cost = battery_cost + motor_cost + servo_cost + avionics_cost + BRS_cost + material_cost + tool_cost_per_vehicle
acquisition_cost_per_flight = acquisition_cost/(flights_per_year * vehicle_life_years)

# Insurance Cost
# Follow R22 for estimate of 6.5# of acquisition cost
insurance_cost_per_year = acquisition_cost * 0.065
insurance_cost_per_flight = insurance_cost_per_year/flights_per_year

# Facility rental cost
vehicle_footprint = 1.2 * (8 * r_prop + 1) * (4 * r_prop + 3); # m^2, 20# for movement around aircraft for maintenance, etc.
area_cost = 10.7639 * 2 * 12; # $/m^2, $2/ft^2 per month assumed

# Facility Cost = Vehicle footprint + 10x footprint for operations
# averaged over # of vehicles at each facility
facility_cost_per_year = (vehicle_footprint + 10*vehicle_footprint/n_vehicles_per_facility) * area_cost
facility_cost_per_flight_hour = facility_cost_per_year/flight_hours_per_year
facility_cost_per_flight = facility_cost_per_flight_hour * flight_time / 3600

# Electricity Cost
# E * $/kWhr including 90# charging efficiency
# Average US electricity cost is $0.12 per kW-hr, up to $0.20 per kW-hr in CA
E = shaft_power * flight_time / 3600
energy_cost_per_flight = 0.12 * E / 0.9

# Battery Replacement Cost
batt_life_cycles = 2000
battery_repl_cost_per_flight = battery_cost/batt_life_cycles

# Motor Replacement Cost
motor_life_hrs = 6000
motor_repl_cost_per_flight = flight_time / 3600 / motor_life_hrs * motor_cost

# Servo Replacement Cost
servo_life_hrs = 6000
servo_repl_cost_per_flight = flight_time / 3600 / servo_life_hrs * servo_cost

# Maintenace Cost
human_cost_per_hour = 60
man_hr_per_flight_hour = 0.10 # periodic maintenance estimate
man_hr_per_flight = 0.2 # Inspection, battery swap estimate
labor_cost_per_flight = (man_hr_per_flight_hour * flight_time / 3600 + man_hr_per_flight) * human_cost_per_hour

# Cost Per Flight
cost_per_flight = acquisition_cost_per_flight + insurance_cost_per_flight + facility_cost_per_flight + \
energy_cost_per_flight + battery_repl_cost_per_flight + motor_repl_cost_per_flight + \
servo_repl_cost_per_flight + labor_cost_per_flight

print('Cost Per Flight: $', cost_per_flight*1000)
#   return [C]


   