from openmdao.api import Problem, Group, IndepVarComp, ExecComp, ScipyOptimizeDriver
from Model.Propulsion.power_comp import PowerComp
from Model.Propulsion.range_comp import RangeComp
from Model.Propulsion.cruise_comp import CruiseComp
from Model.Weight.gross_weight_comp import GrossWeightComp
from Model.Weight.thrust_weight_comp import ThrustWeightComp
from Model.Weight.weight_buildup_comp import EmptyWeightComp


prob = Problem(model=Group())

model = prob.model

ivc = model.add_subsystem('ivc',IndepVarComp(),promotes_outputs = ['*'])

ivc.add_output('Wb',val=600)  #[kg], battery weight
ivc.add_output('Wp',val=454)    #[kg], weight of passangers
#ivc.add_output('We_W0')    # empty to gross fraction

ivc.add_output('m')
ivc.add_output('r')
ivc.add_output('TS',val=188) # ~50% of mach @ Sl
#ivc.add_output('cd0',val=0.0197)
ivc.add_output('rho',val=1.225)

ivc.add_output('V') 
#ivc.add_output('Cd',val=0.03)
#ivc.add_output('Cl',val=0.32)
ivc.add_output('S',val=13.2)
ivc.add_output('AR',val=7)

ivc.add_output('G',val=5)   #climb gradient
ivc.add_output('n',val=1)   # load factor
ivc.add_output('e',val=0)   # oswald efficiency
ivc.add_output('W_S',val=0) # wind loading
ivc.add_output('Neg',val=8) # number of engines 
ivc.add_output('Np',val=4)  # number of people 

# adding subsystems
model.add_subsystem('weight',GrossWeightComp())
model.add_subsystem('FOM',PowerComp())
model.add_subsystem('range',RangeComp())
model.add_subsystem('cruiseP',CruiseComp()) # cruise power
model.add_subsystem('emptyW',EmptyWeightComp())
#model.add_subsystem('T_W',ThrustWeightComp())

# conencting to gross_weights comp
model.connect('Wb','weight.Wb')
model.connect('Wp','weight.Wp')
model.connect('emptyW.We','weight.We')
#model.connect('We/W0','weight.We/W0')

# connecting to empty weight comp
model.connect('AR','emptyW.AR')
#model.connect('Wb','emptyW.Wb')
model.connect('V','emptyW.V')
model.connect('Neg','emptyW.Neg')
model.connect('weight.W0','emptyW.W0')
model.connect('Np','emptyW.Np')


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
model.connect('cruiseP.cd0','FOM.cd0')
model.connect('rho','FOM.rho')
model.connect('TS','FOM.TS')
model.connect('r','FOM.r')

# connecting to cruise power comp
model.connect('weight.W0','cruiseP.W')
#model.connect('Cd','cruiseP.Cd')
#model.connect('Cl','cruiseP.Cl')
model.connect('AR','cruiseP.AR')
model.connect('S','cruiseP.S')
model.connect('V','cruiseP.V')
#model.connect('cd0','cruiseP.cd0')

# connecting to range comp
model.connect('Wb','range.B_W')
model.connect('FOM.PH','range.P_L')
model.connect('cruiseP.P_C','range.P_C')
model.connect('V','range.V')


prob.driver = ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
prob.driver.options['tol'] = 1e-9
prob.driver.options['disp'] = True

model.add_design_var('r',lower=0.7,upper=1)
model.add_design_var('V',lower=67,upper=103)
model.add_design_var('Wb') # proff sees typical of 20-25% gross weight

#model.add_constraint('weight.We_W0',lower=0.45,upper=0.70) # 30% - 70%, from lecture
#model.add_constraint('weight.W0',lower=1700,upper=2000)
model.add_constraint('FOM.FM',lower=0.70,upper=0.80)

model.add_constraint('range.R',equals=340)
model.add_constraint('weight.Wb_W0',lower=0.25,upper=0.30) # batt to gross
#model.add_constraint('FOM.PH',upper=550)
model.add_constraint('cruiseP.P_C',upper=100)
#model.add_constraint('cruiseP.cl',upper=0.4)

model.add_objective('FOM.PH',scaler=-1)

prob.setup()

# Initial Guesses
#prob['We/W0'] = 0.6
prob['r'] = 0.7
prob['V'] = 80


#opt driver
#prob.driver = pyOptSparceDriver()
#prob.driver.options['optimizer'] = "SLSQP"
#prob.driver.hist_file = 'host.hst'


#prob.run_model()
prob.set_solver_print(level=0)
prob.run_driver()
print('Batt Weight',prob['Wb'])
print('Tip Speed',prob['TS'],'[m/s]')
print('Empty Weight Fraction:',prob['weight.We_W0'])
print('Battery Weight Fraction:',prob['weight.Wb_W0'])
print('Empty Weight',prob['emptyW.We'])
print('Gross Weight:',prob['weight.W0'],'[kg]')
print('Figure of Merit:',prob['FOM.FM'])
print('Required Radius:',prob['FOM.r'],'[m]')
print('Required Power for Hover:',prob['FOM.PH'],'[kW]')
print('Required Power for Cruise:',prob['cruiseP.P_C'],'[kW]')
print('Max Trip Range @',prob['V'],'[m/s]:',prob['range.R'],'[km]','Time',prob['range.t'],'[hr]')
print('cl',prob['cruiseP.cl'])
print('cd',prob['cruiseP.cd'])
print('cd0',prob['cruiseP.cd0'])

