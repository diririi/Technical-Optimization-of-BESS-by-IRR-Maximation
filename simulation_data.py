# Output variables of program

# import library
import numpy as np

# main class of structure
class simulation_data:

    def __init__(self):

        """Initialization of all class variables. This class contains output variables."""

        # simulation: main output vectors: SOC, operation, revenue

        self.SOC_sim = np.full(0, 0, dtype=float)               # state of charge during simulation period for each timestamp; initial = 0; 0 % at Q_u; 100 % at 0; the real state of charge is different because it relates to Q_N which degradetes during time. the real SOC can be recalculated from SOC sim
        self.real_operation = np.full(0,"0",dtype=object)       # real operation of BESS with market of each timestamp used during operation period; other events like outages or curtailments are indicated as well
        self.revenue = np.full(0, 0,dtype=float)                # revenue with + = positive revenue and - = negative in case of penalties for each timestamp of the operation period
        

        # sorted numbered vectors of nominal best prices of each matrix. Best price element = 0, second best price 1 ...
        
        self.sorted_charge = np.full(0, 0,dtype=int)            # for charging best price numberation; to calculate future_revenue
        self.sorted_discharge = np.full(0, 0,dtype=int)         # for discharging best price numberation; to calculate future_revenue
        self.sorted_reserve = np.full(0, 0,dtype=int)           # for reserve power best price numberation; to calculate future_revenue


        # neglecting the real operation checks of e.g. curtailments, the following include the final planned values which are traded on the markets
        
        self.real_plan_operation = np.full(0,"0",dtype=object)      # saved outputs of function: generate_real_plan; variable: future_market as variable over the calculation period
        self.real_plan_energy = np.full(0, 0,dtype=float)           # saved outputs of function: generate_real_plan used_capacity_temp as variable over the calculation period: usable SOC equivalent

        
        # degradation variables
        
        self.average_SOC = float(50)        # in %      # average state of charge (relative to Q_N)
        self.average_Q_d = float(0)         # in MWh    # average discharged capacity
        self.Qd = float(0)                  # in MWh    # discharged capacity; calculated from usable SOC vector
        self.nominal_capacity = float(0)    # in MWh    # nominal capacity over total calculation period, also valid for each replacement
        self.degradation = float(0)         # in %      # of QN at the end of each replacement period and the projects end
        self.nominal_power = float(0)       # in MW     # nominal power over total calculation period, also valid for each replacement
        self.corrected_DOD = float(0)       # in %      # average DOD; if DOD was choosen too low by user; the DOD will be corrected accordingly to degradation; this variable contains the valid average DOD in every case
        self.corrected_P_loss = float(0)    # in %      # power loss of the battery (almost neglectible)
        

        # variables converted to replacement period for output

        self.system_RTE_replacement  = np.full(0, 0,dtype=float)    # system RTE from inda converted to replacement period: each replacement the system RTE will improve
        self.capex_kWh_replacement  = np.full(0, 0, dtype=float)    # capacity-dependent capex from inda converted to replacement period: each replacement the capacity-dependent capex will be less due to learning effect
        

        # financial variables

        self.annual_costs = np.full(0, 0, dtype=float)          # in €      # all costs of the calculation period in annual resolution
        self.annual_revenue = np.full(0, 0, dtype=float)        # in €      # annual sum of revenue function
        self.cashflow = np.full(0, 0, dtype=float)              # in €      # annual sum of revenue - costs
        self.IRR = float(0)                                     # in %      # main financial result; internal rate of return
        self.NPV = float(0)                                     # in €      # net present value
        self.count_cycles = float(0)                            # no unit   # amount of full cycles each replacement period as average
       
        
        # helping variables

        self.last_plan_outage_considered = False                # no unit   # if there is an outage & the BESS cant meet plan operation, it must pay penatly. But only for the markets booked this loop. If the outage continue to next loop, no markets will be reservated in real, so there is no penalty for these
        self.annual_production = np.full(0, 0, dtype=float)     # in MWh    # annual sum of released power of storage
        self.annual_consumption = np.full(0, 0, dtype=float)    # in MWh    # annual sum of consumed power of storage
        self.SOC_error = int(0)                                 # no unit   # if there is an error in the calculation part of a SOC border violated, its indicated here. If the variables is 0 in the end, there is no SOC error.


       