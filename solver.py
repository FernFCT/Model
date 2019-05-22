from openmdao.api import Problem, Group, IndepVarComp, ExecComp, ScipyOptimizeDriver
from Model.Propulsion.power_comp import PowerComp
from Model.Propulsion.weight_comp import WeightComp

prob = Problem(model=Group())

model = prob.model

ivc = model.add_subsystem('ivc',IndepVarComp(),promotes_outputs = ['*'])
#ivc.add_output('PH',val=0.0)
ivc.add_output('m',val=0.0)
ivc.add_output('r',val=0.0)
ivc.add_output('TS',val=170)
ivc.add_output('cd0',val=0.0197)
ivc.add_output('rho',val=1.225)


model.add_subsystem('weight',WeightComp())
model.add_subsystem('FOM',PowerComp())


model.connect('m','weight.m')

model.connect('weight.W','FOM.W')
model.connect('cd0','FOM.cd0')
model.connect('rho','FOM.rho')
model.connect('TS','FOM.TS')
model.connect('r','FOM.r')


prob.driver = ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
prob.driver.options['tol'] = 1e-9
prob.driver.options['disp'] = True

model.add_design_var('r',lower=0.5,upper=1.5)
model.add_constraint('FOM.FM',equals=0.85)
model.add_objective('FOM.PH')

prob.setup()

prob['m'] = 2500
prob['r'] = 1.5


#prob.run_model()
prob.set_solver_print(level=0)
prob.run_driver()
print('Figure of Merit:',prob['FOM.FM'])
print('Required Radius:',prob['FOM.r'])
