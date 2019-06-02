# Estimate tooling cost of a vehicle by summing tooling costs for all major
# components
#
# Inputs:
#  rProp        - Prop/rotor radius [m]
#  cruiseOutput - Structure with cruise performance data
#
# Outputs:
#  toolCostPerVehicle - Estimate of tool cost per vehicle [$]
#
# Functions Called:
#       toolingCost.m

#function toolCostPerVehicle = costBuildup(rProp,cruiseOutput)
import numpy as np
from .tooling_cost import ToolingCost

def CostBuildup(r_prop,c_ref, b_ref):
    # Inputs
    fuselage_width = 1
    fuselage_length = 5
    toc = 0.15  # Wing / canard thickness
    prop_radius = r_prop
    prop_chord = 0.15 * prop_radius
    x_hinge = 0.8
    winglet =  0.2

    parts_per_tool = 1000

    fuselage_height = 1.3 # Guess
    span = b_ref
    chord = c_ref

    # tool_cost_per_vechile = 100 # used as test value

    # Wing Tooling
    wing_tool_cost = np.array([0, 0, 0, 0])
    wing_tool_cost[0] = ToolingCost((span - fuselage_width)/2, toc*chord, chord*0.2) # Leading Edge
    wing_tool_cost[1] = ToolingCost((span - fuselage_width)/2, toc*chord*0.7, chord*0.2) # Aft spar
    wing_tool_cost[2] = ToolingCost((span - fuselage_width)/2, chord*0.75, 0.02)*2 # Upper/Lower skin
    wing_tool_cost[3] = ToolingCost(span, toc*chord, chord*.20) # Forward spar
    wing_tool_cost = 2*(2*sum(wing_tool_cost[0:3])+wing_tool_cost[3]) # Total wing tooling cost (matched tooling)

    # Winglet Tooling
    winglet_tool_cost = np.array([0, 0, 0, 0])
    winglet_tool_cost[0] = ToolingCost(winglet*span/2, toc*chord, chord*.2) # Leading edge
    winglet_tool_cost[1] = ToolingCost(winglet*span/2,toc*chord*0.7,chord*.2) # Aft spar
    winglet_tool_cost[2] = ToolingCost(winglet*span/2,chord*0.75,0.02)*2 # Upper/Lower skin
    winglet_tool_cost[3] = ToolingCost(winglet*span/2,toc*chord,chord*.20) # Forward spar
    winglet_tool_cost = 4*sum(winglet_tool_cost) # Total winglet tooling cost (matched tooling)

    # Canard Tooling
    canard_tool_cost = wing_tool_cost # Total canard tooling cost

    # Fuselage Tooling
    fuselage_tool_cost = np.array([0, 0, 0, 0])
    fuselage_tool_cost[0] = ToolingCost(fuselage_length*.8,fuselage_height,fuselage_width/2)*2 # Right/Left skin
    fuselage_tool_cost[1] = ToolingCost(fuselage_length*.8,fuselage_width/2,fuselage_height/4) # Keel
    fuselage_tool_cost[2] = ToolingCost(fuselage_width,fuselage_height,0.02)*2 # Fwd/Aft Bulkhead
    fuselage_tool_cost[3] = ToolingCost(fuselage_length*.1,fuselage_width,fuselage_height/3) # Nose/Tail cone
    fuselage_tool_cost = 2*sum(fuselage_tool_cost) # Total fuselage tooling cost (matched tooling)

    # Prop Tooling
    prop_tool_cost = np.array([0, 0])
    prop_tool_cost[0] = ToolingCost(prop_radius,prop_chord,prop_chord*toc/2)*2 # Skin
    prop_tool_cost[1] = ToolingCost(prop_radius,prop_chord*toc,prop_chord/4)*2 # Spar tool
    prop_tool_cost = 4*sum(prop_tool_cost) # Total propeller tooling cost (left/right hand) (matched tooling)

    # Control Surface (2 tools)
    control_tool_cost = np.array([0, 0])
    control_tool_cost[0] = ToolingCost((span-fuselage_width)/2,(1-x_hinge)*chord,chord*toc/4) # Skin
    control_tool_cost[1] = ToolingCost((span-fuselage_width)/2,(1-x_hinge)*chord,chord*toc/4) # Skin
    control_tool_cost = 8*sum(control_tool_cost) # Total wing tooling (matched tooling)

    # Total tool cost
    total_tool_cost = wing_tool_cost + canard_tool_cost + fuselage_tool_cost + prop_tool_cost + control_tool_cost + winglet_tool_cost

    tool_cost_per_vechile = total_tool_cost / parts_per_tool

    return tool_cost_per_vechile
    
