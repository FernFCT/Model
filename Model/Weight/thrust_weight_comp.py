import numpy as np 
from openmdao.api import ExplicitComponent

class ThrustWeightComp(ExplicitComponent):

    def setup(self):
        self.add_input('G',desc = 'climb gradient')
        self.add_input('n',desc = 'load factor')
        self.add_input('e',desc = 'oswald efficieny')
        self.add_input('AR',desc = 'aspect ratio')
        self.add_input('cd0',desc = 'parasitic drag')
        self.add_input('rho',desc = 'density')
        self.add_input('W_S',desc = 'Wing Loading')
        self.add_input('Vc',desc = 'Cruise Speed')

        self.add_output('T_W_climb',desc = 'Thrust-to-Weight ratio climb')
        self.add_output('T_W_cruise',desc = 'Thrust-to-Weight ratio cruise')
        self.add_output('T_W_maneuver',desc = 'Thrust-to-Weight ratio maneuver')
                       
        self.declare_partials(of = '*', wrt = '*', method = 'cs')

    def compute(self,inputs,outputs):
        q = 0.5*inputs['rho']*inputs['Vc']*inputs['Vc']
        twclimb = inputs['G'] + (inputs['W_S']/(np.pi*inputs['e']*inputs['AR']*q)) + (inputs['cd0']*q/(inputs['W_S']))
        cl = 2*inputs['W_S']/(inputs['rho']*inputs['Vc']*inputs['Vc'])
        cd = inputs['cd0'] + (1/(np.pi*inputs['e']*inputs['AR']))*cl*cl
        twcruise = (cl/cd)**(-1)
        twmaneuver = (inputs['cd0']*q/(inputs['W_S'])) + (inputs['n']*inputs['n'])*(inputs['W_S']/(np.pi*inputs['e']*inputs['AR']*q))

        outputs['T_W_climb'] = twclimb
        outputs['T_W_cruise'] = twcruise
        outputs['T_W_maneuver'] = twmaneuver