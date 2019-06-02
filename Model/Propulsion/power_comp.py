from openmdao.api import ExplicitComponent

n = 1 # variable accounting for failed motor and e extra power

class PowerComp(ExplicitComponent):
    
 

    def setup(self):
        self.add_input('W',desc='Weight') # weight
        self.add_input('cd0',desc='zero lift coeff')   # zero lift coeff
        self.add_input('rho',desc='density at SL')
        self.add_input('TS') # tip speed
        self.add_input('r')
        

        self.add_output('FM',val=0.0,desc='Figure of Merit')
        self.add_output('PH',val=0.0,desc='Power for Hover')

        # self.declare_partials('y', 'x')
        self.declare_partials(of='*', wrt='*', method='cs')
        # self.set_check_partial_options('x', method='cs')

    def compute(self, inputs, outputs):
        W = inputs['W']*9.81    # convert to [N]
        r = inputs['r']
        rho = inputs['rho']
        tip_speed = inputs['TS']
        cd0 = inputs['cd0']
        sol = 0.1 


        S = 3.14*(r**2)
        T = n*W/8 # thrust required per motor
        ct = T/( rho *S* (tip_speed**2) )
        cp = ( 1.15*( (ct**(3/2)) /(2**.5) ) + (1/8)*sol*cd0 ) # solidity
        PI = T * ((T/(2*S*rho))**.5)
        PH = cp*rho*S*(tip_speed**3)*.99 
        FM = PI/PH

        outputs['FM'] = FM
        outputs['PH'] = 8*PH/1000





    # def compute_partials(self, inputs, partials):
    #     partials['y', 'x'] = 2.