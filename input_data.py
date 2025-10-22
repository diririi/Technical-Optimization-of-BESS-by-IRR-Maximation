# Here all input variables of the user are stored and in the second process turned into simulation values

# import library
import numpy as np

# create main class
class input_data:

    def __init__(self):

        """Initialization of all class variables. This class contains input and process variables."""

        # user defined variables are with default initialized
        self.start_simulation = False                       # no unit      # indicates if the simulation is active or not; will be true after all user inputs         
        self.technology_storage_system = "Li-Ion (LFP)"     # no unit      # technology of the storage system. Allowed are: "Li-Ion (NMC)" and "Li-Ion (LFP)" // later: "Li-Ion (NCA)"  "Li-Ion (LTO)" can be added
        self.year_commissioning = 2027                      # no unit      # year of commissioning
        self.calculation_period = 20                        # a            # calculation period of the BESS
        self.replacement_period = 10                        # a            # replacement period of the capacity unit of the BESS
        self.intraday_active = False                        # no unit      # marketing strategy: sell electricity on Intraday market
        self.primary_reserve_active = False                 # no unit      # marketing strategy: grid services: primary reserve
        self.secondary_reserve_power_active = False         # no unit      # marketing strategy: grid services: secondary reserve power
        self.secondary_reserve_energy_active = False        # no unit      # marketing strategy: grid services: secondary reserve energy without SR power
        self.SR_simultaneously_active = False               # no unit      # marketing strategy: use positive and negative SR power at the same time (only possible if powerfactor >= 2)
        self.purchase_active = False                        # no unit      # it is possible to store power from the grid
        self.selfconsumption_active = False                 # no unit      # use storage for self consumption of the renewable plant
        self.capacity_storage_min = float(30)               # in MWh       # (minimum) capacity of storage
        self.capacity_storage_max = float(30)               # in MWh       # maximum capacity of storage (for optimization)
        self.capacity_step = float(30)                      # in MWh       # step size for storage capacity from min to max (for optimization)
        self.powerfactor_min = float(1)                     # in MWh/MW    # (minimum) factor capacity / power
        self.powerfactor_max = float(1)                     # in MWh/MW    # maximum factor capacity / power (for optimization)
        self.powerfactor_step = float(1)                    # in MWh/MW    # step factor capacity / power from min to max (for optimization)
        self.grid_limit = float(164.9)                      # in MW        # The BESS might be not allowed to feed all power produced into the grid. This variable indicates such a feed-in grid limit
        self.RES_consumption_costs = float(21.041)          # in ct/kWh    # costs, RES payes for electricity consumption incl. fee
        self.fees_BESS = float(0.11)                        # in ct/kWh    # sum of levies for the BESS
        self.discount_rate = float(2.0)                     # in %         # discounting future cash flows to present cash flows
        self.initial_discount = float(564000)               # in €         # discount of any kind. Maybe there is a subsidy for the project.
        self.initial_costs = float(0)                       # in €         # costs of any kind. Maybe the old transformer must be replaced by the new one.
        self.renewable_technology = "XXX"                   # no unit      # renewable technology connected to storage. Allowed are: 'wind'   'pv'   'wind_pv'   
        self.opex_storage_MWh = float(0.273)                # in €/MWh     # Operation and Maintanance costs of storage system per MWh produced energy; variable costs due to variation of cycle number are dependent on operation
        self.DOD = float(80)                                # in %         # the average depts of discharge describes how deep the BESS is cycled 
        self.cycles_per_year = int(1300)                    # no unit      # how many complete cycles = charge + discharge cycles should be simulated during the operation period?
        self.recovery_time = int(90)                        # in min/cycle # how much time does the storage need after one complete active cylce to the next one at minimum for cooling down? 
        self.recovery_activation = float(2)                 # cycles       # after how many cycles should the recovery mode be active?
        self.pu_pe = int(100)                               # in %         # how much power of nominal power should be used? Due to unknown degradation it is easier for the user to enter the ratio of usable power to EOL power
        self.self_consumption_pv = float(57.8)              # in kW        # self consumption of PV park in case of night or outages. The BESS can provide supply power
        self.self_consumption_wind = float(57.8)            # in kW        # self consumption of wind park in case of night or outages. The BESS can provide supply power
        self.self_discharge = float(4)                              # in %/month   # how much capacity will be lost by self-discharge
        self.SR_trading_energy_for_direct_activation = float(40)    # in €/MWh     # how much lower must the price bit be compared to average for assumed 100 % propable activation?
        self.factor_penalty = float(1.2)                            # no unit      # if a perfomance can not be provided, a penalty must be paid. The amount can be adjusted higher than the outstanding income
        self.prediction_horizon = int(8)                            # in 0.25 h    # number of timestamps (each 0.25 h) that are predicted by the program in simulation mode.
        self.storage_duration_PR = float(1)                         # in h         # how much capacity will be reserved for PR ?
        self.storage_duration_SR = float(1)                         # in h         # how much capacity will be reserved for SR ?
        self.storage_degradation_costs = float(8.486)               # in €/MW/cycle     # for Redispatch measures, the cycle degradation costs are compensated as well. Enter the costs of one cycle.
        self.safty_factor_capactiy  = float(2)                      # in %              # because self-discharge and RES+P are not considered in the planning phase, there should be a safty factor to charge a little more than needed to ensure stable discharge operation
        self.loss_not_optimal_market_behavior = float(20)           # in %              # the distribution of revenues will follow the optimal possible way. In real, it should be less because in case of an auction, it will not be won every time.
        self.matching_factor = float(1.5)                           # no unit           # the prediction horizon will calculate the revenue for multiple cases. If one case is selected, other cases can be combined with the first one but only if they are almost as good as the first. This factor describes how good the matching should be. 1 = best match, 2 = wide range of prices allowed -> will lead to more cycles
        self.RTE_annual_degradation = float(0.2)                    # percentage points # annual degradation of RTE
        self.RTE_SOC_dependency = float(26)                         # percentage points # for SOC = 100 %, additional RTE losses can be estimated, defined here. Better would it be to use a linear approximation
        self.residual_value = float(38)                             # in €/kWh          # income for selling the capacity unit after operation each replacement period. If costs are estimated, negative values are allowed


        # dependencies in Excel File of valid variables: Not every input is valid but only the input defined her which must equal the dependencies in the Excel file

        self.valid_total_power = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]       # in MW        # valid power entries of the program // user input will be rounded to next valid value - values could be added here + in the related Excel Files  
        self.valid_hours = [1, 2, 4, 6, 8, 10]                                                              # in MWh/MW    # valied storage hours // equal to power factor; user input will be rounded to next valid value - values could be added here + in the related Excel Files  
        self.valid_pu_pe = [1, 0.8, 0.6, 0.4, 0.2]                                                          # in %         # valid ratio of usable to EOL power // user input will be rounded to next valid value - values could be added here + in the related Excel Files  
        self.excel_year_start = 2025                                                                        # no unit      # first year in Excel file start date: 01.01.excel_year_start 00:15
        self.excel_year_end = 2050                                                                          # no unit      # last year in Excel file (end date: 01.01.excel_year_end 00:00); the end year itself is not within the data, only the first date of the end year


        # load as annual variables as vector dependent on year commissioning and storage technology

        self.capex_storage_kWh = np.full(1, 0, dtype=float)                 # in €/kWh     # vector of investement of storage in € / nominal capacity of storage in kWh during simulation period
        self.capex_storage_kW = np.full(1, 0, dtype=float)                  # in €/kW      # vector of investement of storage in € / nominal power of storage in kW during simulation period
        self.opex_storage_kW = np.full(1, 0, dtype=float)                   # in €/(kW*a)  # vector of operation and maintanance costs of storage system per installed power during simulation period
        self.roundtrip_efficiency = np.full(1, 0, dtype=float)              # in %         # AC/AC charge/discharge efficiency of storing energy in storage and releasing it to the grid
        self.grid_charges_kW = np.full(1, 0, dtype=float)                   # in €/(kW*a)  # power dependent grid charges will be evaluated by the program from predefined Excel File
        self.grid_charges_kWh = np.full(1, 0, dtype=float)                  # in ct/kWh    # capacity dependent grid charges will be evaluated by the program from predefined Excel File


        # load as 15-min step vector over whole periode

        self.curtailments_GO = np.full(1, 0, dtype=float)                       # in %         # vector of grid operator curtailments dependent on user input in Excel file. The vector's length is dependent on the calculation period
        self.intraday_prices = np.full(1, 0, dtype=float)                       # in €/MWh     # vector of intraday markt prices 
        self.primary_reserve_price = np.full(1, 0, dtype=float)                 # in €/MW      # vector of primary reserve prices
        self.secondary_reserve_price_MW_plus = np.full(1, 0, dtype=float)       # in €/MW      # vector of power price for positive secondary reserve
        self.secondary_reserve_price_MW_minus = np.full(1, 0, dtype=float)      # in €/MW      # vector of power price for positive secondary reserve
        self.secondary_reserve_price_MWh_plus = np.full(1, 0, dtype=float)      # in €/MWh     # vector of energy price for positive secondary reserve
        self.secondary_reserve_price_MWh_minus = np.full(1, 0, dtype=float)     # in €/MWh     # vector of energy price for positive secondary reserve
        self.primary_reserve_activation = np.full(1, 0, dtype=float)            # in %         # vector of primary reserve power. Negative values = discharging
        self.secondary_reserve_activation = np.full(1, 0, dtype=float)          # in %         # vector of secondary reserve power. Negative values = discharging
        

        # load as 15-min step vector over one year

        self.power_pv = np.full(1, 0, dtype=float)                              # in kW        # vector of feed-in power from pv into the grid
        self.power_wind = np.full(1, 0, dtype=float)                            # in kW        # vector of feed-in power from wind to the grid
        self.losses_wind = np.full(1, 0, dtype=float)                           # in %         # vector of losses of the wind plant
        self.losses_pv = np.full(1, 0, dtype=float)                             # in %         # vector of losses of the pv plant
        self.losses_storage = np.full(1, 0, dtype=float)                        # in %         # vector of losses of the storage
       

        # evaluated by program, single variabel

        self.end_year = int(2045)                               # no unit       # determined by start year and calculation period. The end year itself will not be calculated anymore
        self.simulation_power = float(10)                       # in MW         # constant power of one simulation. For first simulation simulation_power = capacity_storage_min / powerfactor_min
        self.simulation_capacity = float(100)                   # in MWh        # constant capacity of one simulation. For first simulation simulation_capacity = capacity_storage_min
        self.simulation_power_factor = float(1)                 # in MWh/MW     # constant power factor of one simulation. For first simulation simulation_power_factor = powerfactor_min
        
        self.investigated_timestamps_charge = int(0)            # per year; How many timestamps are affected by charing to meet the goal cycles
        self.investigated_timestamps_discharge = int(0)         # per year; How many timestamps are affected by discharing to meet the goal cycles
        self.investigated_timestamps_PR_power = int(1)          # per year; for PR;    dependent on activation propability in each year: much more timestamps can be sold on the market because the energy is not always called
        self.investigated_timestamps_SR_power_plus = int(0)     # per year; for SR+P;  dependent on activation propability in each year: much more timestamps can be sold on the market because the energy is not always called
        self.investigated_timestamps_SR_power_minus = int(0)    # per year; for SR-P;  dependent on activation propability in each year: much more timestamps can be sold on the market because the energy is not always called
        self.investigated_timestamps_SR_twice_power = int(0)    # per year; for SR+-P; dependent on activation propability in each year: much more timestamps can be sold on the market because the energy is not always called


        # evaluated by program: vector

        self.one_year_res = np.full(35063, 0, dtype=float)                          # in kW; created with nominal year entries and filled in calculation.py
        self.RES_production = np.full(1,0,dtype=float)                              # in kW; includes pv + wind production with consideration of RES losses and length of whole calculation periode
        self.one_year_storage_loss = np.full(35063, 0, dtype=float)                 # in %; one nominal year storage losses
        
        self.annual_activation_propability_PR = np.full(0, 0, dtype=float)          # in %   # for positive and negative PR together; vector over simulation period in annual resolution
        self.annual_activation_propability_SR_plus = np.full(0, 0, dtype=float)     # in %   # for positive SR; vector over simulation period in annual resolution
        self.annual_activation_propability_SR_minus = np.full(0, 0, dtype=float)    # in %   # for negative SR; vector over simulation period in annual resolution
        self.annual_activation_propability_SR_twice = np.full(0, 0, dtype=float)    # in %   # for positive and negative SR together; vector over simulation period in annual resolution

        self.nominal_price_intraday = np.full(0, 0, dtype=float)            # intraday prices converted for comparison: € / MWh -> € / (MW * 15 min * 100 % activation)
        self.nominal_price_SR_energy_plus = np.full(0, 0, dtype=float)      # SR energy + prices converted for comparison: € / MWh -> € / (MW * 15 min * 100 % activation) & 100 % activation by user-defined variable
        self.nominal_price_SR_energy_minus = np.full(0, 0, dtype=float)     # SR energy - prices converted for comparison: € / MWh -> € / (MW * 15 min * 100 % activation) & 100 % activation by user-defined variable
        self.nominal_price_SR_power_plus = np.full(0, 0, dtype=float)       # SR power + prices converted for comparison: € / MW -> € / (MW * 15 min * 100 % activation) & 100 % activation by activation propability
        self.nominal_price_SR_power_minus = np.full(0, 0, dtype=float)      # SR power - prices converted for comparison: € / MW -> € / (MW * 15 min * 100 % activation) & 100 % activation by activation propability
        self.nominal_price_SR_power_twice = np.full(0, 0, dtype=float)      # SR power + & - prices converted for comparison: from nom price SR power +  &  nom price SR power -
        self.nominal_price_RES_power = np.full(0, 0, dtype=float)           # RES trading prices (= power from RES to BESS only) converted for comparison: nom intraday prices without taxes
        self.nominal_price_PR = np.full(0, 0, dtype=float)                  # PR price converted for comparison: € / MW -> € / (MW * 15 min * 100 % activation) & 100 % activation by activation propability

        self.V_charging_operation = np.full(0, 0, dtype=int)        # best timestamps of charging yearly numerated
        self.V_discharging_operation = np.full(0, 0, dtype=int)     # best timestamps of discharging yearly numerated
        self.V_reserve_power_operation = np.full(0, 0, dtype=int)   # best timestamps of reserve power yearly numerated
        self.V_plan_operation = np.full(0,"0",dtype=object)         # plan operation with market ID of charging / discharging each timestamp; optimum of 3 vectors above


        # evaluated by program: matrix

        self.M_best_charging_prices = np.empty((0, 2), dtype=object)        # matrix of best charging prices; 1. column: best price; 2. column: from which market?
        self.M_best_discharging_prices = np.empty((0, 2), dtype=object)     # matrix of best discharging prices; 1. column: best price; 2. column: from which market?
        self.M_best_power_prices = np.empty((0, 2), dtype=object)           # matrix of best power prices from reserve markets; 1. column: best price; 2. column: from which market?
        

    def print_vector_lengths(self):  

        """Use this function to print the recent vector lengths of all variables included in this class."""
       
        for attr_name in dir(self):

            # only NumPy-Arrays:
            attr_value = getattr(self, attr_name)

            if isinstance(attr_value, np.ndarray):

                print(f"length of {attr_name}: {len(attr_value)}")
