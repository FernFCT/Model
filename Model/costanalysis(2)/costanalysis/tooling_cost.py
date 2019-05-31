# Estimates tooling cost based on part dimensions including material, rough
# machining, and finishing machining
#
# Inputs:
# length - part length [m]
# width  - part width [m]
# depth  - part depth [m]
#
# Output:
# cost - Tool cost [$]
#
import math 

def ToolingCost(length, width, depth):
    # Material
    tool_side_offset = 0.09 # Offset on each side of tool
    tool_depth_offset = 0.03 # Offset at bottom of tool
    tool_cost = 10000 # Cost be m^3 of tooling material [$/m^3]

    tool_volume = (length + 2 * tool_side_offset) * (width + 2 * tool_side_offset) * (depth + tool_depth_offset)
    material_cost = tool_cost * tool_volume # Tooling material costs

    # Machining (Rough Pass)
    rough_SFM = 200 # Roughing surface feet per minute
    rough_FPT = 0.003 # Roughing feed per tooth [in]
    rough_cost_rate = 150/3600 # Cost to rough [$/s]
    rough_bit_diam = 0.05 # Rougher diameter [m]

    rough_bit_depth = rough_bit_diam/4 # Rougher cut depth [m]
    rough_RPM = 3.82 * rough_SFM / (39.37 * rough_bit_diam) # Roughing RPM
    rough_feed = rough_FPT * rough_RPM * 2 * 0.00042 # Roughing Feed [m/s]
    rough_bit_step = 0.8 * rough_bit_diam # Rougher step size

    cut_volume = length * math.pi * depth * width / 4 # Amount of material to rough out
    rough_time = cut_volume / (rough_feed * rough_bit_step * rough_bit_depth) # Time for roughing
    rough_cost = rough_time * rough_cost_rate # Roughing cost

    # Machining (Finish Pass)
    finish_SFM = 400 # Roughing surface feet per minute
    finish_FPT = 0.004 # Roughing feed per tooth [in]
    finish_cost_rate = 175/3600 # Cost to finish [$/s]
    finish_bit_diam = 0.006 # Finish diameter [m]
    finish_passes = 5 # Number of surface passes

    finish_RPM = 3.82 * finish_SFM / (39.37 * finish_bit_diam) # Roughing RPM
    finish_feed = finish_FPT * finish_RPM * 2 * 0.00042 # Roughing Feed [m/s]

    def EllipsePerimeter(a, b):
        h = (a - b)**2 / (a + b)**2
        p = math.pi*(a+b)*(1+3*h/(10+(4-3*h)**0.5))
        return p

    finish_bit_step = 0.8 * finish_bit_diam # Rougher step size
    cut_area = length * EllipsePerimeter(width/2,depth)/2; # Amount of material to rough out
    finish_time = cut_area / (finish_feed * finish_bit_step) * finish_passes; # Time for roughing
    finish_cost = finish_time * finish_cost_rate; # Roughing cost

    # Total Cost
    cost = material_cost + rough_cost + finish_cost
    
    return cost

