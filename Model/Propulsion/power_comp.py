from openmdao.api import ExplicitComponent


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
        self.declare_partials(of='*', wrt='*', method='fd')
        # self.set_check_partial_options('x', method='cs')

    def compute(self, inputs, outputs):
        W = inputs['W']
        r = inputs['r']
        rho = inputs['rho']
        tip_speed = inputs['TS']
        cd0 = inputs['cd0']


        S = 3.14*(r**2)
        T = W # thrust required
        ct = T/( rho *S* (tip_speed**2) )
        cp = ( 1.15*( (ct**(3/2)) /(2**.5) ) + (1/8)*0.1*cd0 )
        PI = T * ((T/(2*S*rho))**.5)
        PH = cp*rho*S*(tip_speed**3)
        FM = PI/PH

        outputs['FM'] = FM
        outputs['PH'] = PH





    # def compute_partials(self, inputs, partials):
    #     partials['y', 'x'] = 2.