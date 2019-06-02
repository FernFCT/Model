from openmdao.api import ExplicitComponent


class GrossWeightComp(ExplicitComponent):
    # Coefficients
    

    def setup(self):
        self.add_input('Wp')   # weight of payload (passangers)
        self.add_input('Wb')   # weight of battery
        self.add_input('S',desc='lifting surface')
        #self.add_input('We/W0')   # empty over gross
        self.add_input('We',desc='empty weight')
        self.add_output('W0') # gross weight
        self.add_output('We_W0') # gross weight
        self.add_output('Wb_W0') # gross weight
        self.add_output('W_S')
        self.declare_partials('*', '*')
        self.declare_partials(of='*', wrt='*', method='cs')

    def compute(self, inputs, outputs):
        Wp = inputs['Wp']
        Wb = inputs['Wb']
        We = inputs['We']
        #We_W0 = inputs['We']/inputs['W0']
        W0 = (Wp + Wb + We) 
        outputs['We_W0'] = We/W0
        outputs['Wb_W0'] = Wb/W0
        outputs['W0'] = W0
        outputs['W_S'] = W0/inputs['S']
        
    #def compute_partials(self, inputs, partials):
        #Wp = inputs['Wp']
        #Wb = inputs['Wb']
        #We_W0 = inputs['We']/inputs['W0']
        #partials['W0', 'Wp'] = 1. / (1 - We_W0)
        #partials['W0', 'Wb'] = 1. / (1 - We_W0)
        #artials['W0', 'We/W0'] = (Wp + Wb) / (1 - We_W0) ** 2