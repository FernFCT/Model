from openmdao.api import ExplicitComponent

rho = 1.225 #density, [kg/m**3]


class   CruiseComp(ExplicitComponent):  

   
    def setup(self):
        self.add_input('W',desc='Weight of aircraft')
        self.add_input('Cd',desc='coefficient of drag')
        self.add_input('Cl',desc='coefficient of lift')
        self.add_input('AR',desc='Aspect Ratio')
        self.add_input('S',desc='Refernce Area')
        self.add_input('V',desc='Airspeed')
        self.add_input('cd0',desc='zero lift drag')

        self.add_output('P_C',desc='Power required for cruise')

        self.declare_partials(of='*', wrt='*', method='fd')

      

    def compute(self,inputs,outputs):
        W = inputs['W']*9.81 
        # add Cl & Cd if airfoil code doesnt work
        cl = 2*W/(rho*(inputs['V']**2)*inputs['S'])
        k = 1/(3.14*0.8*inputs['AR']) # e = 0.8
        cd = inputs['cd0'] + k*cl**2
        #outputs['P_C'] = (( (2*(W**3)*(inputs['Cd']**2))/(inputs['S']*rho*(inputs['Cl']**3)) )**.5)/1000
        outputs['P_C'] = (( (2*(W**3)*(cd**2))/(inputs['S']*rho*(cl**3) ))**.5)/1000