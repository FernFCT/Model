from openmdao.api import ExplicitComponent
import numpy as np

class EmptyWeightComp(ExplicitComponent):
    # Coefficients
    

    def setup(self):
        self.add_input('AR',desc='aspect ratio')
        #self.add_input('Wb',desc='battery weight')
        self.add_input('V',desc='cruise speed')
        self.add_input('Neg',desc='number of engines')
        self.add_input('W0',desc='gross weight')
        self.add_input('Np',desc='number of people')
        
        self.declare_partials(of='*', wrt='*', method='cs')
        self.add_output('We',desc='empty weight')
        

    def compute(self, inputs, outputs):

        #Wb = inputs['Wb']*2.205
        AR = inputs['AR']   
        Np = inputs['Np']
        V = inputs['V']*3.281     # convert to american
        t_c = 0.12          # thickness to chord ratio
        L_f =  21.33               # Fuselage structural length [ft]
        Lm = 5              # lenth of main landing gear [in]
        Neg = inputs['Neg'] # number of engines
        Nl = 1               # ultimate landing gear factor
        Nz = 3.9            # ultimate load factor
        q = 0.5*0.002377*(V**2)  # dynamic pressure at cruise
        Sf = 362.744               # fuselage wetted area
        Sw = 142.233               # trapezoidal wing area
        Wdg = inputs['W0']*2.2046              # gross weight
        Wen = 110              # engine weight each [lb]
        Wl = Wdg            # langing gross weight
        #Wuav = 800          # usual 800-1400
        M = V/1116.13       # mach
        L_D = 15.35             # lift over drag
        B_w = 31.5             # wing span

        #wing
        W_w = 0.036*(Sw**0.758)*(AR**0.86)*(q**0.006)*((100*t_c)**(-0.3))*((Nz*Wdg)**0.49)
        # fuselage
        W_f = 0.052*(Sf**1.086)*((Nz*Wdg)**0.22)*(L_f**(-0.051))*((L_D)**(-0.072))*(q**0.241)
        # landing gear
        W_lg = 0.095*((Nl*Wl)**0.768)*((Lm/12)**0.845)
        # installed engine
        W_ie = 2.575*(Wen**0.922)*(Neg)
        # flight controls
        W_fc = 0.053*(L_f**1.536)*(B_w**0.371)*((Nz*Wdg*10**(-4))**0.8)
        # hydraulics
        W_h = 0.001*Wdg
        # avionics
        W_av = 33 # vahana avionics = 15 kg = 33.069 lb
        # electrical
        W_el = 12.57*(W_av)**0.51
        # air conditioning
        W_ac = 0.265*Wdg**0.52*Np**0.68*W_av**0.17*M**0.08
        # furnishings 
        W_fur = 0.0582*Wdg - 65
        # actuators
        # 12 actuators, 0.65 kg each
        W_act = 12*1.43
        
        We = 0.8*(W_w + W_f + W_lg + W_ie + W_fc + W_h + W_av + W_el + W_ac + W_fur + W_act)/2.205
        #print('weight',We)
        outputs['We'] = We  # outputs kg
        


   
        