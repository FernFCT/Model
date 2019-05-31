from openmdao.api import Problem, Group, IndepVarComp, ExecComp, ScipyOptimizeDriver
from Model.Propulsion.power_comp import PowerComp
from Model.Propulsion.range_comp import RangeComp
from Model.Propulsion.cruise_comp import CruiseComp
from Model.Weight.gross_weight_comp import GrossWeightComp
# from Model.Weight.thrust_weight_comp import ThrustWeightComp
from Model.costanalysis1.operating_cost import OperatingCost


prob = Problem(model=Group())

model = prob.model

ivc = model.add_subsystem('ivc',IndepVarComp(),promotes_outputs = ['*'])

ivc.add_output('Wb',val=627.0)  #[kg], battery weight
ivc.add_output('Wp',val=454)    #[kg], weight of passangers
ivc.add_output('We/W0')    # empty to gross fraction
ivc.add_output('Wm',val=635.6)  #[kg], motor weight

ivc.add_output('m',val=0.0)
ivc.add_output('r',val=0.0)
ivc.add_output('TS',val=188) # ~50% of mach @ Sl
ivc.add_output('cd0',val=0.0197)
ivc.add_output('rho',val=1.225)

ivc.add_output('V') 
ivc.add_output('Cd',val=0.03)
ivc.add_output('Cl',val=0.32)
ivc.add_output('S',val=13.2)
ivc.add_output('AR',val=7)

ivc.add_output('G',val=5)   #climb gradient
ivc.add_output('n',val=1)   # load factor
ivc.add_output('e',val=0)   # oswald efficiency
ivc.add_output('W_S',val=0) # wind loading

# adding subsystems
model.add_subsystem('weight',GrossWeightComp())
model.add_subsystem('FOM',PowerComp())
model.add_subsystem('range',RangeComp())
model.add_subsystem('cruiseP',CruiseComp()) # cruise power
#model.add_subsystem('T_W',ThrustWeightComp())
model.add_subsystem('cost',OperatingCost())

# conencting to gross_weights comp
model.connect('Wb','weight.Wb')
model.connect('Wp','weight.Wp')
model.connect('We/W0','weight.We/W0')

# connecting to thrustWeightComp
#model.connect('G','T_W.G')
#model.connect('n','T_W.n')
#model.connect('e','T_W.e')
#model.connect('AR','T_W.AR')
#model.connect('cd0','T_W.cd0')
#model.connect('rho','T_W.rho')
#model.connect('W_S','T_W.W_S')
#model.connect('V','T_W.Vc')

# connecting to Props comp
model.connect('weight.W0','FOM.W')
model.connect('cd0','FOM.cd0')
model.connect('rho','FOM.rho')
model.connect('TS','FOM.TS')
model.connect('r','FOM.r')

# connecting to cruise power comp
model.connect('weight.W0','cruiseP.W')
model.connect('Cd','cruiseP.Cd')
model.connect('Cl','cruiseP.Cl')
model.connect('AR','cruiseP.AR')
model.connect('S','cruiseP.S')
model.connect('V','cruiseP.V')
model.connect('cd0','cruiseP.cd0')

# connecting to range comp
model.connect('Wb','range.B_W')
model.connect('FOM.PH','range.P_L')
model.connect('cruiseP.P_C','range.P_C')
model.connect('V','range.V')

# connecting to cost analysis
model.connect('r','cost.r_prop')
model.connect('V','cost.cruise_speed')
model.connect('range.R','cost.avg_dist')
model.connect('We/W0','cost.We/W0')
model.connect('weight.W0','cost.W0')
model.connect('Wb','cost.mass_batt')
model.connect('Wm','cost.mass_motor')
model.connect('S','cost.S')
model.connect('AR','cost.AR')
model.connect('FOM.PH','cost.shaft_power')
model.connect('cruiseP.P_C','cost.P_C')


# Setup optimization algorithm
#prob.driver = pyOptSparseDriver()
#prob.driver.options['optimizer'] = "SLSQP"
#prob.driver.hist_file = 'hist.hst'
prob.driver = ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
prob.driver.options['tol'] = 1e-9
prob.driver.options['disp'] = True

model.add_design_var('r',lower=0.5,upper=1.5)
model.add_design_var('We/W0',lower=0.40,upper=0.70) # 30% - 70%, from lecture
model.add_design_var('V',lower=67,upper=103)



model.add_constraint('FOM.FM',equals=0.80)
model.add_constraint('weight.W0',lower=1700,upper=2500)
model.add_constraint('FOM.PH',upper=500)
model.add_constraint('cruiseP.P_C',upper=90)
model.add_objective('cost.Cost')


prob.setup()

# Initial Guesses
prob['We/W0'] = 0.6
prob['r'] = 1
# guesses from CDR
#BASED ON INITIAL GUESS THE OPTIMZER MIGHT PICK A LOCAL MINIMA INSTEAD OF GLOBAL
prob['AR'] = 7
prob['S'] = 13.2
prob['V'] = 90
prob['Cd'] = 0.03 # not used for calculation but here to run
prob['Cl'] = 0.32 # not used for calculation but here to run
#prob['TS'] = 160



#prob.run_model()
prob.set_solver_print(level=0)
prob.run_driver()
print('Tip Speed',prob['TS'],'[m/s]')
print('Empty Weight Fraction:',prob['We/W0'])
print('Gross Weight:',prob['weight.W0'],'[kg]')
print('Figure of Merit:',prob['FOM.FM'])
print('Required Radius:',prob['FOM.r'],'[m]')
print('Required Power for Hover:',prob['FOM.PH'],'[kW]')
print('Required Power for Cruise:',prob['cruiseP.P_C'],'[kW]')
print('Max Trip Range @',prob['V'],'[m/s]:',prob['range.R'],'[km]','Time',prob['range.t'],'[hr]')
print('Cost per trip: $',prob['cost.Cost'])


