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
model.add_subsystem('Fig',PowerComp())


model.connect('m','weight.m')

model.connect('weight.W','Fig.W')
model.connect('cd0','Fig.cd0')
model.connect('rho','Fig.rho')
model.connect('TS','Fig.TS')
model.connect('r','Fig.r')


prob.driver = ScipyOptimizeDriver()

model.add_design_var('r', lower=0.5, upper=1)
model.add_constraint('Fig.FM',equals=0.85)
model.add_objective('rho',scaler=-1)

prob.setup()

prob['m'] = 2500
prob['r'] = 0.9


#prob.run_model()
prob.run_driver()
print(prob['Fig.FM'])
print(prob['Fig.r'])
#print(prob['PH'])