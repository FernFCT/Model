from openmdao.api import ExplicitComponent
from .costanalysis.cost_buildup import CostBuildup

class OperatingCost(ExplicitComponent):


    def setup(self):
        self.add_input('r_prop', desc='Radius Propeller [m]')   # 1 
        self.add_input('cruise_speed', desc='Cruise Speed [m/s]')   # 102.82
        self.add_input('avg_dist', desc='Average Distance of trip [m]') # 193121
        self.add_input('shaft_power', desc='Shaft Power [kW]' ) # 156
        self.add_input('We/W0', desc = 'Empty Weight Fraction')
        self.add_input('W0', desc = 'Gross Weight')
        #self.add_input('mass_struct', desc='Mass of Structure [kg]')    # 180
        self.add_input('mass_batt', desc='Mass of Battery [kg]')    # 627.66
        self.add_input('mass_motor',desc = 'Mass of Motor [kg]')    # 635.8
        #self.add_input('b_ref', desc= 'Span of one wing [m]') # 13.21 / 2
        #self.add_input('c_ref', desc= 'Ref Chord [m]') # 1 
        self.add_input('S', desc = 'Wing Reference Area (both) [m^2]')
        self.add_input('AR', desc = 'Aspect Ratio')
        self.add_input('P_C', desc= 'Power at Cruise [kW]') # power to weight 0.22

        self.add_output('Cost', desc = 'Cost per trip [$]')

        self.declare_partials(of='*', wrt='*', method='fd')

    def compute(self, inputs, outputs):

        r_prop = inputs['r_prop']
        cruise_speed = inputs['cruise_speed']
        avg_dist = inputs['avg_dist']
        shaft_power = inputs['shaft_power']
        mass_struct = inputs['We/W0']*inputs['W0'] - inputs['mass_motor']
        mass_batt = inputs['mass_batt']
        mass_motor = inputs['mass_motor']
        S_single = inputs['S']/2
        b_ref = (inputs['AR'] * S_single)**0.5
        c_ref = S_single / b_ref
        power_to_weight = inputs['P_C'] / inputs['W0']

        # Assumptions
        flight_hours_per_year = 600
        flight_time = avg_dist/cruise_speed
        flights_per_year = flight_hours_per_year / (flight_time / 3600)
        vehicle_life_years = 10
        n_vehicles_per_facility = 200

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

        outputs['Cost'] = cost_per_flight

