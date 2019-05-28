from openmdao.api import ExplicitComponent

rho = 1.225 #density, [kg/m**3]


class   WeightComp(ExplicitComponent):  

   
    def setup(self):
        self.add_input('W',desc='Weight of aircraft')
        self.add_input('Cd',desc='coefficient of drag')
        self.add_input('Cl',desc='coefficient of lift')
        self.add_input('AR',desc='Aspect Ratio')
        self.add_input('S',desc='Refernce Area')
        self.add_input('V',desc='Airspeed')

        self.add_output('P_C',desc='Power required for cruise')

        self.declare_partials(of='*', wrt='*', method='fd')

      

    def compute(self,inputs,outputs):
        outputs['P_C'] = (( (2*(inputs['W']**3)*(inputs['Cd']**2))/(inputs['S']*rho*(inputs['Cl']**3)) )**.5)/1000