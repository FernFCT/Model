from openmdao.api import ExplicitComponent

B_density = 400     # [Wh/kg]
FAA = 0.5           # [hr], flight time required by FAA for emergency
LO_time = 90/3600   # [hr], time to reach cruise alt
res = 0.80          # 20% battery reserve for healthy and happy battery :)
class   RangeComp(ExplicitComponent):  

   
    def setup(self):
        self.add_input('B_W',desc='Battery Weight')
        self.add_input('P_L',desc='Power Required @ Liftoff')
        self.add_input('P_C',desc='Power Required  @ Cruise')
        self.add_input('V',desc='Speed flying @ cruise')

        self.add_output('R',desc='Max Range W/Reserve & Emergency 30min')
        self.add_output('t',desc='Time flying @ max range')

        self.declare_partials(of='*', wrt='*', method='fd')

    def compute(self,inputs,outputs):
        LO_Wh = inputs['P_L']*LO_time*1000  # Energy spent on liftoff
        time = ( (B_density*inputs['B_W']*res)-LO_Wh-(LO_Wh/2) ) / (1000*inputs['P_C'])
        dist = (time-FAA)*inputs['V']*3.6   #conversion from [m/s]->[kph]

        outputs['R'] = dist
        outputs['t'] = time