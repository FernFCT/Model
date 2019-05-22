from openmdao.api import ExplicitComponent

#def initialize(self):
class   WeightComp(ExplicitComponent):  

   
    def setup(self):
        self.add_input('m')
        self.add_output('W')

        #self.declare_partials('*','*')

    def compute(self,inputs,outputs):
        outputs['W'] = inputs['m']*9.81