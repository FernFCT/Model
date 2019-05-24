from openmdao.api import Problem, Group, IndepVarComp, ExecComp, ScipyOptimizeDriver
from Model.Propulsion.power_comp import PowerComp
from Model.Propulsion.weight_comp import WeightComp
from Model.Weight.gross_weight_comp import GrossWeightComp

prob = Problem(model=Group())

model = prob.model

ivc = model.add_subsystem('ivc',IndepVarComp(),promotes_outputs = ['*'])

ivc.add_output('Wb',val=350.0)  #[kg], battery weight
ivc.add_output('Wp',val=454)    #[kg], weight of passangers
ivc.add_output('We/W0')    # empty to gross fraction

ivc.add_output('m',val=0.0)
ivc.add_output('r',val=0.0)
ivc.add_output('TS',val=170)
ivc.add_output('cd0',val=0.0197)
ivc.add_output('rho',val=1.225)


model.add_subsystem('weight',GrossWeightComp())
model.add_subsystem('FOM',PowerComp())

# conencting to weights group
model.connect('Wb','weight.Wb')
model.connect('Wp','weight.Wp')
model.connect('We/W0','weight.We/W0')

# connecting to Props group
model.connect('weight.W0','FOM.W')
model.connect('cd0','FOM.cd0')
model.connect('rho','FOM.rho')
model.connect('TS','FOM.TS')
model.connect('r','FOM.r')


prob.driver = ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
prob.driver.options['tol'] = 1e-5
prob.driver.options['disp'] = True

model.add_design_var('r',lower=0.5,upper=1.5)
model.add_design_var('We/W0',lower=0.30,upper=0.70) # 30% - 70%, from lecture
model.add_constraint('weight.W0',lower = 1500,upper=2500)
model.add_constraint('FOM.FM',equals=0.80)
model.add_objective('FOM.PH')

prob.setup()

# Initial Guesses
prob['We/W0'] = 0.60
prob['r'] = 1.5


#prob.run_model()
prob.set_solver_print(level=0)
prob.run_driver()
print('Gross Weight Fraction:',prob['We/W0'])
print('Gross Weight:',prob['weight.W0'],'[kg]')
print('Figure of Merit:',prob['FOM.FM'])
print('Required Radius:',prob['FOM.r'],'[m]')
print('Required Power for Hover:',prob['FOM.PH'],'[kW]')

