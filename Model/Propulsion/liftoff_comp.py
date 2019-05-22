from openmdao.api import IndepVarComp, Group, Problem, ExecComp, ScipyOptimizeDriver
import numpy as np
# should get like .81
prob = Problem()
prob.model = model = Group()

model.add_subsystem('Radius', IndepVarComp('r', 1)) # radius 
model.add_subsystem('T_S', IndepVarComp('tip_speed', 170))  #SOS @ SL * Mach. Mach = 0.5 for noise
model.add_subsystem('Weight', IndepVarComp('W', 24525))  #[N]
model.add_subsystem('Zero_L', IndepVarComp('cd0', 0.0197))
model.add_subsystem('density', IndepVarComp('rho', 1.225))  # density @ Sl


model.add_subsystem('Thrust', ExecComp('T = W/8'))  # thrust req per propeller
model.add_subsystem('Disk_Area', ExecComp('S = 3.14*(r**2)'))
model.add_subsystem('T_C', ExecComp('ct = T/( rho *S* (tip_speed**2) )'))
model.add_subsystem('P_C', ExecComp('cp = ( 1.15*( (ct**(3/2)) /(2**.5) ) + (1/8)*0.1*cd0 )')) # power coefficient
model.add_subsystem('P_I', ExecComp('PI = T * ((T/(2*S*rho))**.5)'))
model.add_subsystem('P_H', ExecComp('PH = cp*rho*S*(tip_speed**3)'))
model.add_subsystem('F_merit', ExecComp('FM = PI/PH'))

model.connect('Zero_L.cd0', 'P_C.cd0') # con cd0 to pc
model.connect('Weight.W', 'Thrust.W') # connecting weight to thrust calc
model.connect('Radius.r', 'Disk_Area.r') # connecting radius to disk calc
model.connect('Thrust.T', ['T_C.T','P_I.T' ]) # connecting the thrust to eqs that need it
model.connect('Disk_Area.S', ['T_C.S','P_I.S','P_H.S' ]) # connecting area to things
model.connect('T_S.tip_speed', ['T_C.tip_speed','P_H.tip_speed' ]) # connecting tip speed
model.connect('density.rho', ['T_C.rho','P_I.rho','P_H.rho' ]) # con rho
model.connect('T_C.ct', 'P_C.ct') # ct to P_C
model.connect('P_C.cp', 'P_H.cp')
model.connect('P_I.PI','F_merit.PI')
model.connect('P_H.PH','F_merit.PH')

# Optimization Stuff
prob.driver = ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
prob.driver.options['tol'] = 1e-9
prob.driver.options['disp'] = True

model.add_design_var('Radius.r', lower=0.70, upper=1)
model.add_objective('density.rho',scaler=-1) # random obj to force it to run
model.add_constraint('F_merit.FM',equals=0.85) 
#add constraint for minimum power???????


prob.setup()
print('Running Optimizer')
prob.set_solver_print(level=0)
prob.run_driver()

print('Figure of Merit')
print(prob['F_merit.FM'])
print('Radius [m]')
print(prob['Radius.r'])
print('Power Required for liftoff [kW]')
print(8*prob['P_H.PH']/1000)