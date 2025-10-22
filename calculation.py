# import libraries and classes
import numpy as np
from input_data import input_data
from simulation_data import simulation_data
import math
import numpy_financial as npf 

# main class of file
class calculation:

    def __init__(self, inda: input_data, sim: simulation_data):

        """This is the initialization function. This class containes all relevant calculations of the simulation."""

        self.inda = inda
        self.sim = sim

    def equalize_vectors(self, inda: input_data):   

        """Calculate renewable production vectors together to RES_production and convert all 15-min resolution vectors to the same length."""

        # convert all annual vectors to the desired length of calculation period: 1 value per year

        if inda.calculation_period < len(inda.capex_storage_kW):
            inda.capex_storage_kW[:inda.calculation_period]

        if inda.calculation_period < len(inda.capex_storage_kWh):
            inda.capex_storage_kWh[:inda.calculation_period]

        if inda.calculation_period < len(inda.grid_charges_kW):
            inda.grid_charges_kW[:inda.calculation_period]

        if inda.calculation_period < len(inda.grid_charges_kWh):
            inda.grid_charges_kWh[:inda.calculation_period]

        if inda.calculation_period < len(inda.opex_storage_kW):
            inda.opex_storage_kW[:inda.calculation_period]

        if inda.calculation_period < len(inda.roundtrip_efficiency):
            inda.roundtrip_efficiency[:inda.calculation_period]

        # the values of CAPEX kWh and RTE will change dependend on the replacement period and not every year:

        # for initial installation
        next_replacement = inda.replacement_period

        for j in range(len(inda.roundtrip_efficiency)):
            
            # if the storage should be replaced every 2 year and the simulation period are two years, the storage is not replaced. The replacement will take place after year 2 which is out of the simulation
            if(j+1>next_replacement):    
               
                next_replacement = next_replacement + inda.replacement_period

            # not replace
            elif(j>0):
               
                # annual degradation is given in percentage points; not %
                inda.roundtrip_efficiency[j] = (inda.roundtrip_efficiency[j-1] - inda.RTE_annual_degradation)  
                inda.capex_storage_kWh[j] = inda.capex_storage_kWh[j-1]

        # create vector of RES production; neglecting values if more than one standard year is provided (leap years)
        # total period 25 a (considering leap years) = 876576 values // 35063,04 per year -> 35063 values per nominal year (see report)

        # for one year stored vectors; considering only one year without leap years; rest of 35063 values filled with 0 -> see class inda
        for i in range(35040): 

            # transfer all storage losses to nominal year losses
            inda.one_year_storage_loss[i] = inda.losses_storage[i]         

            if(inda.renewable_technology=="wind_pv"):

                # the total production of res is the sum of PV and wind prodcution, excluding losses
                inda.one_year_res[i] = inda.power_pv[i] * (float(100) - inda.losses_pv[i]) / float(100) + inda.power_wind[i] * (float(100) - inda.losses_wind[i]) / float(100)  
            
            elif(inda.renewable_technology=="pv"):

                # the total production of res is the PV prodcution, excluding losses
                inda.one_year_res[i] = inda.power_pv[i] * (float(100) - inda.losses_pv[i]) / float(100)  
            
            elif(inda.renewable_technology=="wind"):

                # the total production of res is the wind prodcution, excluding losses
                inda.one_year_res[i] = inda.power_wind[i] * (float(100) - inda.losses_wind[i]) / float(100) 


        # repeat annual vector n times of the calculation period to get to nominal years
        inda.RES_production = np.tile(inda.one_year_res, (inda.excel_year_end - inda.excel_year_start))             
        inda.losses_storage = np.tile(inda.one_year_storage_loss, (inda.excel_year_end - inda.excel_year_start))    

        # delete one year variables because all 15-min vectors should have the length of the calculation period

        inda.one_year_res = 0  
        inda.one_year_storage_loss = 0
        inda.losses_pv = 0
        inda.losses_wind = 0
        inda.power_pv = 0
        inda.power_wind = 0

        # limit all 15-min vectors to calculation period

        # determine start and end timestamp
        start = (inda.year_commissioning - inda.excel_year_start) * 35063
        end = (inda.excel_year_end - inda.end_year) * 35063 + 1                

        # for all vectors developed by retetition in this function from one year values, there must be one value less
        inda.RES_production = inda.RES_production[start:len(inda.RES_production) - (end - 1)]   
        inda.curtailments_GO = inda.curtailments_GO[start:len(inda.curtailments_GO) - end]
        inda.losses_storage = inda.losses_storage[start:len(inda.losses_storage) - (end - 1)]
        
        # for all vectors imported over the total period: They are trimmed now
        if(inda.intraday_active==True):

            inda.intraday_prices = inda.intraday_prices[start:len(inda.intraday_prices) - end]
        
        if(inda.primary_reserve_active==True):
        
            inda.primary_reserve_activation = inda.primary_reserve_activation[start:len(inda.primary_reserve_activation) - end]
            inda.primary_reserve_price = inda.primary_reserve_price[start:len(inda.primary_reserve_price) - end]
            
        if(inda.secondary_reserve_power_active==True or inda.secondary_reserve_energy_active==True or inda.SR_simultaneously_active==True):

            inda.secondary_reserve_activation = inda.secondary_reserve_activation[start:len(inda.secondary_reserve_activation) - end]
            inda.secondary_reserve_price_MW_minus = inda.secondary_reserve_price_MW_minus[start:len(inda.secondary_reserve_price_MW_minus) - end]
            inda.secondary_reserve_price_MW_plus = inda.secondary_reserve_price_MW_plus[start:len(inda.secondary_reserve_price_MW_plus) - end]
            inda.secondary_reserve_price_MWh_minus = inda.secondary_reserve_price_MWh_minus[start:len(inda.secondary_reserve_price_MWh_minus) - end]
            inda.secondary_reserve_price_MWh_plus = inda.secondary_reserve_price_MWh_plus[start:len(inda.secondary_reserve_price_MWh_plus) - end]

        # consider curtailments for RES: During GO curtailments, RES power is not available for BESS
        for i in range(len(inda.RES_production)):

            # too much power in grid = negative curtailments = reduction of RES_power
            if(inda.curtailments_GO[i] > 0):       
                
                inda.RES_production[i] = inda.RES_production[i] * (100 - inda.curtailments_GO[i]) / 100    
    

    def highest_values_of_vector(self, vector, number_highest):

        """return the highest values of a vector specified in 'vector'. How much elements should be investigated, is defined in 'number_highest'. It returns a numberated vector with 0=highest element, 1=second highest element... at the indices of the original vector. Not considered elements are set to 99999."""
        
        output = np.full(len(vector), 99999, dtype=int)

        # get vector of highest indices
        highest_indices = np.argpartition(vector, -number_highest)[-number_highest:]    
        
        # sort highest indeces
        sort_highest_indices = highest_indices[np.argsort(-vector[highest_indices])]    
        
        for rang, index in enumerate(sort_highest_indices, start=1):
            
            # sorted indices assigned with number 1,2,3...
            output[index] = rang                                                        
        
        return output
    

    def lowest_values_of_vector(self, vector, number_lowest):
        
        """return the lowest values of a vector specified in 'vector'. How much elements should be investigated, is defined in 'number_lowest'. It returns a numberated vector with 0=lowest element, 1=second lowest element... at the indices of the original vector. Not considered elements are set to 99999."""

        output = np.full(len(vector), 99999, dtype=int)
        
        # find indices of number_lowest values
        lowest_indices = np.argpartition(vector, number_lowest)[:number_lowest]        
        
        # sort array do get order
        sort_indices = lowest_indices[np.argsort(vector[lowest_indices])]               
        
        for rang, index in enumerate(sort_indices, start=1):

            # sorted numbers of indices - 1,2,3...
            output[index] = rang                                                        
        
        return output
    

    def find_annual_activation_propabilities(self, inda: input_data, i_values_start, i_values_end):

        """Calculate the activation propabilities of the reserve markets PR SR+P SR-P SR+-P and store them as annual vectors in inda."""

        recent_activation_p = 0.0
        # for SR+P help variable
        recent_activation_p_srp = 0.0   
        # for SR-P help variable
        recent_activation_p_srm = 0.0   

        if(inda.primary_reserve_active==True):  
            
            # annual activation vector PR
            primary_activation_yearly = inda.primary_reserve_activation[i_values_start:len(inda.primary_reserve_activation) - i_values_end].copy()  
            
            # count negative and positive activations together
            recent_activation_p = np.count_nonzero(primary_activation_yearly) / float(35063) * 100    

            # connect single year to total timeline
            inda.annual_activation_propability_PR = np.append(inda.annual_activation_propability_PR, recent_activation_p)  

        if(inda.secondary_reserve_power_active==True or inda.secondary_reserve_energy_active==True or inda.SR_simultaneously_active==True):
            
            # annual activation vector SR
            secondary_activation_yearly = inda.secondary_reserve_activation[i_values_start:len(inda.secondary_reserve_activation) - i_values_end].copy() 
            
            # count positive activations 
            recent_activation_p_srp = np.count_nonzero(secondary_activation_yearly < 0) / float(35063) * 100  
            
            # connect single year to total timeline for SR+P
            inda.annual_activation_propability_SR_plus = np.append(inda.annual_activation_propability_SR_plus, recent_activation_p_srp)     

            # count negative activations 
            recent_activation_p_srm = np.count_nonzero(secondary_activation_yearly > 0) / float(35063) * 100  
            
            # connect single year to total timeline for SR-P
            inda.annual_activation_propability_SR_minus = np.append(inda.annual_activation_propability_SR_minus, recent_activation_p_srm)   

        if(inda.SR_simultaneously_active==True):

            # if SR+-P is active, it is more propable that one of SR+P and SR-P is activated
            recent_activation_p = recent_activation_p_srm + recent_activation_p_srp     

            # connect single year to total timeline
            inda.annual_activation_propability_SR_twice = np.append(inda.annual_activation_propability_SR_twice, recent_activation_p)   


    def planned_timestamps(self, inda:input_data, i):   

        """How many timestamps should be investigated according to the number of cycles predefined by user? This function stores the amount of timestamps dependend on the market type in inda. If the amound exceeds all possible timestamps, it is set to maximum."""

        # converts system RTE into a calculation factor; the higher the RTE, the less extra charge cycles are needed.
        system_RTE_factor = 2 - inda.roundtrip_efficiency[i] / 100  

        # converts self-discharge into a calculation factor; the higher the self-discharge rate, the more charge cycles are needed
        self_discharge_factor = 1 + inda.self_discharge / 100         

        # how many charge & discharge timestamps are needed annually? see formulars in thesis for explanation
        inda.investigated_timestamps_charge = int(inda.cycles_per_year * 4 * inda.simulation_power_factor * system_RTE_factor * self_discharge_factor) 
        inda.investigated_timestamps_discharge = int(inda.cycles_per_year * 4 * inda.simulation_power_factor)   

        # simplified limit to all timestamps in a year. More are impossible
        if(inda.investigated_timestamps_charge > 35062): inda.investigated_timestamps_charge = 35062        
        if(inda.investigated_timestamps_discharge > 35062): inda.investigated_timestamps_discharge = 35062     


        # for power, more timestamps can be covered due to activation propability < 100 %. For secondary reserve energy: if the bit price is lower than the average, the activation propability is circa 100 %
        
        # timestamps of PR
        if(inda.primary_reserve_active==True): inda.investigated_timestamps_PR_power = int((inda.investigated_timestamps_discharge + inda.investigated_timestamps_charge) / (2 * inda.annual_activation_propability_PR[i] / 100) )                 
        # timestamps of SR+P
        if(inda.secondary_reserve_power_active==True or inda.SR_simultaneously_active==True): inda.investigated_timestamps_SR_power_plus = int(inda.investigated_timestamps_discharge / (inda.annual_activation_propability_SR_plus[i] / 100))                                                   
        # timestamps of SR-P
        if(inda.secondary_reserve_power_active==True or inda.SR_simultaneously_active==True): inda.investigated_timestamps_SR_power_minus = int(inda.investigated_timestamps_charge / (inda.annual_activation_propability_SR_minus[i] / 100))                                                     
        # timestamps of SR+-P 
        if(inda.SR_simultaneously_active==True): inda.investigated_timestamps_SR_twice_power = int((inda.investigated_timestamps_discharge + inda.investigated_timestamps_charge) / (2 * inda.annual_activation_propability_SR_twice[i] / 100) )     

         # simplified limit to all timestamps in a year!

        if(inda.investigated_timestamps_PR_power > 35062): inda.investigated_timestamps_PR_power = 35062          

        if(inda.investigated_timestamps_SR_power_plus > 35062): inda.investigated_timestamps_SR_power_plus = 35062    

        if(inda.investigated_timestamps_SR_power_minus > 35062): inda.investigated_timestamps_SR_power_minus = 35062     

        if(inda.investigated_timestamps_SR_twice_power > 35062): inda.investigated_timestamps_SR_twice_power = 35062    


    def extract_possible_operation_periods(self, inda:input_data, sim:simulation_data):

        """The three matrices charge, discharge and power reserve market&prices are each analysed for best prices. The prices are numberated in this function for each matrix: 1=best price, 2=second best price, ... , 99999=out of consideration. The user defined cycles are considered as well."""

        # i=0,1... (calculation_period - 1)    # split total simulation into yearly simulations with 1 nominal year = 35063 x 15 min values
        for i in range(inda.calculation_period):   

            i_values_start = (i) * 35063                                # 0 for the first year
            i_values_end = (inda.calculation_period - i - 1) * 35063    # last index of value in a year
            
            # planned timestamps for charging, discharging and reserve power. They must be refreshed annually.
            self.planned_timestamps(inda,i)     

            charge_yearly = inda.M_best_charging_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 0].copy()          # cut out one year vector of matrix
            discharge_yearly = inda.M_best_discharging_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 0].copy()    # cut out one year vector of matrix
            reserve_power_yearly = inda.M_best_power_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 0].copy()      # cut out one year vector of matrix
            reserve_power_yearly_type = inda.M_best_power_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 1].copy() # cut out one year vector of matrix; for the type of reserve power activation e.g. PR

            discharge_yearly = np.array(discharge_yearly, dtype=float)              # convert to float
            discharge_yearly = np.round(discharge_yearly, decimals=3)               # round to 3 decimals
            charge_yearly = np.array(charge_yearly, dtype=float)                    # convert to float
            charge_yearly = np.round(charge_yearly, decimals=3)                     # round to 3 decimals
            reserve_power_yearly = np.array(reserve_power_yearly, dtype=float)      # convert to float
            reserve_power_yearly = np.round(reserve_power_yearly, decimals=3)       # round to 3 decimals

            # calculate charge and discharge operation numberated by best prices

            # because SR-E is stored already in the right unit by multiplying with (-1), it is comparable with INT-P
            charging_oparation_yearly = self.lowest_values_of_vector(charge_yearly, inda.investigated_timestamps_charge)                
            discharging_oparation_yearly = self.highest_values_of_vector(discharge_yearly, inda.investigated_timestamps_discharge)       

            # the number of timestamps is dependend on the type of reserve power because of a different activation propability. That is why the reserve power numberation must take place in a detailed loop
            reserve_power_oparation_yearly = np.full(35063, 99999, dtype=int)       
            # recent index of maximum value
            k = 0      
            # recent market of maximum value         
            market = "XXX"  
            #propabilities for charging / discharging
            p_charge = 0.5
            p_discharge = 0.5
            # calculation of timestamp equivalent of reserve power markets. Because they are less probable active, the cylce are timestamps influanced by them is very less. This variable indicates the part of the timestamp affected by the recent reserve power market
            equi_timestamps_reserve = inda.investigated_timestamps_charge * p_charge + inda.investigated_timestamps_discharge * p_discharge
            # some helping variables; 1 initial to prevent division by 0; makes no difference for large numbers
            count_charge = 1    
            count_discharge = 1
            recent_timestamps = 0

            # at maximum, the end of the algorithm will be if all timestamps are effected (dependend on user input possible)
            for e in range(35063):  

                k = np.argmax(reserve_power_yearly)         # find index of maximum
                reserve_power_oparation_yearly[k] = (e+1)   # first maximum = 1, then 2...
                market = reserve_power_yearly_type[k]       # find market of belonging recent max value
                reserve_power_yearly[k] = -1000             # set to out of range min value to not be considered further; only for local copy of variable; original matrix not effected

                # determine part of cycles effected by reserve power; the part is the ratio of charge+discharge timestamps and the timestamps of the reserve power market
                if(market == "PR"):

                    count_charge = count_charge + 0.5
                    count_discharge = count_discharge + 0.5
                    recent_timestamps = recent_timestamps + (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_PR_power

                elif(market == "SR+P"):

                    count_discharge = count_discharge + 1
                    recent_timestamps = recent_timestamps + inda.investigated_timestamps_discharge / inda.investigated_timestamps_SR_power_plus

                elif(market == "SR-P"):

                    count_charge = count_charge + 1
                    recent_timestamps = recent_timestamps + inda.investigated_timestamps_charge / inda.investigated_timestamps_SR_power_minus

                elif(market == "SR+-P"):

                    count_charge = count_charge + 0.5
                    count_discharge = count_discharge + 0.5
                    recent_timestamps = recent_timestamps + (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_twice_power

                else:

                    print("ERROR: unknown market in extract_possible_operation_periodes")
                    return

                # recalculate charge / discharge propabilities & equivalent timestamps

                p_charge = count_charge / (count_charge + count_discharge)
                p_discharge = 1 - p_charge
                equi_timestamps_reserve = inda.investigated_timestamps_charge * p_charge + inda.investigated_timestamps_discharge * p_discharge

                if(equi_timestamps_reserve <= recent_timestamps):

                    # all timestamps distributed; end of algorithm
                    break   


            # connect single years to total timeline
            inda.V_charging_operation = np.concatenate((inda.V_charging_operation, charging_oparation_yearly))   
            inda.V_discharging_operation = np.concatenate((inda.V_discharging_operation, discharging_oparation_yearly))  
            inda.V_reserve_power_operation = np.concatenate((inda.V_reserve_power_operation, reserve_power_oparation_yearly))   
            

    def generate_comparable_price_timelines(self, inda:input_data):

        """This function converts all origninal market prices to nominal prices which are comparable with each other. They have the unit € / MW / 15 min / full activation. The results are stored in the class inda."""
    
        # i=0,1... (calculation_period - 1)    # split total simulation into yearly simulations with 1 nominal year = 35063 x 15 min values
        for i in range(inda.calculation_period):    

            # determine start and end timestamps annually
            i_values_start = (i) * 35063  
            i_values_end = (inda.calculation_period - i - 1) * 35063
            # for inactive markets: set to default
            default = np.full(35063, -10000, dtype=float)
           
            # create vectors of activation propabilies for SR and PR, depending on activated markets
            self.find_annual_activation_propabilities(inda, i_values_start, i_values_end)   

            # cut out one year because the distribution of cycles is calculated yearly
            intraday_yearly = inda.intraday_prices[i_values_start:len(inda.intraday_prices) - i_values_end].copy()   

            # connect single years to total timeline  #  conversion from € / MWh to € / MW by division by 4
            inda.nominal_price_intraday = np.concatenate((inda.nominal_price_intraday, intraday_yearly / float(4)))   

            if(inda.secondary_reserve_energy_active==True or inda.secondary_reserve_power_active==True or inda.SR_simultaneously_active==True):

                # cut out one year because the distribution of cycles is calculated yearly
                SR_energy_plus_yearly = inda.secondary_reserve_price_MWh_plus[i_values_start:len(inda.secondary_reserve_price_MWh_plus) - i_values_end].copy()   

                # positive = discharging BESS  # connect single years to total timeline  #   conversion from € / MWh to € / MW by division by 4 and subtrating a user-defined price tolerance to ensure activation; subtracting means: get less money
                inda.nominal_price_SR_energy_plus = np.concatenate((inda.nominal_price_SR_energy_plus, (SR_energy_plus_yearly - inda.SR_trading_energy_for_direct_activation) / float(4)))   

                # cut out one year because the distribution of cycles is calculated yearly
                SR_energy_minus_yearly = inda.secondary_reserve_price_MWh_minus[i_values_start:len(inda.secondary_reserve_price_MWh_minus) - i_values_end].copy()   

                # negative = charging BESS; # connect single years to total timeline  #   conversion from € / MWh to € / MW by division by 4 and subtrating a user-defined price tolerance to ensure activation; subtracting means: pay more money because in the input file negative SR-E prices = pay money. The negative prices are more reduced by this formular, so more money must be paid.
                inda.nominal_price_SR_energy_minus = np.concatenate((inda.nominal_price_SR_energy_minus, (SR_energy_minus_yearly - inda.SR_trading_energy_for_direct_activation) / float(4)))   


            else:   # set impossible values for easier calculation if markets are inactive

                inda.nominal_price_SR_energy_minus = np.concatenate((inda.nominal_price_SR_energy_minus, default))  # aim for high prices
                inda.nominal_price_SR_energy_plus = np.concatenate((inda.nominal_price_SR_energy_plus,  default))   # aim for high prices

            if(inda.secondary_reserve_power_active==True or inda.SR_simultaneously_active==True):

                # converted activation propabilities
                SR_p_active = inda.annual_activation_propability_SR_plus[i] / float(100)
                SR_m_active = inda.annual_activation_propability_SR_minus[i] / float(100)

                # SR+P cut out one year because the distribution of cycles is calculated yearly
                SR_power_plus_yearly = inda.secondary_reserve_price_MW_plus[i_values_start:len(inda.secondary_reserve_price_MW_plus) - i_values_end].copy()   

                # SR+P; the energy price is added because you get extra money if you feed in
                SR_power_plus_yearly = (SR_power_plus_yearly + (SR_energy_plus_yearly / float(4)) * SR_p_active) / SR_p_active  
                
                 # connect single years to total timeline  #   conversion considering activation propability and nominal energy prices
                if(inda.secondary_reserve_power_active==True): inda.nominal_price_SR_power_plus = np.concatenate((inda.nominal_price_SR_power_plus, SR_power_plus_yearly))  

                # SR-P # cut out one year because the distribution of cycles is calculated yearly
                SR_power_minus_yearly = inda.secondary_reserve_price_MW_minus[i_values_start:len(inda.secondary_reserve_price_MW_minus) - i_values_end].copy()   
                
                # SR-P; the energy price is added because you get extra money if you consum energy; if negative prices given, then you have to pay
                SR_power_minus_yearly = (SR_power_minus_yearly + (SR_energy_minus_yearly / float(4)) * SR_m_active) / SR_m_active  

                # connect single years to total timeline  #   conversion considering activation propability and nominal energy prices
                if(inda.secondary_reserve_power_active==True): inda.nominal_price_SR_power_minus = np.concatenate((inda.nominal_price_SR_power_minus, SR_power_minus_yearly))   

                # for both SR+P & SR-P at the same time
                if(inda.SR_simultaneously_active==True):

                    # prices are added and activation propabilities to get the combined price
                    SR_power_twice_yearly = ( SR_power_plus_yearly * SR_p_active +  SR_power_minus_yearly * SR_m_active) / (SR_p_active + SR_m_active)

                    # connect single years to total timeline  #   conversion considering activation propability and nominal energy prices
                    inda.nominal_price_SR_power_twice = np.concatenate((inda.nominal_price_SR_power_twice, SR_power_twice_yearly))  

                    # deactivate other Power-Markets to only consider SR+-P: otherwise SR+-P will not be selected to disadvantage ratio of revenue to cylce usage. 
                    if(inda.secondary_reserve_power_active==False):     

                        inda.nominal_price_SR_power_minus = np.concatenate((inda.nominal_price_SR_power_minus, default))
                        inda.nominal_price_SR_power_plus = np.concatenate((inda.nominal_price_SR_power_plus,  default)) 

                else:   # set impossible values for easier calculation

                    inda.nominal_price_SR_power_twice = np.concatenate((inda.nominal_price_SR_power_twice, default))


            else:   # set impossible values for easier calculation

                inda.nominal_price_SR_power_minus = np.concatenate((inda.nominal_price_SR_power_minus, default))
                inda.nominal_price_SR_power_plus = np.concatenate((inda.nominal_price_SR_power_plus,  default)) 
                inda.nominal_price_SR_power_twice = np.concatenate((inda.nominal_price_SR_power_twice, default))  

            if(inda.primary_reserve_active==True):

                # cut out one year because the distribution of cycles is calculated yearly
                PR_price = inda.primary_reserve_price[i_values_start:len(inda.primary_reserve_price) - i_values_end].copy()   
               
                # connect single years to total timeline  #   conversion considering activation propability and nominal energy prices
                inda.nominal_price_PR = np.concatenate((inda.nominal_price_PR, PR_price / (inda.annual_activation_propability_PR[i] / 100)))   

            else:   # set impossible values for easier calculation

                inda.nominal_price_PR = np.concatenate((inda.nominal_price_PR, default))

            
            # trading with RES is always assumed possible. The case of selling power from BESS to RES is covered separetely. The other cases of the BESS charging from RES by saving taxes and duties and at grid limits are covered here
            
            # one year res at local variable
            res_yearly = inda.RES_production[i_values_start:len(inda.RES_production) - i_values_end].copy()    
            res_trading = np.full(35063, 0, dtype=float)

            # create nominal prices for RES-P
            for e in range(len(res_yearly)):

                # in case of a grid limit which is lower than the RES production: the BESS can charge the excess power for 0 €. Additionally there is a cost saving aspect for taxes and duties which would have been paid in case of grid consumption
                if res_yearly[e] > (inda.grid_limit*1000):

                    res_trading[e] = (0 - (inda.grid_charges_kWh[i] + inda.fees_BESS) * 10) / float(4)        

                # RES will sell the electricity for 0 at minimum. Otherwise RES will be curtailed.
                elif intraday_yearly[e] < 0 and res_yearly[e] > 0:                                                

                    res_trading[e] = (0 - (inda.grid_charges_kWh[i] + inda.fees_BESS) * 10) / float(4)     

                # standart case: RES sells energy to the BESS for the intradayprice. The BESS don't have to pay taxes in contrast to grid electricity
                elif res_yearly[e] > 0:

                    res_trading[e] = (intraday_yearly[e] - (inda.grid_charges_kWh[i] + inda.fees_BESS) * 10) / float(4)      

                # not RES production: set price very high to not be considered
                else:   

                    res_trading[e] = 9999

            # connect single years to total timeline 
            inda.nominal_price_RES_power = np.concatenate((inda.nominal_price_RES_power, res_trading))   


    def generate_optimum_price_matrices(self, inda:input_data):

        """3 matrices of optimum comparable prices should be calculated: optimum charge, optimum discharge and optimum reserve power markets. The output are 3 matrices, each consisting of the optimum price and the optimum market."""

        # Power market optimization
        best_power_prices = []

        for i in range(len(inda.nominal_price_intraday)):

            prices = [
                (inda.nominal_price_PR[i], "PR"),
                (inda.nominal_price_SR_power_plus[i], "SR+P"),
                (inda.nominal_price_SR_power_minus[i], "SR-P"),
                (inda.nominal_price_SR_power_twice[i], "SR+-P"),
            ]

            # Best price selection: maximum prices. Then the vector is created
            best_price = max(prices, key=lambda x: x[0])  
            best_power_prices.append(best_price)

        # conversion to np array
        inda.M_best_power_prices = np.array(best_power_prices, dtype=object) 


        # Charging market optimization
        best_charging_prices = []

        # condition for: only use RES-P as charging; never the grid. Then: copy RES-P prices only
        if(inda.purchase_active==False):        

            best_charging_prices = np.column_stack((inda.nominal_price_RES_power.copy(), np.full_like(inda.nominal_price_RES_power.copy(),"RES-P",dtype=object)))

        # if other markets are allowed too
        else:

            for i in range(len(inda.nominal_price_intraday)):

                # Inversion because now low prices are defined as best for charging. For the SR-E prices the conversion was the other way round.
                sr_e_neg = inda.nominal_price_SR_energy_minus[i] * (-1)  

                prices = [
                    (inda.nominal_price_intraday[i], "INT-P"),
                    (sr_e_neg, "SR-E"),
                    (inda.nominal_price_RES_power[i], "RES-P"),
                ]

                # Best price selection: minium prices are best. The vector is created.
                best_price = min(prices, key=lambda x: x[0])  
                best_charging_prices.append(best_price)

        # conversion to np array
        inda.M_best_charging_prices = np.array(best_charging_prices, dtype=object)


        # Discharging market optimization
        best_discharging_prices = []

        for i in range(len(inda.nominal_price_intraday)):

            prices = [
                (inda.nominal_price_intraday[i], "INT+P"),
                (inda.nominal_price_SR_energy_plus[i], "SR+E"),
            ]

            # Best price selection: maximum prices are best. The vector is created.
            best_price = max(prices, key=lambda x: x[0])  
            best_discharging_prices.append(best_price)

        # coversion to np array
        inda.M_best_discharging_prices = np.array(best_discharging_prices, dtype=object)

    
    def generate_plan_operation(self, inda:input_data):

        """This function generates the plan operation which is a vector including the goal markets of each timestamp to participate. The cycles of the battery are considered but no SOC and market limits."""

        # goal 1: get best price timestamps
        # goal 2: match the user defined cycles
        # goal 3: charging & discharging distributed equally

        # create vectors for annual analysis
        self.charging_plan = np.full(0,0,dtype=int) 
        self.discharging_plan = np.full(0,0,dtype=int) 
        self.reserve_plan = np.full(0,0,dtype=int) 
        self.RES_yearly = np.full(0,0,dtype=float) 
        self.reserve_power_yearly_type = np.full(0,0,dtype=object) 
        self.discharge_yearly_type = np.full(0,0,dtype=object)
        self.charge_yearly_type = np.full(0,0,dtype=object) 
        self.charge_yearly = np.full(0,0,dtype=float) 
        self.discharge_yearly = np.full(0,0,dtype=float) 
        self.reserve_power_yearly = np.full(0,0,dtype=float) 

        # i=0,1... (calculation_period - 1)    # split total simulation into yearly simulations with 1 nominal year = 35063 x 15 min values
        for i in range(inda.calculation_period):   

            # the calculation must be annual because the considered timestamps change with the activation propability of primary reserve markets, which changes annually

            self.index_charge = 0        # index of charging vector where recent value of V_charging_operation is investigated
            self.index_discharge = 0     # index of discharging vector where recent value of V_discharging_operation is investigated
            self.index_reserve = 0       # index of reserve vector where recent value of V_reserve_power_operation is investigated

            self.charge_cycle_stamp = 0        # count charge cycles only to have charge & discharge cycles equally distributed
            self.discharge_cycle_stamp = 0     # count discharge cycles only to have charge & discharge cycles equally distributed
            self.last_charge = 0               # last charge_value, for switching charge and discharge
            self.last_discharge = 0            # last discharge_value, for switching charge and discharge
            self.discharge_active = True       # to distribute charge & discharge equally; switches if one complete charge or discharge cycle is distributed

            # start and end timestamps of annual vector
            i_values_start = (i) * 35063  
            i_values_end = (inda.calculation_period - i - 1) * 35063
            
            # refresh annual planned timestamps for charging, discharging and reserve power
            self.planned_timestamps(inda,i)     

            # yearly investigated: investigated timestamps change annually
            self.charge_yearly = inda.M_best_charging_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 0].copy()            
            self.charge_yearly_type = inda.M_best_charging_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 1].copy()      
            self.discharge_yearly = inda.M_best_discharging_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 0].copy()      
            self.discharge_yearly_type = inda.M_best_discharging_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 1].copy() 
            self.reserve_power_yearly = inda.M_best_power_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 0].copy()        
            self.reserve_power_yearly_type = inda.M_best_power_prices[i_values_start : (len(inda.intraday_prices) - i_values_end), 1].copy()   
            self.charging_plan = inda.V_charging_operation[i_values_start : (len(inda.intraday_prices) - i_values_end)].copy()                 
            self.discharging_plan = inda.V_discharging_operation[i_values_start : (len(inda.intraday_prices) - i_values_end)].copy()           
            self.reserve_plan = inda.V_reserve_power_operation[i_values_start : (len(inda.intraday_prices) - i_values_end)].copy()              
            self.RES_yearly = inda.RES_production[i_values_start : (len(inda.intraday_prices) - i_values_end)].copy()                           
            
            # convert again because otherwise it is not stored as float and calculation operations wont work
            self.discharge_yearly = np.array(self.discharge_yearly, dtype=float)            # convert to float
            self.discharge_yearly = np.round(self.discharge_yearly, decimals=3)             # round to 3 decimals
            self.charge_yearly = np.array(self.charge_yearly, dtype=float)                  # convert to float
            self.charge_yearly = np.round(self.charge_yearly, decimals=3)                   # round to 3 decimals
            self.reserve_power_yearly = np.array(self.reserve_power_yearly, dtype=float)    # convert to float
            self.reserve_power_yearly = np.round(self.reserve_power_yearly, decimals=3)     # round to 3 decimals
            self.RES_yearly = np.array(self.RES_yearly, dtype=float)                        # convert to float
            self.RES_yearly = np.round(self.RES_yearly, decimals=3)                         # round to 3 decimals

            # this is the annual plan operation vector which is coverted to the calculation period afterwards
            self.plan = np.full(35063,"INACTIVE",dtype=object) 
            
            # at maximum all elements can be distributed, otherwhise exit previously (because of cycle limit)
            for e in range(35063):    

                # if all timestamps are distributed (35062) but the cycle goal is not met, the reserve power timestamps will be exchanged by charging & discharging markets to increase the cycles until the cycle goal is fulfilled.
                if(e>=35062): 

                    self.overwrite_reserve_timestamps(inda,i)
                    break   
                
                # all charge and discharge cycles have been distributed: goal fulfilled
                if(self.charge_cycle_stamp >= inda.investigated_timestamps_charge and self.discharge_cycle_stamp >= inda.investigated_timestamps_discharge):

                    break    

                # all charge cycles are distributed: distribute the rest of discharge timestamps
                if(self.charge_cycle_stamp >= inda.investigated_timestamps_charge):

                    self.discharge_active = True

                # all discharge cycles are distributed: distribute the rest of charge timestamps
                elif(self.discharge_cycle_stamp > inda.investigated_timestamps_discharge):

                    self.discharge_active = False

                # a complete charge timestamp is distributed. The next one is a discharge timestamp then
                elif(self.last_charge + 1 <= self.charge_cycle_stamp):    

                    self.last_charge = self.charge_cycle_stamp
                    self.discharge_active = True

                # a complete discharge timestamp is distributed. The next one is a charge timestamp then
                elif(self.last_discharge + 1 <= self.discharge_cycle_stamp):  

                    self.last_discharge = self.discharge_cycle_stamp
                    self.discharge_active = False

                # get the best charging, discharging and reserve power price and the related indices for comparison
                self.index_charge = np.argmin(self.charging_plan)        
                self.index_discharge = np.argmin(self.discharging_plan)       
                self.index_reserve = np.argmin(self.reserve_plan)        

                # reserve power and discharging markets are competitive because discharging and power reserve market aim for max price; charing for min price. The discharging market is better than the reserve power market
                if(self.discharge_active==True and self.discharge_yearly[self.index_discharge] > self.reserve_power_yearly[self.index_reserve] and self.discharging_plan[self.index_discharge]!=99999):  

                    # select the best discharging index at the plan operation vector and assign it to the corresponding discharging market
                    self.distribute_discharge_timestamp(inda,i,e)  
                
                # distribute the charging market at the timestamp of the charging index determined previously 
                elif(self.discharge_active==False and self.charging_plan[self.index_charge]!=99999):    

                    # assign the charging index at the plan operation vector to the corresponding charging market 
                    self.distribute_charge_timestamp(inda,i,e) 

                # reserve power markets are best: They will account neutral for both charging and discharging timestamps; competitive to discharge only because both aim for highest prices
                elif(self.reserve_plan[self.index_reserve]!=99999):

                    # assign the reserve power index at the plan operation vector to the corresponding reserve power market 
                    self.distribute_reserve_timestamp(inda,i,e)         
                
                # switch charge & discharge if all values of one are default to enable further distribution until the cycle goal is met.
                else:   

                    if(self.discharge_active == False): self.discharge_active = True
                    else: self.discharge_active = False

            # connect single years to total timeline of plan operation
            inda.V_plan_operation = np.concatenate((inda.V_plan_operation, self.plan))   
            
    
    def distribute_discharge_timestamp(self, inda:input_data, i, e):

        """This function distributes one discharge timestamp of the previously identified best discharge index."""

        # the recently best discharge market is is copied to the plan operation at the same index
        self.plan[self.index_discharge] = self.discharge_yearly_type[self.index_discharge]     
        
        # the recently distributed timestamp should not be overwritten: set discharging index of all comparable price vectors to default
        self.charging_plan[self.index_discharge] = 99999                                                          
        self.discharging_plan[self.index_discharge] = 99999 
        self.reserve_plan[self.index_discharge] = 99999 

        # 100 % activation propability estimated on markets INT+P and SR+E: distribute 1 total discharging timestamp
        if(self.plan[self.index_discharge] == "INT+P" or                                         
            self.plan[self.index_discharge] == "SR+E"):                                                       

            self.discharge_cycle_stamp = self.discharge_cycle_stamp + 1    
            
        else:   # error case: should not happen

            print("ERROR: unknown market in distribute_discharge_timestamp: discharge")
            print(self.plan[self.index_discharge])
            return

            
    def distribute_reserve_timestamp(self, inda:input_data, i, e):       

        """This function distributes one power reserve timestamp of the previously identified best power reserve index."""

        # power reserve is considered neutral in this case because the real activation is unknown

        # the recently best power reserve market is is copied to the plan operation at the same index
        self.plan[self.index_reserve] = self.reserve_power_yearly_type[self.index_reserve]     
        
        # the recently distributed timestamp should not be overwritten: set reserve power index of all comparable price vectors to default
        self.charging_plan[self.index_reserve] = 99999                                                         
        self.discharging_plan[self.index_reserve] = 99999 
        self.reserve_plan[self.index_reserve] = 99999 

        # the cycle impact is considered neutral: equal for charging & discharging and partly: only a part cycle is affected, depending on activation propability or in this case the ratio of charge+discharge timestamps devided by the reserve market timestamps

        if(self.plan[self.index_reserve] == "PR"):                                                       

            self.discharge_cycle_stamp = self.discharge_cycle_stamp + (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_PR_power / 2   
            self.charge_cycle_stamp = self.charge_cycle_stamp + (inda.investigated_timestamps_charge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_PR_power / 2

        elif(self.plan[self.index_reserve] == "SR+P"):

            self.discharge_cycle_stamp = self.discharge_cycle_stamp + (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_power_plus / 2  
            self.charge_cycle_stamp = self.charge_cycle_stamp + (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_power_plus / 2

        elif(self.plan[self.index_reserve] == "SR-P"):

            self.discharge_cycle_stamp = self.discharge_cycle_stamp + (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_power_minus / 2
            self.charge_cycle_stamp = self.charge_cycle_stamp + (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_power_minus / 2

        elif(self.plan[self.index_reserve] == "SR+-P"):

            self.discharge_cycle_stamp = self.discharge_cycle_stamp + (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_twice_power / 2
            self.charge_cycle_stamp = self.charge_cycle_stamp + (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_twice_power / 2

        else:

            print("ERROR: unknown market in distribute_discharge_timestamp: reserve")
            return


    def distribute_charge_timestamp(self, inda:input_data, i , e):

        """This function distributes one charging timestamp of the previously identified best charging index."""
       
        # the recently best charging market is is copied to the plan operation at the same index
        self.plan[self.index_charge] = self.charge_yearly_type[self.index_charge]    
            
        # the recently distributed timestamp should not be overwritten: set charging index of all comparable price vectors to default
        self.charging_plan[self.index_charge] = 99999                                                        
        self.discharging_plan[self.index_charge] = 99999 
        self.reserve_plan[self.index_charge] = 99999 

        # 100 % activation propability estimated on markets INT+P and SR+E: distribute 1 total charging timestamp
        if(self.plan[self.index_charge] == "INT-P" or                                         
            self.plan[self.index_charge] == "SR-E"):                                                       

            self.charge_cycle_stamp = self.charge_cycle_stamp + 1   

        # in case of charging from RES and a grid limit is exceeded, the BESS can charge the excess power to a preferred price. If the excess power is less than the usable power of the BESS, the BESS will charge with less power than pssible
        elif(self.plan[self.index_charge] == "RES-P"):            

            if(self.RES_yearly[self.index_charge] > inda.grid_limit):
            
                part_cycle = (self.RES_yearly[self.index_charge] - inda.grid_limit) / inda.simulation_power

                # case: RES-P power > grid limit + BESS power
                if(part_cycle > 1):     

                    part_cycle = 1

                self.charge_cycle_stamp = self.charge_cycle_stamp + part_cycle

            else:

                self.charge_cycle_stamp = self.charge_cycle_stamp + 1
        
        else:

            print("ERROR: unknown market in distribute_charge_timestamp")
            return


    def simulation_main_program(self, inda:input_data, sim:simulation_data):

        """Call this function after the planned operation calculation to perform a simulation. Based on the planned operation, the real operation, usable SOC and revenue are the main output vectors."""

        # considering SOC_sim = state of charge of constant usable capacity during simulation
        # considering grid operator positive and negative curtailments: consider them only in case of not participating at power reserve markets 
        # considering outages of the BESS
        # considering breaks between cycles for cooling the storge
        # considering selling periodes of power reserve markets (4h)
        # considering requirements of each market (e.g. for reserve markets: Is there enough available energy?)
        # considering penalties if energy / power is not available on markets. E.g. if there is not enough capacity for reserve power participation than required
        # considering self discharge & efficiency
        # considering RES+P: consider only if there is enough power in the storage after participating at the recent timestamp market. Because the extracted power is very low compared to the market traded power, it is considered seperately.
        # considering grid limit
        # considering prices & energies & powers & fees
        
        # goal: find real operation & revenue & SOC
        sim.real_operation = np.full(len(inda.nominal_price_intraday), "INACTIVE",dtype=object)  # operation of the BESS: could be a market as SR+P or INACTIVE or OUTAGE... Only 1 operation each timestamp (+ RES+P) is allowed!
        sim.SOC_sim = np.full(len(inda.nominal_price_intraday), 0, dtype=float)                  # usable SOC of the BESS: in % between 0 und 100             
        sim.revenue = np.full(len(inda.nominal_price_intraday), 0, dtype=float)                  # revenue of the BESS: for penalties negativ
       
        # relevant variables of this function
        self.year_index = 0                         # index of recent calculation year
        self.available_energy = 0                   # available energy in the storage
        self.free_energy = 0                        # available capacity for charging
        self.next_i = 0                             # the planning includes a vector of timestamps. The next real timestamp i investigated will normally not be i+1 but i+self.next_i

        # charging & discharging capacity will be changed depending on grid limit, res power... now they are initialized by default
        self.capacity_for_charging = 0.25 * inda.simulation_power * inda.roundtrip_efficiency[self.year_index] / 100    # capacity that can be charged real within 1 investigated timestamp 
        self.capacity_for_discharging = 0.25 * inda.simulation_power                                                    # capacity that can be discharged real within 1 investigated timestamp 

        # Every i recent timestamp, every e predicted timestamp these vectors of j elments are recalculated
        self.future_market = np.full(inda.prediction_horizon, "INACTIVE",dtype=object)      # no unit   # this vector will refresh for each value of future_revenue; the last index is the last elment within the prediction horizon. It includes the informations, which markets j should be used to reach plan operation at timestamp e.
        self.used_capacity_temp = np.full(inda.prediction_horizon, 0, dtype=float)          # in MWh    # describes the used capacity each timestamp: try to use nominal power but if SOC or market restrictions are violated, it might be less. RTE is included. It is used to determine capacity and power of future_market usage. all are positive values. In combination with the market, the information can be extracted if the capacity is charged or discharged.
        self.capacity_needed = float(0)                                                     # in MWh    # how much capactiy is needed to meet the plan operation each e? It is needed for planning and will refresh every e times
        self.operation_needed = "none"                                                      # no unit   # possible operations: # none # discharge # charge.  Operations needed to fulfill the conditions of e timestamp of future_revenue

        # results needed to compare all calculated predictions (e times), stored in future_market
        self.future_revenue = np.full(inda.prediction_horizon, 999998,dtype=float)          # 1 revenue calculated for each future_market vector, following different operations: reaching the plan value at e with e = element of the prediction horizon.
        
        # neglecting the real operation checks, the following include the final planned values as on the markets traded
        sim.real_plan_operation = np.full(len(inda.nominal_price_intraday), "INACTIVE",dtype=object)      # saved outputs of function: generate_real_plan; variable: future_market as variable over the calculation period
        sim.real_plan_energy =  np.full(len(inda.nominal_price_intraday), 0, dtype=float)                 # saved outputs of function: generate_real_plan used_capacity_temp as variable over the calculation period
        
        # set the recent timestamp to 0
        i = 0

        # covers total simulation period i = real recent timestamp of the simulation
        while i < len(inda.nominal_price_intraday):       

            self.next_i = 0                                                                   # reset, if changed in last iteration. The programm can distribute different values for next i and the recent timestamp will refresh accordingly.
            self.future_market = np.full(inda.prediction_horizon, "INACTIVE",dtype=object)    # reset because the length might be changed in program
            self.used_capacity_temp = np.full(inda.prediction_horizon, 0, dtype=float)        # reset because the length might be changed in program
        
            # count the index of the year; index = 0 is year 1. The RTE is for example dependend on the recent year. In contrast: 'i' will cover the total simulation period.
            if(i >= (self.year_index + 1) * 35063): 

                self.year_index = self.year_index + 1

                # capacity needed to charge to reach plan value operation. It will refresh in the program again. This is just an example of annual dependend variables
                self.capacity_for_charging = 0.25 * inda.simulation_power * inda.roundtrip_efficiency[self.year_index] / 100   
                        
            # assumption: start with SOC = 0
            if(i==0): self.available_energy = 0     
            else: self.available_energy = sim.SOC_sim[i-1] / 100 * inda.simulation_capacity     # already charged capacity
            self.free_energy = inda.simulation_capacity - self.available_energy                 # already discharged capacity
            
            # If the simulation is almost done, the last elements are neglected if there are not enough values for the prediction horizon left
            if(i+inda.prediction_horizon >= len(inda.nominal_price_intraday)): 
              
                while i < len(inda.nominal_price_intraday):
                    
                    # for the rest few values estimate INACTIVE and the last SOC
                    sim.SOC_sim[i] = sim.SOC_sim[i-1]   
                    sim.real_operation[i] = "INACTIVE"
                    sim.revenue[i] = 0
                    i = i + 1

                # end of the main simulation
                break            
                

            # generates the vector future_revenue and used_capacity_temp. These vectors are changed multiple times within the function but in the end they will return 1 optimum result for each vector. This result is used again in the next function.
            # considered are: grid limit, SOC, selling periodes of power reserve markets (4h), requirements of each market
            # if recover is still active, dont do further planning because it cant operate anyway
            if(sim.real_operation[i] != "RECOVER"): self.generate_real_plan(inda,sim,i)    
            
            # copy some intermediate results
            for s in range(len(self.future_market)):

                sim.real_plan_operation[s+i] = self.future_market[s]
                sim.real_plan_energy[s+i] = self.used_capacity_temp[s]


            # from the previous function the results future_market and used_capacity_temp are used.
            # the results of the following function are usable SOC, revenue and markets stored in sim for the total simulation period
            # other cases as GO curtailments, outages, activation of reserve energy and self-discharge could change the planned result of the previous function
            self.implement_real_operation(inda,sim,i)  


            # because a stack of data, e.g. 16 is analyzed, the next i could increase by 16. The amount is dependend on the real operation
            if(self.next_i > 1): i += self.next_i   
            else: i = i + 1

        
    def check_plan_operation_possible(self, inda:input_data, sim:simulation_data, recent_t, index_future):   # is at timestamp future_t the plan operation possible. The actual timestamp of the simulation is recent_t

        """Is it possible to reach plan operation at index_future? If yes, how much capacity is needed and what is the operation needed previously (charging, discharging or nothing) to real plan operation at index_future?"""

        # consider power reserve periodes 
        # consider SOC
        # consider efficiency 
        # considering grid limit 

        # needed capacity to reach plan operation: it will be refreshed every time this function is called
        self.capacity_needed = 0               
        # if changed, it is now set to default                                             
        self.capacity_for_discharging = 0.25 * inda.simulation_power    
         # if changed, it is now set to default 
        self.capacity_for_charging = 0.25 * inda.simulation_power * self.recent_RTE(inda,sim,recent_t) / 100   
        # self.available_energy is refreshed after each planning cycle and reset to real value after determination of next best price markets

        possible = False    # is it possible to meet the plan operation at future_t timestamp ( = index_future)?

        future_t = recent_t + index_future  # the future element of 3 timestamps in the future would be index_future = 3. The recent timestamp could be 2834 for example.

        power_reserve_possible = False      # is it possible to participate at power reserve market trading at the future time stamp?

        # is power reserve participation allowed at the recent timestamp? +16 to make the first timestamp 0 active for power reserve trading; every 16 timestamps, power reserve is allowed
        if((future_t+16) % 16 == self.reserve_offset(inda)):    

            power_reserve_possible = True  

        # do nothing is always possible
        if(inda.V_plan_operation[future_t]=="INACTIVE"):    

            self.operation_needed="none"
            self.capacity_needed = 0            
            possible = True
            return possible
        
        # the future plan is discharging the storage from Intradaymarket or SR+E Market. 
        elif(inda.V_plan_operation[future_t]=="INT+P" or inda.V_plan_operation[future_t]=="SR+E"):     
                
            # goal: discharging; how much capacity can be discharged that future timestamp?
            
            # is it possible to feed in considering grid limit?
            if(inda.grid_limit < inda.RES_production[future_t] / 1000 + inda.simulation_power):    

                # RES production is greater than grid limit -> the BESS is not allowed to feed in
                if(inda.grid_limit - inda.RES_production[future_t] / 1000 < 0): 

                    possible = False
                    return possible

                # in case of a grid limit only a part of the energy can be discharged. 
                else:
                    
                    self.capacity_for_discharging = 0.25 * (inda.grid_limit - inda.RES_production[future_t] / 1000)    


            # charge as much available energy that a discharge would be possible

            # operation would be possible a future_t timestamp without doing anything
            if(self.available_energy >= self.capacity_for_discharging):      

                self.operation_needed = "none"
                self.capacity_needed = 0
                possible = True
                return possible

            # because of partly charge & discharge by grid limit and RES-P charging are possible, the following loop will determine the available capacity for charging
            count_charge = 0

            # all timestamps before future_t are investigated for charging operation
            for r in range(index_future):   

                # if there is no plan at this index, it can be used for charging theoretically
                if(self.last_plan[r] == "INACTIVE"):

                    # if there is a grid limit, maybe only a part can be used
                    if(inda.V_plan_operation[future_t]=="RES-P" and inda.RES_production[future_t] / 1000 < inda.simulation_power):

                        count_charge = count_charge + (inda.RES_production[future_t] / 1000) / inda.simulation_power * self.capacity_for_charging   

                    # without grid limit the storage can charge with usable power
                    else:

                        count_charge = count_charge + self.capacity_for_charging

                # consider a little more charging to ensure stable discharge operation in case of events like self-discharge which are excluded from previous planning
                if(count_charge >= self.capacity_for_discharging * (1+inda.safty_factor_capactiy/100)):     

                    self.operation_needed = "charge"
                    self.capacity_needed = self.capacity_for_discharging * (1+inda.safty_factor_capactiy/100) - self.available_energy
                    possible = True
                    return possible

            return possible

        #charge from Market. Is it possible to reach this plan value?
        elif(inda.V_plan_operation[future_t]=="INT-P" or inda.V_plan_operation[future_t]=="RES-P" or inda.V_plan_operation[future_t]=="SR-E"):  

            # goal: charging. What capacity can be charged that timestamp?

            # if there is no RES production, the storage cannot be charged from RES
            if(inda.V_plan_operation[future_t]=="RES-P" and inda.RES_production[future_t] / 1000 < 0):

                possible = False
                return possible

            # if there is RESS production but less than the usable power of the BESS, the BESS can be charged partly
            elif(inda.V_plan_operation[future_t]=="RES-P" and inda.RES_production[future_t] / 1000 < inda.simulation_power): 

                # charging capacity is limited to available capacity from RES, considering RTE
                self.capacity_for_charging = 0.25 * inda.RES_production[future_t] / 1000 * self.recent_RTE(inda,sim,recent_t) / 100     

            # charge as much available energy that a discharge would be possible

            # operation would be possible a future_t timestamp without doing anything
            if(self.free_energy >= self.capacity_for_charging):     

                self.operation_needed = "none"
                self.capacity_needed = 0
                possible = True
                return possible

            # because of partly charge & discharge by grid limit and RES-P charging, the following loop will determine the available capacity for discharging
            count_discharge = 0

            # plan charging: consider RES-P production; # all timestamps before future_t are investigated for discharging operation
            for r in range(index_future):   

                if(self.last_plan[r] == "INACTIVE"):

                    if(inda.grid_limit < inda.simulation_power):

                        # only part of simulation power is used
                        count_discharge = count_discharge + inda.grid_limit / inda.simulation_power * self.capacity_for_discharging   

                    else:

                        count_discharge = count_discharge + self.capacity_for_discharging

                # there is enough discharged that the future charging operation is possible
                if(count_discharge >= self.capacity_for_charging * (1+inda.safty_factor_capactiy/100)):

                    self.operation_needed = "discharge"
                    self.capacity_needed = self.capacity_for_charging * (1+inda.safty_factor_capactiy/100) - self.free_energy   
                    possible = True
                    return possible
            
            return possible


        # goal: participate at PR market
        elif(inda.V_plan_operation[future_t]=="PR"):    

            # only to beginning of a reserve power period possible; will calculate the whole period then at once in the following functions
            if(power_reserve_possible==True):   
                
                # is the storage capacity big enough for participating at PR?
                if(inda.storage_duration_PR * inda.simulation_power > inda.simulation_capacity):   

                    possible = False
                    return possible

                # discharge needed: the same conditions as for discharge operation. For explanations look there
                if(self.free_energy < inda.storage_duration_PR * inda.simulation_power / 2):    

                    count_discharge = 0

                    for r in range(index_future):   

                        if(self.last_plan[r] == "INACTIVE"):

                            if(inda.grid_limit < inda.simulation_power):

                                # only part of simulation power is used
                                count_discharge = count_discharge + inda.grid_limit / inda.simulation_power * self.capacity_for_discharging   

                            else:

                                count_discharge = count_discharge + self.capacity_for_discharging

                        # the market participation requirement is fulfilled: return possible = true
                        if(count_discharge >= inda.storage_duration_PR * inda.simulation_power / 2 * (1+inda.safty_factor_capactiy/100)):

                            self.operation_needed = "discharge"
                            self.capacity_needed = inda.storage_duration_PR * inda.simulation_power / 2 * (1+inda.safty_factor_capactiy/100) - self.free_energy   
                            possible = True
                            return possible
                
                # charge needed: the same conditions as for charge operation. For explanations look there
                elif(self.available_energy < inda.storage_duration_PR * inda.simulation_power / 2):    
                  
                    count_charge = 0

                    for r in range(index_future):  

                        if(self.last_plan[r] == "INACTIVE"):

                            if(inda.V_plan_operation[future_t]=="RES-P" and inda.RES_production[future_t] / 1000 < inda.simulation_power):

                                # only part of simulation power is used
                                count_charge = count_charge + (inda.RES_production[future_t] / 1000) / inda.simulation_power * self.capacity_for_charging   

                            else:

                                count_charge = count_charge + self.capacity_for_charging

                        # enough charging timestamps found to perform discharging: return possible = true
                        if(count_charge >= inda.storage_duration_PR * inda.simulation_power / 2 * (1+inda.safty_factor_capactiy/100)):     

                            self.operation_needed = "charge"
                            self.capacity_needed = inda.storage_duration_PR * inda.simulation_power / 2 * (1+inda.safty_factor_capactiy/100) - self.available_energy
                            possible = True
                            return possible

                else: # if the SOC is in the allowed range, nothing must be done to reach the plan value

                    self.operation_needed = "none"   
                    possible = True
                    return possible

            possible = False
            return possible

        elif(inda.V_plan_operation[future_t]=="SR-P"):  # possible charging by the SR Market

            # participation only to begin of a reserve power period possible; will be calculated for the whole period then
            if(power_reserve_possible==True):   

                # is the storage capacity big enough for participating at SR? cosider 0.99 as tolerace factor because otherwise the program will rarely select SR markets for storage hour 1
                if(inda.storage_duration_SR * 0.99 * inda.simulation_power > inda.simulation_capacity):    

                    possible = False
                    return possible

                # discharge needed
                if(self.free_energy < inda.storage_duration_SR * 0.99 * inda.simulation_power):    

                    count_discharge = 0

                    for r in range(index_future):  

                        if(self.last_plan[r] == "INACTIVE"):

                            if(inda.grid_limit < inda.simulation_power):

                                # only part of simulation power is used
                                count_discharge = count_discharge + inda.grid_limit / inda.simulation_power * self.capacity_for_discharging   

                            else:

                                count_discharge = count_discharge + self.capacity_for_discharging

                        if(count_discharge >= inda.storage_duration_SR * 0.99 * inda.simulation_power * (1+inda.safty_factor_capactiy/100)):

                            self.operation_needed = "discharge"
                            self.capacity_needed = inda.storage_duration_SR * 0.99 * inda.simulation_power * (1+inda.safty_factor_capactiy/100) - self.free_energy   
                            possible = True
                            return possible
                        
                else: # if the SOC is in the allowed range, nothing must be done to reach the plan value

                    self.operation_needed = "none"   
                    possible = True
                    return possible

            possible = False
            return possible

        # possible discharing by the SR market
        elif(inda.V_plan_operation[future_t]=="SR+P"):  

            # only to begin of a reserve power period possible; will be calculated for the whole period then
            if(power_reserve_possible==True):   
                
                # is the storage capacity big enough for participating at SR? 0.99 is a tolerance factor because for power factor 1, SR participation is chosen very rarely otherwise
                if(inda.storage_duration_SR * 0.99 * inda.simulation_power > inda.simulation_capacity):    
                    
                    possible = False
                    return possible

                # charge needed
                if(self.available_energy < inda.storage_duration_SR * 0.99 * inda.simulation_power):    

                    count_charge = 0

                    for r in range(index_future):   

                        if(self.last_plan[r] == "INACTIVE"):

                            if(inda.V_plan_operation[future_t]=="RES-P" and inda.RES_production[future_t] / 1000 < inda.simulation_power):

                                # only part of simulation power is used
                                count_charge = count_charge + (inda.RES_production[future_t] / 1000) / inda.simulation_power * self.capacity_for_charging   

                            else:

                                count_charge = count_charge + self.capacity_for_charging

                        # engough was charged to participate at the SR+P market; return possible = true
                        if(count_charge >= inda.storage_duration_SR * 0.99 * inda.simulation_power * (1+inda.safty_factor_capactiy/100)):     

                            self.operation_needed = "charge"
                            self.capacity_needed = inda.storage_duration_SR * 0.99 * inda.simulation_power * (1+inda.safty_factor_capactiy/100) - self.available_energy
                            possible = True
                            return possible
                        
                else: # if the SOC is in the allowed range, nothing must be done to reach the plan value

                    self.operation_needed = "none"   
                    possible = True
                    return possible

            possible = False
            return possible

        # discharing or charing is possible by the SR+-P market
        elif(inda.V_plan_operation[future_t]=="SR+-P"):  

            # participation only at the beginning of a 16-timestamp period possible; the whole period will be calculated in following functions
            if(power_reserve_possible==True):   

                # is the storage capacity big enough for participating at SR+-P? considering a tolerance factor of 0.99; otherwise the market would be rarely chosen with power factor 2
                if(inda.storage_duration_SR * 0.99 * 2 * inda.simulation_power > inda.simulation_capacity):   

                    possible = False
                    return possible

                # discharge needed
                if(self.free_energy < inda.storage_duration_SR * 0.99 * inda.simulation_power):    

                    count_discharge = 0

                    for r in range(index_future):   

                        if(self.last_plan[r] == "INACTIVE"):

                            if(inda.grid_limit < inda.simulation_power):

                                # only part of simulation power is used
                                count_discharge = count_discharge + inda.grid_limit / inda.simulation_power * self.capacity_for_discharging   

                            else:

                                count_discharge = count_discharge + self.capacity_for_discharging

                        # there is enough capacity dischared to participate at the SR+-P market; return possible = true
                        if(count_discharge >= inda.storage_duration_SR * 0.99 * inda.simulation_power * (1+inda.safty_factor_capactiy/100)):

                            self.operation_needed = "discharge"
                            self.capacity_needed = inda.storage_duration_SR * 0.99 * inda.simulation_power * (1+inda.safty_factor_capactiy/100) - self.free_energy  
                            possible = True
                            return possible
                
                # charge needed
                elif(self.available_energy < inda.storage_duration_SR * 0.99 * inda.simulation_power):    
                  
                    count_charge = 0

                    for r in range(index_future):   

                        if(self.last_plan[r] == "INACTIVE"):

                            if(inda.V_plan_operation[future_t]=="RES-P" and inda.RES_production[future_t] / 1000 < inda.simulation_power):

                                # only part of simulation power is used
                                count_charge = count_charge + (inda.RES_production[future_t] / 1000) / inda.simulation_power * self.capacity_for_charging  

                            else:

                                count_charge = count_charge + self.capacity_for_charging

                        # there is enough capacity charged to participate at the SR+-P market; return possible = true
                        if(count_charge >= inda.storage_duration_SR * 0.99 * inda.simulation_power * (1+inda.safty_factor_capactiy/100)):     

                            self.operation_needed = "charge"
                            self.capacity_needed = inda.storage_duration_SR * 0.99 * inda.simulation_power * (1+inda.safty_factor_capactiy/100) - self.available_energy
                            possible = True
                            return possible

                else: # if the SOC is in the allowed range, nothing must be done to reach the plan value

                    self.operation_needed = "none"   
                    possible = True
                    return possible

            possible = False
            return possible
        
        else:
            
            possible = False
            return possible    
    

    def generate_real_plan(self,inda:input_data,sim:simulation_data,i):

        """This function calculates an improved plan based on the original plan which includes SOC and market limitations. The output are vectors with length of the prediction horizon of optimal market participation and the capacity needed each timestamp."""

        # consider power reserve periodes
        # consider SOC
        # consider efficiency
        # considering grid limit

        self.overcompensation = False                                                   # if charging is required for discharging but it violates SOC restrictions, this is indicated by this variable
        self.last_plan = np.full(len(self.future_market), "INACTIVE",dtype=object)      # here the last plan is stored. The plan will be improved over number_plans dependend on the power factor (capacity / power ratio)
        self.last_revenue = 999998                                                      # here the last revenue is stored. The recent revenue will be compared with this variable
        self.duty_operation = "none"                                                    # first, charging and discharging should be possible. After one loop, either charging or discharging is selected for further loops because if charing and discharing will appear before the first plan value, the operations will cancel each other out
        self.last_capacity_used = np.full(len(self.future_market), 0,dtype=float)       # it could be possible that less capacity is used than possible. This vector stores the activated capacities dependent on last_market
        check_possible = False

        #self.recent_capacity = 0      # recent capactiy distributed by charging or discharging operation; During number_plans, the number will increase
        # available and free energy are refreshed before the start of the function and after each possible number_plans

        # at the same prediction as many timestamps can be tried to reach plan operation as simulation_power_factor allows because if there is more capacity than power, multiple chargings & dischargings can be planned. // * 4 because there are 15-min instead of 1 hour values
        for number_plans in range(int(inda.simulation_power_factor) * 4):            

            # reset the future revenue for every plan iteration
            self.future_revenue = np.full(inda.prediction_horizon, 999998,dtype=float)
            
            # plan the operation e times with plan_operation is reached at e
            for e in range(len(self.future_revenue)):   

                self.overcompensation = False   
                self.operation_needed="DEFAULT"     
                
                # a new plan will be arranged maybe, therefore load the old planned fixed values. They might be added:
                self.future_market = self.last_plan.copy()     
                self.used_capacity_temp = self.last_capacity_used.copy()

                # the availebale capacity might be changed in previous plans: refresh
                self.refresh_available_energy(i,inda,sim,e)     

                # only operate at inactive timestamps and not where there is already a plan
                if(self.last_plan[e] == "INACTIVE"):      
                    
                    # checks if plan operation at timestamp e is possible and what capacity and operation is needed to reach it
                    check_possible = self.check_plan_operation_possible(inda,sim,i,e)

                    # if operation at future e is impossible, do not consider the whole plan anymore
                    if(check_possible==False): 

                        self.future_revenue[e] = 999999     # set a very unfavorable price

                    # plan operation at future e is possible: go on and calculate a comparative price that indicates the effort of operation
                    if(check_possible==True):    
                        
                        # plan operation is possible at e: copy the plan operation to the future_market prediction
                        self.future_market[e] = inda.V_plan_operation[i+e]  
                        
                        # capacity for charging & discharging are already adjusted in function check_plan_operation_possible for charging & discharging
                        # copy their values also: how much energy will be charged or discharged at future timestamp e?
                        if(self.is_charging_market(inda.V_plan_operation[i+e])==True): self.used_capacity_temp[e] = self.capacity_for_charging   
                        if(self.is_discharging_market(inda.V_plan_operation[i+e])==True): self.used_capacity_temp[e] = self.capacity_for_discharging   
                        # in case of reserve markets, there is no energy charged or discharged for sure at timestamp e, will be considered later
                        
                        # to reach plan operation at e, charging is needed
                        if(self.operation_needed=="charge" and (self.duty_operation=="charge" or self.duty_operation =="none")):  

                            # plan exactly which timestamps are best for charging. The energy amount is known from function check_plan_operation_possible
                            if(self.plan_charging_future(inda,sim,i,e)==False):

                                self.future_revenue[e] = 999999  

                        # to reach plan operation at e, discharging is needed
                        elif(self.operation_needed=="discharge" and (self.duty_operation=="discharge" or self.duty_operation =="none")): 

                            # plan exactly which timestamps are best for discharging. The energy amount is known from function check_plan_operation_possible
                            if(self.plan_discharging_future(inda,sim,i,e)==False):

                                self.future_revenue[e] = 999999  

                        # no further markets have to be planned: just continue with plan operation
                        elif(self.operation_needed!="none"):

                            self.used_capacity_temp = self.last_capacity_used.copy()
                            self.future_market = self.last_plan.copy()
                            # doing nothing is always best. No further planning must be considered in the same prediction
                            return      
                        
                        # if the future revenue is already set, the case should be disregarded. Otherwise calculate a comparable revenue.
                        if(self.future_revenue[e] != 999999):

                            # calculate a comparable revenue which enables comparison of different predictions
                            self.revenue_per_cycle(inda,sim,i,e)       
                          

            # reset the goal vectors to the last valid plan
            self.future_market = self.last_plan.copy()     
            self.used_capacity_temp = self.last_capacity_used.copy()

            # find optimum markets  # all future_revenues as vector with length of prediction horizon are analysed for minimum = best case
            best_case = np.argmin(self.future_revenue)     

            # if an additional case should be included, it must be almost as good as the last case. The tolerace is defined by the matching factor
            if(self.future_revenue[best_case] < self.last_revenue * inda.matching_factor):  

                self.check_plan_operation_possible(inda,sim,i,best_case)            # refresh operation_needed
                self.future_market[best_case] = inda.V_plan_operation[i+best_case]  # store the result of the goal market
                
                # safe the energy that will be charged / discharged at the future timestamp
                if(self.is_charging_market(inda.V_plan_operation[i+best_case])==True): self.used_capacity_temp[best_case] = self.capacity_for_charging   
                if(self.is_discharging_market(inda.V_plan_operation[i+best_case])==True): self.used_capacity_temp[best_case] = self.capacity_for_discharging  
                
                if(self.operation_needed=="charge"): self.plan_charging_future(inda,sim,i,best_case)            # refresh the markets
                elif(self.operation_needed=="discharge"): self.plan_discharging_future(inda,sim,i,best_case)    # refresh the markets
                
                # an end check if multiple planning leads to an not possible exception. In theorie, all checks are already applied before 
                if(self.check_saved_operations_possible(inda,sim,best_case,i)==True):    

                    # if the first plan is a charging plan, further planns must be none or charging as well. Otherwise some plans may be impossible
                    self.duty_operation = self.operation_needed      
                    
                    # safe end results of recent plan in last plan
                    self.last_plan = self.future_market.copy()
                    self.last_revenue = self.future_revenue[best_case]
                    self.last_capacity_used = self.used_capacity_temp.copy()   

                    # if a reserve power market is reached, return to implement the full series
                    if(self.is_reserve_market(self.future_market[best_case])==True): return      

                    # if some SOC limits were already violated, no further planning is necessary
                    if(self.overcompensation==True): return  

                    # available & free energy are refreshed in function: check_saved_operations_possible
                
                else: #if recent market operation is not possible, select last one

                    self.future_market = self.last_plan.copy()
                    self.used_capacity_temp = self.last_capacity_used.copy()
                    return

            else:   # use the old one (or initally INACTIVE)

                self.future_market = self.last_plan.copy()                  # refresh market
                self.used_capacity_temp = self.last_capacity_used.copy()    # refresh used capacities
                return
        

    def plan_charging_future(self,inda:input_data,sim,recent_t,index_future):  

        """If there must be some charing before discharging or reserve power participation, this function determines the optimum charging timestamps to reach plan operation at index_future."""

        okay = False

        # recent capactiy distributed by charging operation
        self.recent_capacity = 0      

        # index_future equals e in previous function
        future_t = recent_t + index_future  

        # it is impossibe to plan an operation if there is no timestamp to plan 
        if(index_future <= 0): 

            okay = False
            return okay 

        # copy part of the original vector to not destroy the orignial by changing values
        self.investigation_vector = inda.M_best_charging_prices[recent_t:future_t, 0].copy()    # trim the vector to the investigation period        
        self.investigation_vector = np.array(self.investigation_vector, dtype=float)            # convert to float
        self.investigation_vector = np.round(self.investigation_vector, decimals=2)             # round to 2 decimals
        self.investigation_type = inda.M_best_charging_prices[recent_t:future_t, 1].copy()      # is directly a string

        # try to set up charging to reach the plan value 

        # j timestamps time to reach the plan value by charing 
        for j in range(len(self.investigation_vector)):     

            index_min = np.argmin(self.investigation_vector)     # minimum price for charging is best
                
            if(self.future_market[index_min]=="INACTIVE"):      # overwrite INACTIVE timestamps only

                # the minimum charge price is determined & the index of it. Then the market type is written in the goal vector future_market
                self.future_market[index_min] = self.investigation_type[index_min]      

                # for markets INT-P and SR-E, there is no power limit: estimating infinite delivery. For RES-P, there could be a limit
                # capacity_needed is already determined by check_function und used again at this function
                # this function also determines a capacity vector: how much capacity will be used each timestamp, including RTE

                # RES is providing less power than the storage could take
                if(self.future_market[index_min]=="RES-P" and inda.RES_production[index_min + recent_t] / 1000 < inda.simulation_power): 

                    # charging capacity is limited to available capacity from RES, considering RTE
                    self.used_capacity_temp[index_min] = 0.25 * inda.RES_production[index_min + recent_t] / 1000 * self.recent_RTE(inda,sim,recent_t) / 100     
                    
                else:

                    self.used_capacity_temp[index_min] = 0.25 * inda.simulation_power * self.recent_RTE(inda,sim,recent_t) / 100   
                    
                self.recent_capacity = self.recent_capacity + self.used_capacity_temp[index_min]
            
            # set very high to be not considered twice
            self.investigation_vector[index_min] = 99999    

            
            # check if planned timestamps for next operation are fulfilled - if yes, stop distributing charging timestamps.
            if(self.capacity_needed <= self.recent_capacity):  

                # there could be distributed too many charge timestamps already; this is checked and corrected in the following function
                self.check_overcompensation_charging(inda,sim,recent_t,index_future,index_min)  

                okay = True
                return okay


        return okay
    

    def plan_discharging_future(self,inda:input_data,sim,recent_t,index_future):  # at index_future, the planned value will be reached

        """If there must be some discharing before charging or reserve power participation, this function determines the optimum discharging timestamps to reach plan operation at index_future."""

        okay = False

        # recent capactiy distributed by discharigng operation
        self.recent_capacity = 0      

        future_t = recent_t + index_future 

        # if there are no timestamps to plan, planning is impossible
        if(index_future <= 0): 

            okay = False
            return okay 

        self.investigation_vector = inda.M_best_discharging_prices[recent_t:future_t, 0].copy()     # limit investigation prices to investigation period       
        self.investigation_vector = np.array(self.investigation_vector, dtype=float)                # convert to float
        self.investigation_vector = np.round(self.investigation_vector, decimals=2)                 # round to 3 decimals
        self.investigation_type = inda.M_best_discharging_prices[recent_t:future_t, 1].copy()       # the same for the market type

        # try to set up discharging to reach the plan value

        # j timestamps time to reach plan value by discharing 
        for j in range(len(self.investigation_vector)):     

            #  maximum price for discharging are best
            index_max = np.argmax(self.investigation_vector)     
                
            # only plan for recently inactive timestamps
            if(self.future_market[index_max]=="INACTIVE"):

                # plan discharging at best discharging index: copy market
                self.future_market[index_max] = self.investigation_type[index_max]     

            # set very low to be not considered twice
            self.investigation_vector[index_max] = -9999    

            # for markets INT-P and SR-E, there is no power limit: estimating infinite delivery. For RES-P, there could be a limit

            if(inda.RES_production[index_max + recent_t] / 1000 + inda.simulation_power > inda.grid_limit): 

                if(inda.RES_production[index_max + recent_t] / 1000 > inda.grid_limit):

                    self.used_capacity_temp[index_max] = 0
                    
                else: 
                    
                    self.used_capacity_temp[index_max] = 0.25 * ( inda.grid_limit - inda.RES_production[index_max + recent_t] / 1000)     

            else:

                self.used_capacity_temp[index_max] = 0.25 * inda.simulation_power

            self.recent_capacity = self.recent_capacity + self.used_capacity_temp[index_max]

            # check if planned timestamps for next operation are fulfilled - if yes, stop distributing discharge timestamps. The others are already set INACTIVE
            if(self.capacity_needed <= self.recent_capacity):  

                # there could be too much discharge timestamps distributed that SOC limits are violated. Then the following function will check and correct it.
                self.check_overcompensation_discharging(inda,sim,recent_t,index_future,index_max)   

                okay = True
                return okay


        return okay


    def revenue_per_cycle(self, inda:input_data, sim:simulation_data, recent_t, e): # j = index array of self.future_revenue[e] = goal . Developed from future_market[] to meet the plan operation at index e

        """This function calculates a comparable revenue for the markets recentlich defined in future_market[] and stores the result in future_revenue[]."""

        nominal_revenue = 0
        amount = 0

        # staying inactive is okay, but if there are other possibilities, better choose them
        if(self.future_market[e]=="INACTIVE"):     

            # set very worse future_revenue
            self.future_revenue[e] = 999997    
            return

        # the future revenue set will be the average of the numbered price vectors for the markets selected.
        # all 3 market types charge, discharge and power reserve are considered equally possible because each market type is numberated from 1 to end.
        for j in range(len(self.future_market)):        

            if(self.future_market[j] == "SR-E" or self.future_market[j]=="RES-P" or self.future_market[j]=="INT-P"):  

                nominal_revenue = nominal_revenue + sim.sorted_charge[recent_t+j]       # charging
                amount = amount + 1

            elif(self.future_market[j] == "SR+E" or self.future_market[j]=="INT+P"):    

                nominal_revenue = nominal_revenue + sim.sorted_discharge[recent_t+j]    # discharging
                amount = amount + 1

            elif(self.is_reserve_market(self.future_market[j])==True):   

                nominal_revenue = nominal_revenue + sim.sorted_reserve[recent_t+j]      # reserve  
                amount = amount + 1

            
        if(amount > 0):

            self.future_revenue[e] = nominal_revenue / amount         # calculate the average out of the sum

        else:

            self.future_revenue[e] = 999999                           # if whole period is INACTIVE, this case will be selected


    def check_saved_operations_possible(self,inda:input_data,sim:simulation_data,future_index, recent_t):

        """If there was a charge or discharge distribution, too many timestamps could have been distributed. This function checks and corrects the mistake by analysing the vector future_market[]."""

        #consider SOC min max
        #consider market conditions
        #consider up to future_t
        okay = True
       
        # builds again a local capactiy to be independend from other functions because its a checking function
        if(recent_t > 0): local_capacity = sim.SOC_sim[recent_t - 1] / 100 * inda.simulation_capacity    
        else: local_capacity = 0

        # is the initial SOC correct?
        if(local_capacity > inda.simulation_capacity or local_capacity < 0): 

            okay = False
            sim.SOC_error = sim.SOC_error + 1
            print("ERROR in check_saved_operations_possible: initial SOC already impossible!", future_index + recent_t, local_capacity, inda.simulation_capacity)
            if(local_capacity > inda.simulation_capacity): sim.SOC_sim[recent_t - 1] = 100
            if(local_capacity < 0): sim.SOC_sim[recent_t - 1] = 0
            return okay

        # checks for all future timestamps if the market participation ist right. If not, return false directly
        for e in range(len(self.future_market)):

            # charging reserve: there must be free capacity
            if((self.future_market[e]=="SR-P" or self.future_market[e]=="SR+-P") and local_capacity > inda.simulation_capacity - inda.storage_duration_SR * 0.99 * inda.simulation_power):    

                okay = False
                return okay

            # discharging reserve: there must be available capacity
            if((self.future_market[e]=="SR+P" or self.future_market[e]=="SR+-P")  and local_capacity < inda.storage_duration_SR * 0.99 * inda.simulation_power):    

                okay = False
                return okay

            # there must be available AND free capacity
            if((self.future_market[e]=="PR" and local_capacity < inda.storage_duration_PR * inda.simulation_power / 2)
                or (self.future_market[e]=="PR" and local_capacity > inda.simulation_capacity - inda.storage_duration_PR * inda.simulation_power / 2)):    

                okay = False
                return okay
               

            #action: predict charged capacity
               
            if(self.future_market[e]=="SR-E" or self.future_market[e]=="INT-P" or self.future_market[e]=="RES-P"):      # charing operation

                local_capacity = local_capacity + self.used_capacity_temp[e]        # perform charging

            elif(self.future_market[e]=="SR+E" or self.future_market[e]=="INT+P"):     

                local_capacity = local_capacity - self.used_capacity_temp[e]        # perform discharging

            # in case of reserve markets no activation of reserve power is considered because we are still in the planning step # the function will end anyway if one reserve market is reached. 

            # check if after charging or discharging action, SOC borders are violated
            if(local_capacity > inda.simulation_capacity or local_capacity < 0): 

                okay = False
                return okay


        # the result is, that every operation should be okay considering SOC. Only for market operation which dont meet the market conditions, this function will return false

        # overwrite original variables if all checks are fullfilled for next loop planning implementation
        self.available_energy = local_capacity
        self.free_energy = inda.simulation_capacity - local_capacity    

        return okay


    def implement_real_operation(self,inda:input_data,sim:simulation_data,i):

        """This function creates the main output vectors usable SOC, operation and revenue over the calculation period in 15-min resolution. The calculation is based on the developed future_market and usable_capacity_temp vector."""
        

        end_market = 0                                          # what is the last timestamp considered in self.future_market? -> the last one not INACTIVE
        end_market = self.resize_future_market(end_market)      # time prediction horizon will be adjusted: in case of reserve market, it must continue for 4 hours. Otherwise is the end the last not INACTIVE element of vector
        if(end_market < 1): end_market = 1                      # otherwise the loop below would be neglected

        for k in range(end_market):

            # everything is calculated new to not be influanced by planning
            # the values from planning are future_market and used_capacity_temp only
           
            # the capacity which belongs to the planned future_market for plan operation. Do not consider the capacity for reserve power markets.
            self.used_capacity = self.used_capacity_temp[k]      
            # the capacity paid is the one inclusive RTE losses for charging                                                  
            self.used_capacity_charging_pay = self.used_capacity_temp[k] / (self.recent_RTE(inda,sim,i)/100)       

            # following variables are resettet. The charge capacity that is affected by payment is inclusive the RTE
            self.capacity_for_discharging = 0.25 * inda.simulation_power    
            self.capacity_for_charging = 0.25 * inda.simulation_power * self.recent_RTE(inda,sim,i) / 100    
            self.capacity_for_charging_pay = self.capacity_for_charging / (self.recent_RTE(inda,sim,i)/100 ) 

            # in case of outages or recovering
            stand_still = False    
            
            # the end of the simulation period is not considered because no prediction horizon can be built with equal length. These few timestamps would be INACTIVE in the end
            if(i+k >= len(inda.nominal_price_intraday)): return   

            # i+k = investigated timestamp: what market & price & SOC will be here?

            if(i+k==0): SOC_consider = 0
            else: SOC_consider = sim.SOC_sim[i+k-1]
            self.available_energy = SOC_consider / 100 * inda.simulation_capacity
            self.free_energy = inda.simulation_capacity - self.available_energy

            # recovery time is needed after each complete cycle to cool down the storage. It is activated by the function below
            if(sim.real_operation[i+k]=="RECOVER"):    

                stand_still = True

            # writes "RECOVER" into the goal vector if a recovery case if active. This is checked by the following function
            elif(self.recovery_check(inda,sim,i,k)==True):  

                stand_still = True
            
            # end of receovery period: develop a new plan by returning
            if(i>0 and sim.real_operation[i+k]=="RECOVER" and sim.real_operation[i+k+1]!="RECOVER"):    #end of recovering handling

                sim.SOC_sim[i+k] = sim.SOC_sim[i+k-1]
                self.next_i = k + 1 
                stand_still = False
                return 

            # in case of not following plan operation, that are the usable capacities; in case of plan operation, use the variable used_capacity
            # the following function adjusts chargeable and dischargeable capacity at timestamp k (real: i+k)
            # case: grid limit: the capacity_for_discharging is reduced
            # case: RES production too low: capacity_for_charging reduced
            # case: SOC 100 or 0 out of range: limit charing / discharing to max and min SOC borders
            self.adjust_charging_discharging_capacity(inda,i,k,sim)     

            # outage of storage; only case 100 % outage is covered because otherwise different actions could be applied at the same timestamp
            if(inda.losses_storage[k+i]>0):   

                sim.real_operation[i+k] = "OUTAGE"  
                sim.SOC_sim[i+k] = sim.SOC_sim[i+k-1]   # SOC stays the same as timestamp before
                stand_still = True

            # the BESS will realize a charging curtailment CURTAIL- if it is not participating at a reserve market, the SOC is less than 100 %, there is no outage or recovering and the BESS is not participating at a charging market that timestamp
            if(inda.curtailments_GO[i+k] > 0 and SOC_consider < 100 and 
               self.is_charging_market(self.future_market[k])==False   
               and self.is_reserve_market(self.future_market[k])==False
               and stand_still==False): 
              
                self.active_GO_Curtailment_charging(inda,sim,i,k)   # Curtail- = charging


            # the BESS will realize a discharging curtailment CURTAIL+ if it is not participating at a reserve market, the SOC more than 0 %, there is no outage or recovering and the BESS is not participating at a discharging market that timestamp
            if(inda.curtailments_GO[i+k] < 0 and SOC_consider > 0 and   
               self.is_discharging_market(self.future_market[k])==False  
               and self.is_reserve_market(self.future_market[k])==False
               and stand_still==False): 
               
               self.active_GO_Curtailment_discharging(inda,sim,i,k)  # Curtail+ = discharging
              

            # either plan operation or penalty is outstanding; not in case of curtailments
            if(sim.real_operation[i+k] != "CURTAIL+" and sim.real_operation[i+k] != "CURTAIL-" and sim.last_plan_outage_considered==False):    

                # must a penalty be applied because the plan operation cannot be fulfilled?
                if(self.penalty(inda,sim,i,k,stand_still)==True):   

                    # only one wording is allowed for the timestamp
                    if(sim.real_operation[i+k]!="OUTAGE" and sim.real_operation[i+k]!="RECOVER"): sim.real_operation[i+k] = "PENALTY"      

                    # choose the last SOC: no operation in case of penalty
                    sim.SOC_sim[i+k] = SOC_consider     

                # follow the plan operation: calculate revenue and SOC
                elif(stand_still==False):

                    self.follow_plan_operation(inda,sim,i,k)


            # in special cases, the SOC stays the same
            elif(sim.last_plan_outage_considered==True and sim.real_operation[i+k] != "CURTAIL+" and sim.real_operation[i+k] != "CURTAIL-"):

                sim.SOC_sim[i+k] = SOC_consider


            # for self discharge
            # calculate the self-discharge loss for the recent timestamp in MWh and implement it by lowering the SOC
            self_discharge = sim.SOC_sim[k+i] / 100 * inda.simulation_capacity * inda.self_discharge / 100 / 30 / 24 / 4           
            sim.SOC_sim[k+i] = (sim.SOC_sim[k+i] / 100 * inda.simulation_capacity - self_discharge) / inda.simulation_capacity * 100
            if(sim.SOC_sim[k+i]<0): sim.SOC_sim[k+i] = 0

            # return after curtailments because in reality the original plan could be added by additional operations to meet plan values
            if(sim.real_operation[i+k] == "CURTAIL+" or sim.real_operation[i+k] == "CURTAIL-"):     

                self.next_i = k + 1     # element k is the curtailment
                return
            
            # if activated and needed, RES can consum energy from the BESS to a minor extent which is handeled in the following function
            if(inda.selfconsumption_active==True): self.power_supply_res_calc(inda,sim,k,i,stand_still)    


        # if the last traded value of the period is an outage and the outages continue, there will be no trades on the market to not loose money because the operation cannot be met.
        if(i>0 and sim.real_operation[i + end_market - 1]=="OUTAGE"):  

            sim.last_plan_outage_considered = True

        else: 
            
            sim.last_plan_outage_considered = False
            
        # at the end of the loop the next i considered by the main program would be that one after the last element implemented in sim.real_operation. That should be i + end_market element
        self.next_i = end_market    


    def is_reserve_market(self, market):

        """The function returns true, if the 'market' is a reserve power market, otherwise false."""

        h=False

        if(market=="SR+P"): h=True
        elif(market=="SR-P"): h=True
        elif(market=="SR+-P"): h=True
        elif(market=="PR"): h=True

        return h
    

    def recovery_check(self,inda:input_data,sim:simulation_data,i,k):

        """Does the storage system needs some time for cooling? If ture, then the cooling will be implemented in this function too."""

        active = False  # indicates if a recovery is needed

        # recovery time after each complete cycle without interrupts, limited by the recovery_activation defined by user
        if(i+k >= int(inda.simulation_power_factor * 4 * 2 * inda.recovery_activation + 1)):

            # investigated timestamps: * 4 for 4 time 15 min and times 2 for charging & discharging; recovery_activation to activate recovery before / after one cylce activation
            for u in range(int(inda.simulation_power_factor * 4 * 2 * inda.recovery_activation)): 

                # check to not violate array restrictions
                if(i+k-u-1 < len(inda.nominal_price_intraday) and i+k-u-1 > 0):   

                    # if there was one of the following defined operation the last cycle(s), then there must be no recovery
                    if(sim.real_operation[i+k-u-1]=="INACTIVE" or sim.real_operation[i+k-u-1]=="OUTAGE" or 
                        (sim.real_operation[i+k-u-1]=="PR" and inda.primary_reserve_activation[i+k-u-1] == 0) or
                        (sim.real_operation[i+k-u-1]=="SR+P" and inda.secondary_reserve_activation[i+k-u-1] >= 0) or
                        (sim.real_operation[i+k-u-1]=="SR-P" and inda.secondary_reserve_activation[i+k-u-1] <= 0) or
                        (sim.real_operation[i+k-u-1]=="SR+-P" and inda.secondary_reserve_activation[i+k-u-1] == 0) or 
                        sim.real_operation[i+k-u-1]=="RECOVER" or sim.real_operation[i+k-u-1]=="PENALTY"
                        or sim.real_operation[i+k-u-1]=="RES+P"):  

                        # inactive 15-min periods inbetween are considered as reset of the storage recovery time
                        break  
                    
                    # there must be recovery which is implemented for the recent and following timestamps defined in recovery_time
                    if(u>=int(inda.simulation_power_factor * 4 * 2 * inda.recovery_activation - 1) and int(inda.recovery_time / 15) >= 1):  

                        # recovery time in min is converted to the number of timestamps
                        for j in range(int(inda.recovery_time / 15)):       

                            # do not voilate array idex restrictions
                            if(i+k+j < len(inda.nominal_price_intraday) and i+k+j-1 > 0):   
                                
                                sim.real_operation[i+k+j] = "RECOVER"
                                active = True
                                sim.SOC_sim[i+k+j] = sim.SOC_sim[i+k+j-1]   # SOC stays the same
                                

        return active
           
        
    def penalty(self,inda:input_data,sim:simulation_data,i,k,stand_still):  

        """This function checks, if a penatly should be applied, for example in case of an outage, and calculates the negative revenue. If a penalty is applied, it returns true. The penalty is calculated for the whole planned power at this timestamp because each timestamp only one operation should take place."""

        # for element k of future_market a penalty is applied; relates to i+k element in real time series

        active = False      # indicates if there is a penalty or not

        # investigate if there are penalty payments for the recent market

        # is there a penalty payment for the INT charging market?
        if(self.future_market[k]=="INT-P" and (stand_still == True or (self.free_energy < self.used_capacity and inda.intraday_prices[k+i] > 0))): 

            # the revenue is turned negative and multiplied by the factor_penalty  # only for positive prices because negative will be revenue in this case and thats not right in the context of a penalty
            sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * float(inda.intraday_prices[k+i].copy()) * self.used_capacity_charging_pay  
            active = True
          
        elif(self.future_market[k]=="INT+P" and float(inda.intraday_prices[k+i]) > 0 and (stand_still == True or self.available_energy < self.used_capacity)): 

            # discharing: only for positive prices because negative will be revenue in this case
            sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * float(inda.intraday_prices[k+i].copy()) * self.used_capacity
            active = True
          
        elif(self.future_market[k]=="RES-P" and float(inda.nominal_price_RES_power[k+i]) > 0 and (stand_still == True or self.free_energy < self.used_capacity)):

            sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * float(inda.nominal_price_RES_power[k+i].copy()) / 4 * self.used_capacity_charging_pay    
            active = True
           
        elif(self.future_market[k]=="SR-E" and (float(inda.secondary_reserve_price_MWh_minus[k+i]) - inda.SR_trading_energy_for_direct_activation) > 0 and (stand_still == True or self.free_energy < self.used_capacity )): 

            sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * (float(inda.secondary_reserve_price_MWh_minus[k+i].copy())- inda.SR_trading_energy_for_direct_activation) * self.used_capacity_charging_pay         
            active = True
           
        elif(self.future_market[k]=="SR+E" and (float(inda.secondary_reserve_price_MWh_plus[k+i]) - inda.SR_trading_energy_for_direct_activation) > 0 and (stand_still == True or self.available_energy < self.used_capacity)):

            sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * float(inda.secondary_reserve_price_MWh_plus[k+i].copy()) * self.used_capacity          # in € / MWh * MWh
            active = True
           
        # for reserve markets, in reality it is the case, that they can charge within the reserve providing period - in the program this is not possible. Therefore it would be unfair to apply a penalthy directly after the market volume is not fulfilled.
        # So the compromise is that a reserve market must pay penalty in this program, if the capacity is too less to fulfill one timestamp activation. 
        # assuming the outage is identified in time and send to the TSO, the TSO would not activate the reserve anymore. Therefore, another penalty for the energy is not calculated. In reality, it could be different.

        elif(self.future_market[k]=="SR+P" and float(inda.secondary_reserve_price_MW_plus[k+i]) > 0 and ((self.available_energy < inda.simulation_power / 4) or stand_still==True)): 

            sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * float(inda.secondary_reserve_price_MW_plus[k+i].copy()) * inda.simulation_power   
            active = True
            
        elif(self.future_market[k]=="SR-P" and float(inda.secondary_reserve_price_MW_minus[k+i]) > 0 and (self.free_energy < inda.simulation_power / 4 * self.recent_RTE(inda,sim,i)/100 or stand_still==True)): 

            sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * float(inda.secondary_reserve_price_MW_minus[k+i].copy()) * inda.simulation_power       
            active = True
            
        elif(self.future_market[k]=="SR+-P" and (float(inda.secondary_reserve_price_MW_minus[k+i]) > 0 or float(inda.secondary_reserve_price_MW_plus[k+i]) > 0)): 

            if(float(inda.secondary_reserve_price_MW_minus[k+i]) > 0 and (self.free_energy < inda.simulation_power / 4 * self.recent_RTE(inda,sim,i)/100 or stand_still==True)):

                sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * float(inda.secondary_reserve_price_MW_minus[k+i].copy()) * inda.simulation_power        
                active = True

            if(float(inda.secondary_reserve_price_MW_plus[k+i]) > 0 and (self.available_energy < inda.simulation_power / 4 or stand_still==True)):
                
                sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * float(inda.secondary_reserve_price_MW_plus[k+i].copy()) * inda.simulation_power         
                active = True

        elif(self.future_market[k]=="PR" and float(inda.primary_reserve_price[k+i]) > 0 and
             (self.free_energy < inda.simulation_power / 4 * 0.99 * self.recent_RTE(inda,sim,i)/100 or
             self.available_energy < inda.simulation_power / 4 * 0.99
             or stand_still==True)): 

            sim.revenue[i+k] = sim.revenue[i+k] - inda.factor_penalty * float(inda.primary_reserve_price[k+i].copy()) * inda.simulation_power          
            active = True

        return active


    def check_overcompensation_charging(self,inda:input_data,sim:simulation_data,recent_t,index_future,index_best):

        """If charging is planned, it could be planned too much charging that some SOC or market limit is violated. This function identified such errors and corrects them."""

        # consider SOC min max
        # consider market conditions
        # operation = charging only: to meet a future discharge or reserve market, charging is needed

        # correct the variable self.recent_capacity by removing the last operation at index_best. This doesn't influance the original function because it's already at the end and self.recent_capacity is used locally only
        # if there is an overcompensation, the loop of planned_values can end directly
        self.overcompensation = False   
        store_recent_capacity = self.recent_capacity

        # removes the last charge operation
        self.remove_charge_operation(inda,index_best,recent_t,sim)

        if(self.future_market[index_future]=="SR+-P"):    

            # the storage wants to discharge and it is already enough capacity in here to do so - question: is there too much capacity in here?
            
            if(self.free_energy - store_recent_capacity < inda.storage_duration_SR * 0.99 * inda.simulation_power):     
            
                self.used_capacity_temp[index_best] = inda.simulation_capacity - inda.storage_duration_SR * 0.99 * inda.simulation_power - self.recent_capacity   
                self.overcompensation = True

        elif(self.future_market[index_future]=="PR"):

             # the storage wants to discharge and it is already enough capacity in here to do so - question: is there too much capacity in here?
            
            if(self.free_energy - store_recent_capacity < inda.storage_duration_PR * inda.simulation_power / 2):   
            
                self.used_capacity_temp[index_best] = inda.simulation_capacity - inda.storage_duration_PR / 2 * inda.simulation_power - self.recent_capacity  
                self.overcompensation = True

        # refresh recent_capacity in case of being changed previously
        self.recent_capacity = self.used_capacity_temp[index_best].copy()      
        
        # exceeding SOC=100 -> if ture, then limit the usable capacity
        if(self.recent_capacity + self.available_energy > inda.simulation_capacity):   

            self.used_capacity_temp[index_best] = inda.simulation_capacity - self.recent_capacity   
            self.overcompensation = True


    def check_overcompensation_discharging(self,inda:input_data,sim:simulation_data,recent_t,index_future,index_best):

        """If discharging is planned, it could be planned too much discharging that some SOC or market limit is violated. This function identified such errors and corrects them."""

        # consider SOC min max
        # consider market conditions
        # operation = discharging only: to meet a future discharge or reserve market, discharging is needed

        # correct the variable self.recent_capacity by removing the last operation at index_best. This doesn't influance the original function because it's already at the end and self.recent_capacity is used locally only
        # if there is an overcompensation, the loops of planned_values can end directly
        self.overcompensation = False   
        store_recent_capacity = self.recent_capacity

        # removes last discharge operation
        self.remove_discharge_operation(inda,index_best,recent_t)   

        if(self.future_market[index_future]=="SR+-P"):   

            # the storage wants to charge and it is already enough free capacity in here to do so - question: is there too less capacity in here?

            if(self.available_energy - store_recent_capacity < inda.storage_duration_SR * 0.99 * inda.simulation_power):    
            
                self.used_capacity_temp[index_best] = inda.storage_duration_SR * 0.99 * inda.simulation_power - self.recent_capacity  
                self.overcompensation = True

        elif(self.future_market[index_future]=="PR"):

            # the storage wants to charge and it is already enough free capacity in here to do so - question: is there too less capacity in here?

            if(self.available_energy - store_recent_capacity < inda.storage_duration_PR * inda.simulation_power / 2):    
            
                self.used_capacity_temp[index_best] = inda.storage_duration_PR / 2 * inda.simulation_power - self.recent_capacity   
                self.overcompensation = True

        # refresh recent_capacity in case of being changes previously
        self.recent_capacity = self.used_capacity_temp[index_best].copy()      
        
        # if the SOC < 0, then there must be a correction of the discharged capacity
        if(self.available_energy - self.recent_capacity < 0):    

            self.used_capacity_temp[index_best] = self.available_energy   
            self.overcompensation = True


    def remove_discharge_operation(self,inda,index_best,recent_t):

        """This function calculates the capacity without the last discharge operation. Grid limits are considered."""

        if(inda.RES_production[index_best + recent_t] / 1000 + inda.simulation_power > inda.grid_limit): 

            self.recent_capacity  = self.recent_capacity - 0.25 * ( inda.grid_limit - inda.RES_production[index_best + recent_t] / 1000)   

        else:

            self.recent_capacity = self.recent_capacity - 0.25 * inda.simulation_power
        

    def remove_charge_operation(self,inda,index_best,recent_t,sim:simulation_data):

        """This function calculates the capacity without the last charge operation. Less RES production than simulation power is considered."""

        if(self.future_market[index_best]=="RES-P" and inda.RES_production[index_best + recent_t] / 1000 < inda.simulation_power): # RES is providing less power than the storage could take

            self.recent_capacity = self.recent_capacity - 0.25 * inda.RES_production[index_best + recent_t] / 1000 * self.recent_RTE(inda,sim,recent_t) / 100     # charging capacity is limited to available capacity from RES, considering RTE

        else:

            self.recent_capacity = self.recent_capacity - 0.25 * inda.simulation_power * self.recent_RTE(inda,sim,recent_t) / 100

      
    def resize_future_market(self, end_market):

        """This function returns the adjusted future_market vector in case of reserve power participation and in every case the vector length that should be considered. It dependents on the last not inactive element and on reserve power markets."""

        end_market = 0

        for k in range(len(self.future_market)):

            # check if it is a reserve power market
            if (self.is_reserve_market(self.future_market[k])==True):  
                
                # shorten the vector to the reserve power element inclusive
                self.future_market = self.future_market[:k + 1]
                self.used_capacity_temp = self.used_capacity_temp[:k + 1]

                # add 15 more elements to fill the 4-h reserve power period
                for _ in range(15):

                    self.future_market = np.append(self.future_market, self.future_market[k])
                    self.used_capacity_temp = np.append(self.used_capacity_temp, self.used_capacity_temp[k])

                # set the end market to new length
                end_market = len(self.future_market)
                break

            # without reserve power markets: set the last non-inactive element as the last element considered
            elif self.future_market[k] != "INACTIVE":
                
                end_market = k + 1

        return end_market
    

    def adjust_charging_discharging_capacity(self, inda:input_data, i, k, sim:simulation_data):

        """This function determines the recent capacity_for_charging and capacity_for_discharging considering SOC, grid limit and RES production."""

        # SOC > 100 case
        if(self.capacity_for_charging + self.available_energy > inda.simulation_capacity):  

            self.capacity_for_charging = inda.simulation_capacity - self.available_energy

        # SOC < 0 case
        if(self.capacity_for_discharging > self.available_energy):  

            self.capacity_for_discharging = self.available_energy

        # grid limit
        if(self.capacity_for_discharging * 4 + inda.RES_production[i+k]/1000 > inda.grid_limit):  

            if(inda.RES_production[i+k]/1000 > inda.grid_limit):
                
                self.capacity_for_discharging = 0
                
            else:

                self.capacity_for_discharging = (inda.grid_limit - inda.RES_production[i+k]/1000) / 4

        # little RES production
        if(self.future_market[k]=="RES-P" and self.capacity_for_charging > (inda.RES_production[i+k]/1000) / 4): 

            self.capacity_for_charging = (inda.RES_production[i+k]/1000) / 4

        # for investigating money, pay inclusive RTE loss
        self.capacity_for_charging_pay = self.capacity_for_charging / (self.recent_RTE(inda,sim,i)/100 ) 
        

    def active_GO_Curtailment_charging(self,inda:input_data,sim,i,k):

        """If there is a GO curtailment for charging the BESS, this function calculates revenue and SOC."""

        # negative curtailments are indicated as charging = CURTAIL-
        sim.real_operation[i+k] = "CURTAIL-"     
        if(self.available_energy + self.capacity_for_charging <= inda.simulation_capacity): sim.SOC_sim[k+i] = (self.capacity_for_charging + self.available_energy) / inda.simulation_capacity * 100   
        else: return
       
        # revenues are payed by GO for the market the BESS would participate otherwise. Negative revenues are possible. Principle: no advantage & no disadvantage

        if(self.future_market[k] == "SR+E"):   

            sim.revenue[k+i] = sim.revenue[i+k] + (float(inda.secondary_reserve_price_MWh_plus[k+i]) - inda.SR_trading_energy_for_direct_activation) * self.used_capacity  
            # taxes and fees will not be compensated; they are subtracted
            sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.used_capacity  

        elif(self.future_market[k] == "INT+P"):   

            sim.revenue[i+k] = sim.revenue[i+k] + float(inda.intraday_prices[i+k]) * self.used_capacity          
            sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.used_capacity   
    

        # second, the charge operation of the GO mus be compensated in case of negative charging prices: then the storage would receive money for charging, otherwhise not.
        if(float(inda.intraday_prices[k+i])<0):    # best prices are < 0 in this matrix & € / MW

            sim.revenue[i+k] = sim.revenue[i+k] + (-1) * float(inda.intraday_prices[k+i]) * self.capacity_for_charging_pay # here capacity for charging is used because maybe more than orignially planned capacity can be used for curtailment
           
        # revenue for degradation:
        # the charging_pay_capacity is the one the power accounts for
        used_power = self.capacity_for_charging_pay * 4   
        # used / simulation_power: in case of SOC limit only a part of the power can be fed in; division by the power factor in case of greater capacities; divison by 2 because of a half cycle but storage_degradation_costs refer to full cycle; / 4 because of conversion from 15-min to 1 h
        sim.revenue[k+i] = sim.revenue[k+i] + used_power * inda.storage_degradation_costs * (used_power / inda.simulation_power) / inda.simulation_power_factor / 2 / 4   
       

    def active_GO_Curtailment_discharging(self,inda:input_data,sim:simulation_data,i,k):

        """If there is a GO curtailment for discharging the BESS, this function calculates revenue and SOC."""

        # positive curtailments are indicated as discharging = CURTAIL+
        sim.real_operation[i+k] = "CURTAIL+"     
        if(self.available_energy >= self.capacity_for_discharging): sim.SOC_sim[k+i] = (self.available_energy - self.capacity_for_discharging) / inda.simulation_capacity * 100
        else: return
        
        # revenues are payed by GO for the market the BESS would participate otherwise. Negative revenues are possible. Principle: no advantage & no disadvantage

        if(self.future_market[k] == "SR-E"):  

            sim.revenue[i+k] = sim.revenue[i+k] + (float(inda.secondary_reserve_price_MWh_minus[k+i]) - inda.SR_trading_energy_for_direct_activation) * self.used_capacity_charging_pay         
            # the GO would not compensate taxes
            sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.used_capacity_charging_pay   

        elif(self.future_market[k] == "INT-P"):    
        
            sim.revenue[i+k] = sim.revenue[i+k] + (-1) * float(inda.intraday_prices[i+k]) * self.used_capacity_charging_pay          
            sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.used_capacity_charging_pay   

        elif(self.future_market[k] == "RES-P"):    

            sim.revenue[i+k] = sim.revenue[i+k] + (-1) * float(inda.nominal_price_RES_power[i+k]) * self.used_capacity_charging_pay * 4      
            # for RES, no grid fees are considered, because the grid is not used. Thats why for creating the nominal prices, the fees were already subtracted from the intraday price. If the real revenue should be calculated, the revenue must be subtracted again by the grid fee, to cancel each other out: price - fee = revenue. revenue - fee = price
            sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.used_capacity_charging_pay    


        # second, the discharge operation of the GO must be compensated: in case of positive prices; in case of negative not
        if(float(inda.intraday_prices[k+i])>0):
            
            sim.revenue[i+k] = sim.revenue[i+k] + float(inda.intraday_prices[k+i]) * self.capacity_for_discharging
           
        # degradation compensation
        used_power = self.capacity_for_discharging * 4
         # used / simulation_power in case of SOC limit only a part of the power can be fed in; division by the power factor in case of greater capacity; divison by 2 because of a half cycle but storage_degradation_costs refer to full cycle; / 4 because of 15-min values in contrast to 1h reference
        sim.revenue[i+k] = sim.revenue[i+k] + used_power * inda.storage_degradation_costs * (used_power / inda.simulation_power) / inda.simulation_power_factor / 2 / 4    
       

    def follow_plan_operation(self,inda:input_data,sim:simulation_data,i,k):

        """This function calculates SOC and revenue by following the plan operation."""

        # copy the market to the output operation vector
        sim.real_operation[k+i] = self.future_market[k]

        # case INACTIVE: SOC stays the same
        if(self.future_market[k] == "INACTIVE"):  

            if(k+i>0): sim.SOC_sim[k+i] = sim.SOC_sim[k+i-1]
            else: 
                sim.SOC_sim[k+i] = 0
            
        # for every market the respective market price is reimbursed / payed. Fees are substracted and the SOC calculated

        elif(self.future_market[k] == "SR-E"):   

            # the trading for direct activation is subtrated. To ensure activation, the bid was lower than the average price
            sim.revenue[i+k] = sim.revenue[i+k] + (float(inda.secondary_reserve_price_MWh_minus[k+i]) - inda.SR_trading_energy_for_direct_activation) * self.used_capacity_charging_pay        
            sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.used_capacity_charging_pay    
            sim.SOC_sim[k+i] = (self.available_energy + self.used_capacity) / inda.simulation_capacity * 100
            
        elif(self.future_market[k] == "INT-P"):    

            sim.revenue[i+k] = sim.revenue[i+k] + (-1) * float(inda.intraday_prices[k+i]) * self.used_capacity_charging_pay          
            sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.used_capacity_charging_pay     
            sim.SOC_sim[k+i] = (self.available_energy + self.used_capacity) / inda.simulation_capacity * 100
            
        elif(self.future_market[k] == "RES-P"):   

            sim.revenue[i+k] = sim.revenue[i+k] + (-1) * float(inda.nominal_price_RES_power[k+i]) * self.used_capacity_charging_pay * 4       
            # for RES-P the fees were previously subtracted from the price. Now they are subtracted from the revenue to let the operation cancel each other out.
            sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.used_capacity_charging_pay    
            sim.SOC_sim[k+i] = (self.available_energy + self.used_capacity) / inda.simulation_capacity * 100

        elif(self.future_market[k] == "INT+P"):   

            sim.revenue[i+k] = sim.revenue[i+k] + float(inda.intraday_prices[k+i]) * self.used_capacity        
            # grid charges etc. must be payed for charging only
            sim.SOC_sim[k+i] = (self.available_energy - self.used_capacity) / inda.simulation_capacity * 100

        elif(self.future_market[k] == "SR+E"):  

            # the trading for direct activation is subtrated. To ensure activation, the bid was lower than the average price
            sim.revenue[i+k] = sim.revenue[i+k] + (float(inda.secondary_reserve_price_MWh_plus[k+i]) - inda.SR_trading_energy_for_direct_activation) * self.used_capacity         
            sim.SOC_sim[k+i] = (self.available_energy - self.used_capacity) / inda.simulation_capacity * 100

        elif(self.future_market[k]=="SR+P"): 

            sim.revenue[i+k] = sim.revenue[i+k] + float(inda.secondary_reserve_price_MW_plus[k+i]) * inda.simulation_power     
            
            # in case of activation, the energy is reimbursed by the average price
            if(float(inda.secondary_reserve_activation[i+k]) < 0):   #positive values = charging; we are here in discharging mode

                sim.revenue[i+k] = sim.revenue[i+k] + float(inda.secondary_reserve_price_MWh_plus[k+i]) * self.capacity_for_discharging 
                sim.SOC_sim[k+i] = (self.available_energy - self.capacity_for_discharging) / inda.simulation_capacity * 100
            
            else:

                if(k+i>0): sim.SOC_sim[k+i] = sim.SOC_sim[k+i-1]

        elif(self.future_market[k]=="SR-P"):

            sim.revenue[i+k] = sim.revenue[i+k] + float(inda.secondary_reserve_price_MW_minus[k+i]) * inda.simulation_power      
            
            # in case of activation, the energy is reimbursed by the average price
            if(float(inda.secondary_reserve_activation[i+k]) > 0):   #positive values = charging; we are here in charging mode

                sim.revenue[i+k] = sim.revenue[i+k] + float(inda.secondary_reserve_price_MWh_minus[k+i]) * self.capacity_for_charging_pay         
                sim.SOC_sim[k+i] = (self.available_energy + self.capacity_for_charging) / inda.simulation_capacity * 100
                sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.capacity_for_charging_pay     
                
            else:

                if(k+i>0): sim.SOC_sim[k+i] = sim.SOC_sim[k+i-1]

        elif(self.future_market[k]=="SR+-P"): # discharging reserve ; in every case penalthy because the availablity is affected. The program considers full power at one timestamp only for reserve markets so there must be no difference of partly outages

            sim.revenue[i+k] = sim.revenue[i+k] + inda.secondary_reserve_price_MW_minus[k+i] * inda.simulation_power        # in € / MW * MW
            sim.revenue[i+k] = sim.revenue[i+k] + inda.secondary_reserve_price_MW_plus[k+i] * inda.simulation_power         # in € / MW * MW
            
            # in case of activation, the energy is reimbursed by the average price
            if(float(inda.secondary_reserve_activation[i+k]) > 0):   #positive values = charging; we are here in charging mode

                sim.revenue[i+k] = sim.revenue[i+k] + float(inda.secondary_reserve_price_MWh_minus[k+i]) * self.capacity_for_charging_pay          
                sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.capacity_for_charging_pay     
                sim.SOC_sim[k+i] = (self.available_energy + self.capacity_for_charging) / inda.simulation_capacity * 100
            
            # in case of activation, the energy is reimbursed by the average price
            elif(float(inda.secondary_reserve_activation[i+k]) < 0):   #positive values = charging; we are here in discharging mode

                sim.revenue[i+k] = sim.revenue[i+k] + float(inda.secondary_reserve_price_MWh_plus[k+i]) * self.capacity_for_discharging        
                sim.SOC_sim[k+i] = (self.available_energy - self.capacity_for_discharging) / inda.simulation_capacity * 100
                
            else:

                if(k+i>0): sim.SOC_sim[k+i] = sim.SOC_sim[k+i-1]

        elif(self.future_market[k]=="PR" and inda.primary_reserve_price[k+i] > 0): 
            
            sim.revenue[i+k] = sim.revenue[i+k] + inda.primary_reserve_price[k+i] * inda.simulation_power       # in € / MW * MW
            
            if(float(inda.primary_reserve_activation[i+k]) < 0):    # discharging action; no additional revenue
                
                sim.SOC_sim[k+i] = (self.available_energy - self.capacity_for_discharging) / inda.simulation_capacity * 100
                
            elif(float(inda.primary_reserve_activation[i+k]) > 0):    # charging action; no additional revenue
                
                sim.SOC_sim[k+i] = (self.available_energy + self.capacity_for_charging) / inda.simulation_capacity * 100
                sim.revenue[i+k] = sim.revenue[i+k] - (inda.grid_charges_kWh[self.year_index] + inda.fees_BESS) / 100 * 1000 * self.capacity_for_charging_pay      # ct/kWh / 100 €/ct * 1000 MWh/kWh

            else:

                if(k+i>0): sim.SOC_sim[k+i] = sim.SOC_sim[k+i-1]

        if(sim.SOC_sim[k+i]>100): 
                
                print("SOC limited to 100 at",i+k)
                return


    def is_charging_market(self, market):

        """If the 'market' is a charging market, it returns true, otherwise false."""

        check = False

        if(market=="SR-E"): check = True
        elif(market=="RES-P"): check = True
        elif(market=="INT-P"): check = True

        return check
    

    def is_discharging_market(self, market):

        """If the 'market' is a discharging market, it returns true, otherwise false."""

        check = False

        if(market=="SR+E"): check = True
        elif(market=="INT+P"): check = True

        return check


    def power_supply_res_calc(self,inda:input_data,sim:simulation_data,k,i,stand_still):

        """This function calculates the power supply of RES from the BESS, called RES+P. It will be activated if needed and only in inactive periods of the storage system."""

        additional_discharge = 0    # in MWh
            
        if(sim.real_operation[i+k]=="INACTIVE"):  # if INACTIVE that timestamp, it is possible to provide power     

            # RES needs supply power if the RES production is less than the self-consumption because the power vector of RES is considered without self-consumption
            if(inda.renewable_technology=="pv" and inda.RES_production[i+k]< inda.self_consumption_pv):  

                additional_discharge = additional_discharge + (inda.self_consumption_pv - inda.RES_production[i+k])/ 4 / 1000    # kW / (4/h) / 1000 MW/kW
                
            elif(inda.renewable_technology=="wind" and inda.RES_production[i+k]< inda.self_consumption_wind):  

                additional_discharge = additional_discharge + (inda.self_consumption_wind - inda.RES_production[i+k]) / 4 / 1000

            elif(inda.renewable_technology=="wind_pv" and inda.RES_production[i+k]< (inda.self_consumption_wind+inda.self_consumption_pv)):  

                additional_discharge = additional_discharge + (inda.self_consumption_wind + inda.self_consumption_pv - inda.RES_production[i+k]) / 4 / 1000

        # RES+P was determined possible. Now the SOC & revenue will be calculated
        if(additional_discharge>0):
            
            # extra condition for very low SOC levels
            if((sim.SOC_sim[k+i] / 100 * inda.simulation_capacity - additional_discharge) < 0):

                revenue_energy = sim.SOC_sim[k+i] / 100 * inda.simulation_capacity
                sim.SOC_sim[k+i] = 0
                sim.real_operation[k+i] = "RES+P"
                sim.revenue[i+k] = sim.revenue[i+k] + (revenue_energy * inda.RES_consumption_costs / 100 * 1000)   

            else:   # standard case

                sim.SOC_sim[k+i] = (sim.SOC_sim[k+i] / 100 * inda.simulation_capacity - additional_discharge) / inda.simulation_capacity * 100
                sim.real_operation[k+i] = "RES+P"
                sim.revenue[i+k] = sim.revenue[i+k] + (additional_discharge * inda.RES_consumption_costs / 100 * 1000)    


    def overwrite_reserve_timestamps(self,inda:input_data,i):

        """To reach the user-defined number of cycles, already distributed reserve power timestamps with low cycle usage should be replaced by alternating charge and discharge timestamps with high cylce usage. This function is called annually."""

        i_values_start = (i) * 35063 
        i_values_end = (inda.calculation_period - i - 1) * 35063

        # create vectors again because the content was changed within last function
        self.charging_plan = inda.V_charging_operation[i_values_start : (len(inda.intraday_prices) - i_values_end)].copy()          # cut out one year vector of matrix; for the type of reserve power activation e.g. PR
        self.discharging_plan = inda.V_discharging_operation[i_values_start : (len(inda.intraday_prices) - i_values_end)].copy()    # cut out one year vector of matrix; for the type of reserve power activation e.g. PR
        
        for e in range(len(self.charging_plan)):

            # if all cycles are distributed: end function
            if(self.charge_cycle_stamp >= inda.investigated_timestamps_charge and self.discharge_cycle_stamp >= inda.investigated_timestamps_discharge):

                return      #   all cycles are distributed for this year


            # all charge timestamps are distributed -> switch to discharge timestamps
            if(self.charge_cycle_stamp >= inda.investigated_timestamps_charge):

                self.discharge_active = True

            # all discharge timestamps are distributed -> switch to charge timestamps
            elif(self.discharge_cycle_stamp > inda.investigated_timestamps_discharge):

                self.discharge_active = False

            # after one complete charge cycle is distributed, switch to discharge
            elif(self.last_charge + 1 <= self.charge_cycle_stamp):    

                self.last_charge = self.charge_cycle_stamp
                self.discharge_active = True

            # after one complete discharge cycle is distributed, switch to charge
            elif(self.last_discharge + 1 <= self.discharge_cycle_stamp):  

                self.last_discharge = self.discharge_cycle_stamp
                self.discharge_active = False

            # index of charging & discharging vector where best price value of V_charging_operation is investigated
            self.index_charge = np.argmin(self.charging_plan)        
            self.index_discharge = np.argmin(self.discharging_plan)       
            
            # case: distribute discharge
            if(self.discharge_active == True):

                # do not overwrite already distributed discharing or charging; only inactive or power reserve markets
                if(self.is_charging_market(self.plan[self.index_discharge]) == False and
                    self.is_discharging_market(self.plan[self.index_discharge]) == False and
                    self.discharging_plan[self.index_discharge] != 99999):   
                    
                    # remove the old power reserve market and replace it by a discharge market
                    self.remove_reserve_timestamp(self.plan[self.index_discharge],inda)
                    self.distribute_discharge_timestamp(inda,i,e)
                    
                else:   

                    self.charging_plan[self.index_discharge] = 99999
                    self.discharging_plan[self.index_discharge] = 99999

            # case: distribute charge
            else:

                # do not overwrite already distributed discharing or charging; only inactive or power reserve markets
                if(self.is_charging_market(self.plan[self.index_charge])==False and
                   self.is_discharging_market(self.plan[self.index_charge])==False and
                   self.charging_plan[self.index_charge] != 99999): 

                    # remove the old power reserve market and replace it by a charging market
                    self.remove_reserve_timestamp(self.plan[self.index_charge],inda)
                    self.distribute_charge_timestamp(inda,i,e)
                    
                else:   

                    self.charging_plan[self.index_charge] = 99999
                    self.discharging_plan[self.index_charge] = 99999
                   
    
    def remove_reserve_timestamp(self,market,inda:input_data):

        """A reserve power specified in 'market' will be replaced by a discharging/charging market. The partly considered timestamps of the previous saved reserve power market will be subtracted from the total amount of charge/discharge timestamps in this function."""
        
        # dependent on the power reserve market, some part of a cycle must be removed from distibution. charing & discharging are considered eqal effected for all power reserve markets because activation is unplanned

        if(market == "PR"):                                                       

            self.discharge_cycle_stamp = self.discharge_cycle_stamp - (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_PR_power / 2   
            self.charge_cycle_stamp = self.charge_cycle_stamp - (inda.investigated_timestamps_charge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_PR_power / 2

        elif(market == "SR+P"):

            self.discharge_cycle_stamp = self.discharge_cycle_stamp - (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_power_plus / 2  
            self.charge_cycle_stamp = self.charge_cycle_stamp - (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_power_plus / 2

        elif(market == "SR-P"):

            self.discharge_cycle_stamp = self.discharge_cycle_stamp - (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_power_minus / 2
            self.charge_cycle_stamp = self.charge_cycle_stamp - (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_power_minus / 2

        elif(market == "SR+-P"):

            self.discharge_cycle_stamp = self.discharge_cycle_stamp - (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_twice_power / 2
            self.charge_cycle_stamp = self.charge_cycle_stamp - (inda.investigated_timestamps_discharge * 0.5 + inda.investigated_timestamps_charge * 0.5) / inda.investigated_timestamps_SR_twice_power / 2

        elif(market != "INACTIVE"):

            print("ERROR: unknown market in remove_reserve_timestamp")
            return


    def sort_price_vectors(self,inda:input_data,sim):

        """Call this function to numberate the charging, discharging and power reserve nominal prices each. The result is stored in simulation_data.py."""

        # create new vectors
        sim.sorted_charge = np.full(len(inda.nominal_price_intraday), 99999,dtype=int)
        sim.sorted_discharge = np.full(len(inda.nominal_price_intraday), 99999,dtype=int)
        sim.sorted_reserve = np.full(len(inda.nominal_price_intraday), 99999,dtype=int)
        
        # assign values & convert them
        discharge_price = inda.M_best_discharging_prices[:,0].copy()
        discharge_price = np.array(discharge_price, dtype=float)              # convert to float
        discharge_price = np.round(discharge_price, decimals=3)               # round to 3 decimals
        charge_price = inda.M_best_charging_prices[:,0].copy()
        charge_price = np.array(charge_price, dtype=float)                    # convert to float
        charge_price = np.round(charge_price, decimals=3)                     # round to 3 decimals
        reserve_price = inda.M_best_power_prices[:,0].copy()
        reserve_price = np.array(reserve_price, dtype=float)              # convert to float
        reserve_price = np.round(reserve_price, decimals=3)               # round to 3 decimals

        # numberate each vector
        sim.sorted_discharge = self.highest_values_of_vector(discharge_price,len(discharge_price)-1)
        sim.sorted_reserve = self.highest_values_of_vector(reserve_price,len(reserve_price)-1)
        sim.sorted_charge = self.lowest_values_of_vector(charge_price,len(charge_price)-1)

    
    def refresh_available_energy(self,i,inda:input_data,sim:simulation_data,e):

        """Call this function to refresh the available and free energy of the storage based on the last SOC stored (i-1) and the future capacities planned to use 'last_capacity_used'."""

        # reset to default of last iteration stack i
        if(i==0): self.available_energy = 0    
        else: self.available_energy = sim.SOC_sim[i-1] / 100 * inda.simulation_capacity    
        self.free_energy = inda.simulation_capacity - self.available_energy  

        # if there are any plans already planned; they must be implemented until the recent timestamp:

        for j in range(e):      # until the recent investigation e - 1 the last planned capacities should be considered

            if(self.is_charging_market(self.future_market[j])==True):

                self.available_energy = self.available_energy + self.last_capacity_used[j]      # add energy in case of charging

            elif(self.is_discharging_market(self.future_market[j])==True):

                self.available_energy = self.available_energy - self.last_capacity_used[j]      # subtract energy in case of discharging


    def correct_plan_reserve_period(self, inda:input_data):

        """Call this function to correct the plan operation vector 'V_plan_operation' and delete all reserve market trades, which are not allowed: every 4h a trade on power reserve markets is possible."""

        for r in range(len(inda.V_plan_operation)):

            # +16 to make the first timestamp 0 active for power reserve trading
            if((r+16) % 16 != self.reserve_offset(inda)):    

                if(self.is_reserve_market(inda.V_plan_operation[r])==True):
                    
                    # replace not allowed power reserve trading periods by INACTIVE
                    inda.V_plan_operation[r] = "INACTIVE"



    def degradation_calculation(self, inda:input_data, sim:simulation_data):

        """This function calculates the degradation of power and capacity of the storage system and recalculates the nominal values dependent on degradation."""

        sim.average_SOC = 0                                 # average SOC
        sim.average_Q_d = 0                                 # average Q_d
        Q_d  = np.full(len(sim.SOC_sim), 0, dtype=float)    # every single discharged capacity is considered

        sim.count_cycles = 0                                # count cycles each replacement period

        sim.corrected_DOD = inda.DOD                        # initial but may be corrected
        sim.degradation = 0                                 # in % of QN each replacement period when the capacity unit of the BESS is replaced
        index_replace = 0                                   # index of replacement
        sim.nominal_capacity = 0                            # in MWh
        sim.corrected_P_loss = float(0)                     # in %; if the DOD user input is not valid or the cycles differ, P loss may be corrected
        sim.nominal_power = float(0)                        # nominal power each replacement period if the capacity unit of the BESS is replaced
        
        number_replacements = int(inda.calculation_period / inda.replacement_period)    # number of replacements
        sim.system_RTE_replacement  = np.full(number_replacements, 0, dtype=float)      # system RTE from inda converted to replacement period
        sim.capex_kWh_replacement  = np.full(number_replacements, 0, dtype=float)       # capex from inda converted to replacement period

        # for all replacements
        for k in range(len(inda.roundtrip_efficiency)):
            
            # there is a replacement in the recent year: the storage gets new RTE & capacity-dependent CAPEX
            if(k >= inda.replacement_period * index_replace):

                sim.system_RTE_replacement[index_replace] = inda.roundtrip_efficiency[inda.replacement_period * index_replace]  
                sim.capex_kWh_replacement[index_replace] = inda.capex_storage_kWh[inda.replacement_period * index_replace]
                index_replace = index_replace + 1

        index_replace = 0           # index of replacement
        self.d_idle = float(0)      # idling degradation
        self.d_cyc = float(0)       # cycling degradation

        # determine Q_d & avg_Q_d: simplified assumed constant for all replacements
        for k in range(len(sim.SOC_sim)):

            # because the non-used part of the BESS is charged, Q_d can be determined
            Q_d[k] = inda.simulation_capacity * (1 - sim.SOC_sim[k] / 100)
            sim.average_Q_d = Q_d[k] + sim.average_Q_d
            # / 100 to convert from percentages to half cycles / 2 to convert from half cycles to full cylces
            if(k > 0): sim.count_cycles = sim.count_cycles + (abs(sim.SOC_sim[k]-sim.SOC_sim[k-1]) / 100) / 2      
        
        # averaging
        sim.average_Q_d = sim.average_Q_d / len(sim.SOC_sim)

        # limit total cycle amount to replacement period: every 5 years the storage is replaced within a lifetime of 15 years: 3 replacements
        sim.count_cycles = sim.count_cycles / (inda.calculation_period / inda.replacement_period)

        # determination of Q_N based on User Input
        sim.nominal_capacity = sim.average_Q_d / (inda.DOD / 100)

        # check 1: if Q_N is already smaller than Q_U, then Q_N & DOD are adjusted previously
        if(sim.nominal_capacity < inda.simulation_capacity): 
            
            sim.nominal_capacity = inda.simulation_capacity
        
        sim.corrected_DOD = sim.average_Q_d / sim.nominal_capacity * 100   

        # assume the average SOC without degradation, recalculate later
        sim.average_SOC = (1 - sim.average_Q_d / sim.nominal_capacity) * 100

        # assumptions for DOD & SOC are made as well.

        for w in range(100):    # try to adjust 100 times maximal: so much adjustements are not needed

            if(w>=99): print("capacity adjustment is only approximately right.\n")

            # factors are dependend on avg_SOC & corrected_DOD
            self.calc_degradation_factors(inda,sim)    
            # sim.degradation in % total degradation of capacity within replacement period
            sim.degradation = self.d_cyc * sim.count_cycles + self.d_idle * (35063 / 4 / 24) * inda.replacement_period    
            absolut_degradation = (sim.degradation / 100) * sim.nominal_capacity
            # at minimum the usable + degradated capacity is needed; if there is even more, this is not problem
            nominal_capacity_min = inda.simulation_capacity + absolut_degradation
           
            if(nominal_capacity_min >= sim.nominal_capacity):

                # recalculate nominal capacity because user input of DOD was false
                sim.nominal_capacity = nominal_capacity_min
                sim.corrected_DOD = sim.average_Q_d / sim.nominal_capacity * 100
                sim.average_SOC = (1 - 2 * sim.average_Q_d / sim.nominal_capacity + (sim.nominal_capacity - absolut_degradation) / sim.nominal_capacity) * 50   # in %

            # the nominal capacity is greater than the minimum condition -> finish algorithm
            else:

                break

        # recalculate other formulars:
        self.calc_degradation_factors(inda,sim)    
        sim.degradation = self.d_cyc * sim.count_cycles + self.d_idle * (35063 / 4 / 24) * inda.replacement_period    
        absolut_degradation = (sim.degradation / 100) * sim.nominal_capacity
        sim.nominal_capacity = absolut_degradation + inda.simulation_capacity
        sim.degradation = absolut_degradation / sim.nominal_capacity * 100
        sim.corrected_DOD = sim.average_Q_d / sim.nominal_capacity * 100
        sim.average_SOC = (1 - 2 * sim.average_Q_d / sim.nominal_capacity + (sim.nominal_capacity - absolut_degradation) / sim.nominal_capacity) * 50   # in %
      
        sim.corrected_P_loss = 0.000036927 * math.exp(0.08657 * sim.corrected_DOD) * pow(sim.count_cycles, 0.00434 * 293 - 0.008 * sim.corrected_DOD - 0.1504)
        sim.nominal_power = inda.simulation_power / (1 - sim.corrected_P_loss / 100.0) / (inda.pu_pe / 100.0)

        
    def calc_degradation_factors(self, inda:input_data, sim:simulation_data):

        """Calculates the idling and cycling capacity degradation d_idle & d_cyc in %, dependent on the technology of the storage system, defined in inda. Possible are: LFP, NMC, LTO, LMO."""

        A = 0   # factor idle
        B = 0   # factor idle
        C = 0   # factor idle
        D = 0   # factor cycle
        E = 0   # factor cycle

        # determines factors based on measurements of a study

        if(inda.technology_storage_system=="Li-Ion (LFP)"):

            A = 0.0000043400
            B = 0.0000273000
            C = 0.0000145000
            D = 0.0004830000
            E = 0.0000238000

        elif(inda.technology_storage_system=="Li-Ion (NMC)"):

            A = 0.0000046700
            B = 0.0000294000
            C = 0.0000156000
            D = 0.0005170000
            E = 0.0000193000
        
        elif(inda.technology_storage_system=="Li-Ion (LTO)"):

            A = 0.0000033600
            B = 0.0000212000
            C = 0.0000112000
            D = 0.0002070000
            E = 0.0000081200

        elif(inda.technology_storage_system=="Li-Ion (LMO)"):

            A = 0.0000080300
            B = 0.0000461000
            C = 0.0000174000
            D = 0.0006810000
            E = 0.0000343000

        # calculate degradation coefficients out of the factors
        self.d_idle = (A * (sim.average_SOC/100) * (sim.average_SOC/100) + B * (sim.average_SOC/100) + C) * 100    # in %
        self.d_cyc = (D * (sim.corrected_DOD/100) * (sim.corrected_DOD/100) + E * (sim.corrected_DOD/100)) * 100   # in %


    def calc_annual_costs_revenue(self, inda:input_data, sim:simulation_data):

        """This function calculates the financial output of the program: Costs, revenue, cash flow, NPV, IRR and annual production and consumption are determined annually."""

        sim.annual_costs = np.full(inda.calculation_period, 0, dtype=float)             # all costs of the calculation period
        sim.annual_production = np.full(inda.calculation_period, 0, dtype=float)        # annual sum of released power of storage
        sim.annual_consumption = np.full(inda.calculation_period, 0, dtype=float)       # annual sum of consumed power of storage
        sim.annual_revenue = np.full(inda.calculation_period, 0, dtype=float)           # annual sum of revenue function

        average_nominal_power = 0
        index_replace = 0 
        index_real = 0

        for t in range(inda.calculation_period):

            for e in range(35063):  # one year

                index_real = e + t * 35063

                if(t>0 or e>0):

                    # if there is a positive revenue, losses due to non optimal market behaviour = losses between theorie and praxis are deducted as a percentage. For costs, this is not the case, otherwise there would be less costs in praxis
                    if(sim.revenue[t] > 0): sim.annual_revenue[t] = sim.annual_revenue[t] + sim.revenue[index_real] * (1 - inda.loss_not_optimal_market_behavior / 100)
                    else: sim.annual_revenue[t] = sim.annual_revenue[t] + sim.revenue[index_real] 

                    # if the recent SOC is lower than before, there was a discharge, otherwise a charge. Production and consumtion are calculated based on SOC differences
                    if(sim.SOC_sim[index_real] < sim.SOC_sim[index_real - 1]):     

                        sim.annual_production[t] = sim.annual_production[t] + (sim.SOC_sim[index_real - 1] - sim.SOC_sim[index_real]) / 100 * inda.simulation_capacity 

                    else:

                        sim.annual_consumption[t] = sim.annual_consumption[t] + (sim.SOC_sim[index_real] - sim.SOC_sim[index_real - 1]) / 100 * inda.simulation_capacity  


        average_nominal_power = sim.nominal_power  # because the nominal power is constant over all replacements

        for t in range(inda.calculation_period):

            # investment costs at the project's start.
            if(t==0):   

                sim.annual_costs[t] = sim.annual_costs[t] + average_nominal_power * 1000 * inda.capex_storage_kW[0]  
                sim.annual_costs[t] = sim.annual_costs[t] - inda.initial_discount      
                sim.annual_costs[t] = sim.annual_costs[t] + inda.initial_costs

            # costs for the replacement of the capacity unit of the BESS
            if(t >= inda.replacement_period * index_replace): 
            
                sim.annual_costs[t] = sim.annual_costs[t] + inda.capex_storage_kWh[t] * 1000 * sim.nominal_capacity  
                # the capacity unit used within the replacement period is still of some value
                if(index_replace > 0): sim.annual_costs[t] = sim.annual_costs[t] - inda.residual_value * 1000 * sim.nominal_capacity * (1 - sim.degradation / 100)      
                index_replace = index_replace + 1

            # opex must be paid annually
            sim.annual_costs[t] = sim.annual_costs[t] + inda.opex_storage_kW[t] * 1000 * average_nominal_power
            sim.annual_costs[t] = sim.annual_costs[t] + inda.opex_storage_MWh * (sim.annual_consumption[t] + sim.annual_production[t])

        # at the end of operation: sell the capacity unit once more for the residual value
        sim.annual_costs[-1] = sim.annual_costs[-1] - inda.residual_value * 1000 * sim.nominal_capacity * (1 - sim.degradation / 100)        
        
        # create a cash-flow
        sim.cashflow = sim.annual_revenue.copy() - sim.annual_costs.copy()    

        # calculate NPV and IRR
        dicount_decimal = inda.discount_rate / 100
        sim.NPV = npf.npv(dicount_decimal, sim.cashflow)
        sim.IRR = npf.irr(sim.cashflow) * 100


    def reserve_offset(self, inda:input_data):

        """Due to the consideration of nominal years, the 4-h power reserve period does not always start at t=0 but with an offset. The offset will be returned."""
        
        offset = 0

        if(inda.secondary_reserve_energy_active==True):

            for i in range(16):

                if(inda.secondary_reserve_price_MW_minus[i]!=inda.secondary_reserve_price_MW_minus[0]): return i

        return offset
    

    def recent_RTE(self,inda:input_data,sim:simulation_data,i):

        """The system RTE is reduced linearly for SOC > 80 % until a maximum user-defined reduction limit at SOC = 100 % is reached. The function returns the recent valid RTE dependent on SOC, the year of capacity-unit-replacement and annual degradation effects."""

        RTE = inda.roundtrip_efficiency[self.year_index]
        RTE_degradation = 0

        if(i > 0):  # i = timestamp

            if(sim.SOC_sim[i-1] > 80):  # last SOC was greater than 80 % -> reduce SOC linear

                # 80 % SOC -> inda.roundtrip_efficiency[i]
                # 100 % SOC -> (inda.roundtrip_efficiency[i] - 26) /// / 20 because of the last 20 percentage points
                RTE_degradation = inda.RTE_SOC_dependency - inda.RTE_SOC_dependency * (100 - sim.SOC_sim[i-1]) / 20

        RTE = RTE - RTE_degradation

        return RTE
