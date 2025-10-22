# import libraries and dependet classes
import tkinter as tk
from excel_data import excel_data
import numpy as np
import math as m
from input_data import input_data

# create an Excel Object
xlx = excel_data(input_data)

# create the main class of the file
class Grafics:

    def __init__(self, inda: input_data):

        """Call for initialization"""

        self.inda = inda
        self.pages = []
        self.heads = []
        self.buttons = []
        self.infos = []
        self.inputs = []
        self.errors = []
        self.labels = []

    def show_frame(self, frame):

        """show next page"""

        frame.tkraise()

    
    def start_simulation(self, inda, root):

        """end grafical interface"""

        inda.start_simulation = True  
        root.destroy()


    def technology_storage_system_NMC(self, inda, button):

        """klick on button Li-Ion (NMC)"""

        # change variable in input_data.py
        inda.technology_storage_system = "Li-Ion (NMC)"
        # change button colour to green
        button.config(bg="green")          
        # show next page         
        self.show_frame(self.pages[1])


    def technology_storage_system_LFP(self, inda, button):

        """klick on button Li-Ion (LFP)"""

        inda.technology_storage_system = "Li-Ion (LFP)"
        button.config(bg="green")                  
        self.show_frame(self.pages[1])


    def submit_year(self, input_year, inda, button):

        """klick on submit button of the start year year_commissioning."""

        # get user input from input field
        user_input = input_year.get()               

        # in case of unexspected user input the program should not crash
        try:

            # convert user input to integer
            year = int(user_input)

            # check if input is valid
            if 2024 < year < 2041:

                inda.year_commissioning = year
                button.config(bg="green")  
                self.show_frame(self.pages[2])

            else:

                button.config(bg="red")

        # in case of unexspected user input, the button turns red
        except ValueError:
            
            button.config(bg="red")


    def submit_period(self, input_calculation_period, input_replacement_period, inda, button):

        """Klick on submit button of caclulation & replacement period."""

        # get user inputs from input field
        user_calculation = input_calculation_period.get() 
        user_replacement = input_replacement_period.get()  

        try:

            # convert user input to integers
            period_calc = int(user_calculation)
            period_replace = int(user_replacement)

            # check if user input is valid
            if 0 < period_calc < 51 and (period_calc + inda.year_commissioning) <= 2050:

                # store result in input_data.py
                inda.calculation_period = period_calc
                inda.end_year = period_calc + inda.year_commissioning

                if 0 < period_replace and period_replace <= period_calc and period_calc % period_replace == 0:

                    inda.replacement_period = period_replace
                    button.config(bg="green")  
                    self.show_frame(self.pages[3])

                else:

                    button.config(bg="red")

            else:

                button.config(bg="red")

        # unexspected user input
        except ValueError:

            button.config(bg="red")


    def submit_intraday(self, inda, button):

        """Klick on Intraday Button."""

        if(inda.intraday_active == True):
            
            inda.intraday_active = False
            button.config(bg="white") 
            
        else:

            inda.intraday_active = True
            button.config(bg="green") 


    def submit_primary_reserve(self, inda, button, button_purchase):

        """Klick on Primary Reserve Button."""

        if(inda.primary_reserve_active == True):
            
            inda.primary_reserve_active = False
            button.config(bg="white") 
            
        else:

            inda.primary_reserve_active = True
            button.config(bg="green") 
            # primary reserve is only possible if electricity can be purchased from the grid
            inda.purchase_active = True
            button_purchase.config(bg="green") 


    def submit_secondary_reserve(self, inda:input_data, button, button6, button_SR_power_twice):

        """Klick on Button to activate Secondary Reserve."""

        if(inda.secondary_reserve_power_active == True):

            inda.secondary_reserve_power_active = False
            button.config(bg="white")
            
        else:

            button.config(bg="green") 
            inda.secondary_reserve_power_active = True
            button6.config(bg="green") 
            inda.purchase_active = True
            inda.SR_simultaneously_active = False
            button_SR_power_twice.config(bg="white")


    def submit_secondary_reserve_energy(self, inda: input_data, button, button6):

        """Klick on button to activate Secondary Reserve Energy trading independent from the power reserve markets."""

        if(inda.secondary_reserve_energy_active == True):

            inda.secondary_reserve_energy_active = False
            button.config(bg="white")
            
        else:

            button.config(bg="green") 
            inda.secondary_reserve_energy_active = True
            button6.config(bg="green") 
            inda.purchase_active = True

    
    def submit_secondary_reserve_power_twice(self, inda:input_data, button, button_purchase, button_SR_power):

        """Klick on Button to offer positive and negative Secondary Reserve Power at the same time."""

        if(inda.SR_simultaneously_active == True):

            inda.SR_simultaneously_active = False
            button.config(bg="white")
            
        else:

            button.config(bg="green") 
            inda.SR_simultaneously_active = True
            button_purchase.config(bg="green") 
            inda.purchase_active = True
            inda.secondary_reserve_power_active = False
            button_SR_power.config(bg="white")


    def submit_purchase(self, inda:input_data, button, button35, button_primary, button_SR_twice, button_SR_energy):

        """Klick on button to activate purchasing energy from electricity markets."""

        if(inda.purchase_active == True):

            inda.purchase_active = False
            button.config(bg="white")
            inda.secondary_reserve_power_active = False
            button35.config(bg="white")
            button_primary.config(bg="white")
            inda.primary_reserve_active = False
            inda.SR_simultaneously_active = False
            button_SR_twice.config(bg="white")
            inda.secondary_reserve_energy_active = False
            button_SR_energy.config(bg="white")

        else:

            inda.purchase_active = True
            button.config(bg="green") 


    def submit_selfconsumption(self, inda, button):

        """Klick on button to activate that RES can consume power from the BESS."""

        if(inda.selfconsumption_active == True):
            
            inda.selfconsumption_active = False
            button.config(bg="white") 
            
        else:

            inda.selfconsumption_active = True
            button.config(bg="green") 


    def submit_market_strategies(self, button, inda:input_data):

        """Klick on button so submit all chosen markets."""
        
        # if no strategy or the wrong strategies are selected, red button
        if(inda.intraday_active == False and inda.primary_reserve_active==False and inda.secondary_reserve_power_active == False and inda.secondary_reserve_energy_active == False and inda.SR_simultaneously_active == False):
            
            button.config(bg="red")
            return

        # next page
        self.show_frame(self.pages[4]) 
    

    def submit_main_storage_parameters(self, inda:input_data, button, input_min_capacity, input_powerfactor_min):
        
        """Klick on button to submit capacity and power factor."""

        try:

            # convert user input to float
            min_capacity = float(input_min_capacity.get())
            powerfactor_min = float(input_powerfactor_min.get())
            
            k = False
            
            # check capacity
            if 1 <= min_capacity <= 1000: 

                inda.capacity_storage_min = min_capacity

            else:

                button.config(bg="red")
                print("Choose the capacity between 1 and 1000 MWh! The optimum range is: 2 to 10 MWh.")
                k = True


            # check power factor
            if 0.01 <= powerfactor_min <= 10:

                if(powerfactor_min<2 and inda.SR_simultaneously_active==True):

                    print("Warning: Better enter a ratio of usable capacity / usable power >= 2 because you seleted participation at simultaneous positiv and negative Secondary Reserve Power Markets.\n")

                if(powerfactor_min<1 and inda.secondary_reserve_power_active==True):

                    print("Warning: Better enter a ratio of usable capacity / usable power >= 1 because you seleted participation at Secondary Reserve Power Markets.\n")
                    
                if(powerfactor_min<0.5 and inda.primary_reserve_activation==True):

                    print("Warning: Better Enter a ratio of usable capacity / usable power >= 1 because you seleted participation at the PR Power Markets. The selection can lead to an increase of penalty payments.\n")
                    
                inda.powerfactor_min = powerfactor_min

            else:

                button.config(bg="red")
                k = True
            
            # if everything is okay, store results and change the page
            if not k:

                # set dependent variables
                inda.simulation_capacity = inda.capacity_storage_min
                inda.simulation_power_factor = inda.powerfactor_min
                inda.simulation_power = inda.simulation_capacity / inda.simulation_power_factor
                
                self.show_frame(self.pages[6])
                
        except ValueError:

            button.config(bg="red")
            print("ValueError: Type in numerical values.")


    def submit_detailed_financial_storage_parameters(self, inda: input_data, button, input_opex_storage_MWh, self_discharge_tk):

        """Klick on button to load CAPEX & OPEX from Excel files, check and store results."""

        try:

            # load capex (2x) & opex (kW) of the BESS as vectors dependent on hours of the system, power and the years of operation
            xlx.load_capex_opex(inda)  

            opex_storage_MWh = float(input_opex_storage_MWh.get())
            
            k = False
            
            # check capex kW  // 0 is allowed if price is given in either kW or kWh only
            if 0 > inda.capex_storage_kW[0] or inda.capex_storage_kW[0] > 5000:

                button.config(bg="red")
                k = True

            # check capex kWh; // 0 is allowed if price is given in either kW or kWh only
            if 0 > inda.capex_storage_kWh[0] or inda.capex_storage_kWh[0] > 5000:
                
                button.config(bg="red")
                k = True

            # check opex kWh // 0 is allowed if price is given in either kW or kWh only
            if 0 <= opex_storage_MWh < 300 and opex_storage_MWh <= inda.capex_storage_kWh[0]:

                inda.opex_storage_MWh = opex_storage_MWh

            else:

                button.config(bg="red")
                k = True

            # check opex kW // 0 is allowed if price is given in either kW or kWh only
            if 0 > inda.opex_storage_kW[0] or inda.opex_storage_kW[0] > 300 or inda.opex_storage_kW[0] > inda.capex_storage_kW[0]:
                
                button.config(bg="red")
                k = True

            # if okay, then next page, load self-discharge rate dependent on the previous selected technology
            if not k:
                
                if(inda.technology_storage_system == "Li-Ion (NMC)"):

                    inda.self_discharge = 1

                elif(inda.technology_storage_system == "Li-Ion (LFP)"):

                    inda.self_discharge = 4

                elif(inda.technology_storage_system == "Li-Ion (LTO)"):

                    inda.self_discharge = 2

                elif(inda.technology_storage_system == "Li-Ion (LMO)"):

                    inda.self_discharge = 3

                self_discharge_tk.set(str(inda.self_discharge))

                self.show_frame(self.pages[5])
                
        except ValueError:

            # wrong input
            button.config(bg="red")
            print("ValueError: Type in valid numbers!")
        

    def submit_detailed_technical_storage_parameters(self, inda: input_data, button, input_DOD, input_pu_pe, input_recover_time, input_cycles_per_year, input_self_discharge, input_recovery_activation, input_rte_annual, input_rte_soc, RES_consumption_txt, RES_consumption_input, RES_consumption_unit, PR_duration_input, PR_duration_txt, PR_duration_unit, SR_duration_input, SR_duration_txt, SR_duration_unit, lower_bid_input, lower_bid_txt, lower_bid_unit):
        
        """Klick on button to submit technical storage parameters as DOD or target cycles per year. The input is checked and stored."""

        try:

            # convert user inputs into storable variables
            DOD = float(input_DOD.get())
            pu_pe = int(input_pu_pe.get())
            recover_time = int(input_recover_time.get())
            cycles_per_year = int(input_cycles_per_year.get())
            self_discharge = float(input_self_discharge.get())
            recovery_activation = float(input_recovery_activation.get())
            rte_annual = float(input_rte_annual.get())
            rte_soc = float(input_rte_soc.get())
            
            k = False

            #check annual rte degradation
            if 0 <= rte_annual <= 2:

                inda.RTE_annual_degradation = rte_annual

            else:

                button.config(bg="red")
                k = True

             #check rte soc dependecy
            if 1 <= rte_soc <= 50:

                inda.RTE_SOC_dependency = rte_soc

            else:

                button.config(bg="red")
                k = True
            
            #check self-discharge
            if 0 <= self_discharge <= 30:

                inda.self_discharge = self_discharge

            else:

                button.config(bg="red")
                k = True

            # check DOD
            if 10 <= DOD <= 100:

                inda.DOD = DOD

            else:

                button.config(bg="red")
                k = True

            # check pu_pe = usable power / EOL power
            if 10 <= pu_pe <= 100:

                inda.pu_pe = pu_pe

            else:

                button.config(bg="red")
                k = True

            # check recover_time
            if 0 <= recover_time <= 120:

                inda.recovery_time = recover_time

            else:

                button.config(bg="red")
                k = True

            # check recover activation
            if 0.25 < recovery_activation <= 10:

                inda.recovery_activation = recovery_activation

            else:

                button.config(bg="red")
                k = True

            # check cycles
            if 10 <= cycles_per_year <= 10000:

                inda.cycles_per_year = cycles_per_year

            else:

                button.config(bg="red")
                k = True

            # load system RTE from Excel file dependent on user inputs
            xlx.load_system_RTE(inda) 

            # check roundtrip_efficiency
            if 50 > inda.roundtrip_efficiency[0] or inda.roundtrip_efficiency[0] > 100:
            
                button.config(bg="red")
                k = True

            # if some cases are deactivated by the user, some input variables are not needed anymore
            if(inda.selfconsumption_active==False):

                # do not show this item on screen: it is not needed anymore because self-consumption is inactive
                RES_consumption_input.place_forget()
                RES_consumption_txt.place_forget()
                RES_consumption_unit.place_forget()

            if(inda.primary_reserve_active==False):

                PR_duration_input.place_forget()
                PR_duration_txt.place_forget()
                PR_duration_unit.place_forget()

            if(inda.secondary_reserve_power_active==False and inda.SR_simultaneously_active==False):

                SR_duration_input.place_forget()
                SR_duration_txt.place_forget()
                SR_duration_unit.place_forget()

            if(inda.secondary_reserve_energy_active==False):

                lower_bid_input.place_forget()
                lower_bid_txt.place_forget()
                lower_bid_unit.place_forget()

            # if everything is okay, then next page
            if not k:

                self.show_frame(self.pages[7])
                
        except ValueError:

            # wrong input exceptions
            button.config(bg="red")
            print("ValueError: Type in valid values!")

    
    def submit_other_electrical_parameters(self, inda, button, input_grid_limit):

        """Klick on this button to submit the grid limit."""

        try:

            # convert user inputs into storable variables
            grid_limit = float(input_grid_limit.get())

            if (0.1 < grid_limit <= 999999) or grid_limit == (-1):

                inda.grid_limit = grid_limit

                # 1 TW is never exceeded
                if(grid_limit == -1): inda.grid_limit = 999999     

                if(inda.purchase_active==True or inda.selfconsumption_active == True):

                    self.show_frame(self.pages[8])

                else:

                    self.show_frame(self.pages[9])

            else:

                button.config(bg="red")

        except ValueError:

            button.config(bg="red")
            print("ValueError: Type in valid values!")


    def submit_taxes_and_duties(self, inda, button, input_RES_consumption_costs, input_fees_BESS):

        """Klick on this button to submit taxes and duties."""

        try:

            # convert user inputs into storable variables
            RES_consumption_costs = float(input_RES_consumption_costs.get())
            fees_BESS = float(input_fees_BESS.get())
            
            k = False

            if (0 <= RES_consumption_costs < 100):

                inda.RES_consumption_costs = RES_consumption_costs
            
            else:

                button.config(bg="red")
                k = True

            if (0 <= fees_BESS < 10):

                inda.fees_BESS = fees_BESS
            
            else:

                button.config(bg="red")
                k = True


            if (k == False):
                
                kk=[True]
                # load grid charges from Excel files
                xlx.load_grid_charge_vectors(inda, kk)

                if(kk[0]==True):

                    self.show_frame(self.pages[9])

                else:

                    button.config(bg="red")

        except ValueError:

            button.config(bg="red")
            print("ValueError: Type in valid values!")


    def submit_other_financial_parameters(self, inda: input_data, button, input_discount, input_discount_rate, input_initial_costs, input_residual, input_penalty, input_non_optimal_market, input_degradation_cost):

        """Klick on this button to submit financial parameters as degradation costs, discount rate or penalty payments."""

        try:

            # convert user inputs into storable variables
            discount = float(input_discount.get())
            discount_rate = float(input_discount_rate.get())
            initial_costs = float(input_initial_costs.get())
            residual = float(input_residual.get())
            penalty = float(input_penalty.get())
            non_optimal_market = float(input_non_optimal_market.get())
            degradation_cost = float(input_degradation_cost.get())

            k = False

            if (0 <= degradation_cost <= 100):

                inda.storage_degradation_costs = degradation_cost
            
            else:

                button.config(bg="red")
                k = True

            if (0 <= non_optimal_market <= 100):

                inda.loss_not_optimal_market_behavior = non_optimal_market
            
            else:

                button.config(bg="red")
                k = True

            if (1 <= penalty <= 5):

                inda.factor_penalty = penalty
            
            else:

                button.config(bg="red")
                k = True

            if (-100 <= residual <= 200):

                inda.residual_value = residual
            
            else:

                button.config(bg="red")
                k = True

            if (0 <= discount < 1000000):

                inda.initial_discount = discount
            
            else:

                button.config(bg="red")
                k = True

            if (0 <= discount_rate < 20):

                inda.discount_rate = discount_rate
            
            else:

                button.config(bg="red")
                k = True

            if (0 <= initial_costs < 100000000):

                inda.initial_costs = initial_costs
            
            else:

                button.config(bg="red")
                k = True


            if (k == False):
                
                self.show_frame(self.pages[10])
                
            else:

                button.config(bg="red")

        except ValueError:

            button.config(bg="red")
            print("ValueError: Type in valid values.")


    def choose_wind_pv(self, inda, button21, button22, button23):

        """Klick on this button to select wind and photovoltaic as renewable technology."""

        inda.renewable_technology = "wind_pv"
        button21.config(bg="white")
        button22.config(bg="white")
        button23.config(bg="green")


    def choose_wind(self, inda, button21, button22, button23):

        """Klick on this button to select wind as renewable technology."""

        inda.renewable_technology = "wind"
        button21.config(bg="green")
        button22.config(bg="white")
        button23.config(bg="white")


    def choose_pv(self, inda, button21, button22, button23):

        """Klick on this button to select photovoltaic as renewable technology."""

        inda.renewable_technology = "pv"
        button21.config(bg="white")
        button22.config(bg="green")
        button23.config(bg="white")


    def submit_simulation_paramters(self, inda:input_data, button, b_primary, b_srpm, b_srpp, b_srep, b_srem, loss_pv, loss_wind, pr_activation, sr_activation, label_self_pv_input, label_self_pv_txt, label_self_pv_unit, label_self_wind_input, label_self_wind_txt, label_self_wind_unit):

        """Submit the renewable technology and check if other parameters can be omitted dependent on user input."""

        try:


            if(inda.renewable_technology != "pv" and inda.renewable_technology != "wind" and inda.renewable_technology != "wind_pv"):

                button.config(bg="red")
                print("ERROR in submit_simulation_paramters: technology not found.")
            
            else:

                # if some settings are disabled, the related elements will not be displayed
                if(inda.primary_reserve_active==False): 
                    
                    b_primary.place_forget()
                    pr_activation.place_forget()

                if(inda.secondary_reserve_power_active==False and inda.SR_simultaneously_active == False): 
                    
                    b_srpm.place_forget()
                    b_srpp.place_forget()
                    sr_activation.place_forget()

                if(inda.secondary_reserve_energy_active==False and inda.secondary_reserve_power_active==False and inda.SR_simultaneously_active == False): 
                    
                    b_srep.place_forget()
                    b_srem.place_forget()

                if(inda.renewable_technology=="pv"): loss_wind.place_forget()
                if(inda.renewable_technology=="wind"): loss_pv.place_forget()

                if(inda.selfconsumption_active==False):

                    label_self_pv_input.place_forget()
                    label_self_pv_txt.place_forget()
                    label_self_pv_unit.place_forget()
                    label_self_wind_input.place_forget()
                    label_self_wind_txt.place_forget()
                    label_self_wind_unit.place_forget()

                if(inda.renewable_technology == "pv" or inda.renewable_technology == "wind_pv"):
                    
                    # show pv page
                    self.show_frame(self.pages[11])

                else:   
                    
                    # show wind page because pv is not included in the simulation
                    self.show_frame(self.pages[12])

        except ValueError:

            button.config(bg="red")   
            print("ERROR in submit_simulation_paramters: unknown exception")


    def submit_pv_parameters(self, inda, button, input_self_consumption_pv):

        """Klick on this button to submit power and self-consumption of the PV plant."""

        try:
            
            kk=[True]
            # the pv power is loaded from an Excel file in 15-min resolution of one year.
            xlx.load_power_pv(inda, kk)

            if(kk[0]==False): 

                button.config(bg="red")
                print("PV data not loaded completly")
                return
            
            self_consumption_pv = float(input_self_consumption_pv.get())

            if(1 < self_consumption_pv < 1000):

                inda.self_consumption_pv = self_consumption_pv

            else:
                
                button.config(bg="red")
                return

            if(inda.renewable_technology=="wind_pv"):

                self.show_frame(self.pages[12])

            else:

                self.show_frame(self.pages[13])

        except ValueError:
    
            button.config(bg="red")
            print("value error")

    
    def submit_wind_parameters(self, inda, button, input_self_consumption_wind):

        """Klick on this button to submit power and self-consumption of the wind plant."""

        try:
            
            kk=[True]
            # the wind power is loaded from an Excel file in 15-min resolution of one year.
            xlx.load_power_wind(inda, kk)

            if(kk[0]==False): 

                button.config(bg="red")
                print("Wind data not loaded completely.")
                return

            self_consumption_wind = float(input_self_consumption_wind.get())

            if(1 < self_consumption_wind < 1000):

                inda.self_consumption_wind = self_consumption_wind

            else:
                
                button.config(bg="red")
                return

            self.show_frame(self.pages[13])

        except ValueError:
    
            button.config(bg="red")
            print("value error")

    
    def submit_market_prices(self, inda: input_data, button):
        
        """Klick on this button to load market prices from Excel files, dependent on the markets chosen."""

        try:

            button.config(bg="yellow")

            kk=[True]
            # always load the intraday data
            xlx.load_intraday(inda, kk)

            if(inda.primary_reserve_active==True):

                xlx.load_primary_prices(inda, kk)

            if(inda.secondary_reserve_power_active==True or inda.secondary_reserve_energy_active==True):

                xlx.load_secondary_prices(inda, kk)

            if(kk[0]==True):

                self.show_frame(self.pages[14])

            else:

                button.config(bg="red")

        except ValueError:

            button.config(bg="red")


    def submit_production_parameters(self, inda: input_data, button):
        
        """Klick on this button to load curtailments, losses and activation probabilities of reserve markets from Excel files."""

        kk=[True]
        xlx.load_curtailments_GO(inda, kk)
        xlx.load_losses_storage(inda, kk)

        if(inda.renewable_technology=="pv" or inda.renewable_technology == "wind_pv"):

            xlx.load_losses_pv(inda, kk)

        if(inda.renewable_technology=="wind" or inda.renewable_technology == "wind_pv"):

            xlx.load_losses_wind(inda, kk)
        
        if(inda.secondary_reserve_power_active == True or inda.secondary_reserve_energy_active==True):

            xlx.load_activation_secondary(inda, kk)
            
        if(inda.primary_reserve_active == True):

            xlx.load_activation_primary(inda, kk)

        if(kk[0]==False):

            button.config(bg="red")
            return

        self.show_frame(self.pages[16])


    def submit_storage_usage(self, inda: input_data, button, input_SR_trading_energy_for_direct_activation, input_predict, input_match, input_safty_capacity, input_SR_duration, input_PR_duration):

        """Klick on this button to submit other program adjustable variables as prediction horizon or the matching factor."""

        try:

            direct_active_sr = float(input_SR_trading_energy_for_direct_activation.get())
            predict = int(input_predict.get())
            match = float(input_match.get())
            safty_capacity = float(input_safty_capacity.get())
            SR_duration = float(input_SR_duration.get())
            PR_duration = float(input_PR_duration.get())
            
            if(SR_duration<0.25 or SR_duration>2):

                button.config(bg="red")
                return

            inda.storage_duration_SR = SR_duration

            if(PR_duration<0.05 or PR_duration>2):

                button.config(bg="red")
                return

            inda.storage_duration_PR = PR_duration

            if(direct_active_sr<0 or direct_active_sr>1000):

                button.config(bg="red")
                return

            inda.SR_trading_energy_for_direct_activation = direct_active_sr

            if(predict<=0 or predict>50):

                button.config(bg="red")
                return
            
            inda.prediction_horizon = predict

            if(match<1 or match>10):

                button.config(bg="red")
                return

            inda.matching_factor = match

            if(safty_capacity<0 or safty_capacity>50):

                button.config(bg="red")
                return

            inda.safty_factor_capactiy = safty_capacity

            self.show_frame(self.pages[17])
            
        except ValueError:

            button.config(bg="red")
        
        
    def init(self, inda: input_data):
        
        """This is the main function of this structure. A grafical interface will open to let the user choose input variables for the simulation. The input is checked before storing. The interface will close if the user clicks on simulation start."""

        # create the main window. Different pages will be shown on the window
        root = tk.Tk()
        root.title("Storage Simulation for Germany")
        root.state('zoomed')

        # all pages are packed in a container which is attributed to the window
        container = tk.Frame(root)
        container.pack(fill="both", expand=True)

        # reletiv dependencies to enable program usage on different screen scizes
        pc_width = root.winfo_screenwidth()
        font_size = int(pc_width / 60)
        font_size_info = int(pc_width / 120)
        font_size_button = int(pc_width / 60 * 0.8)
        font_size_button_min = int(pc_width / 60 * 0.65)
        info_width = pc_width * 0.9

        # Page 1: technology_storage_system
        page1 = tk.Frame(container)
        page1.place(relwidth=1, relheight=1)
        self.pages.append(page1)

        # title of first page
        head1 = tk.Label(page1, text="Choose the technology of the storage system", font=("Helvetica", font_size))
        head1.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head1)

        # Button for choosing the technology Li-Ion NMC
        button40 = tk.Button(
            # button is shown on page 1
            page1,
            # the text on the button
            text="Li-Ion (NMC)",
            # colour of the button
            bg="white",
            # font size and type of the button
            font=("Helvetica", font_size_button),
            # function executed by clicking on the button
            command=lambda: self.technology_storage_system_NMC(inda, button40)
        )
        # position of the button
        button40.place(relx=0.5, rely=0.25, anchor="n")
        # store button in list
        self.buttons.append(button40)
        
        # Button for choosing the technology Li-Ion LFP
        button41 = tk.Button(
            page1,
            text="Li-Ion (LFP)",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.technology_storage_system_LFP(inda, button41)
        )
        button41.place(relx=0.5, rely=0.35, anchor="n")
        self.buttons.append(button41)

        # Info text below
        info1 = tk.Label(
            page1,
            text="This parameter describes the technology of the storage system. Click on the technology that should be used. LFP (Lithium-Iron-Phosphate) has less degradation effects than NMC (Lithium-Nickel-Manganese-Cobalt) and is generally cheaper but NMC is more efficient. LFP is recommended.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info1.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info1)

        # Page 2: year_commissioning
        page2 = tk.Frame(container)
        page2.place(relwidth=1, relheight=1)
        self.pages.append(page2)

        # title of page 2
        head2 = tk.Label(page2, text="Choose the year of commissioning for the BESS", font=("Helvetica", font_size))
        head2.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head2)

        # Entry for year_commissioning
        input_year = tk.Entry(page2, font=("Helvetica", font_size_button), textvariable = tk.StringVar(value=inda.year_commissioning))
        input_year.place(relx=0.5, rely=0.4, anchor="n", width=100)
        self.inputs.append(input_year)

        # Submit button for year_commissioning
        button2 = tk.Button(
            page2,
            text="submit year",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_year(input_year, inda, button2)
        )
        button2.place(relx=0.5, rely=0.5, anchor="n")
        self.buttons.append(button2)

        # Info text below
        info2 = tk.Label(
            page2,
            text="Please enter the year, for which the commissioning of the BESS is planned. This influences the development of predefined default variables of the program. For example, the efficiency of the storage system will increase over time. Valid years are between 2025 and 2040.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info2.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info2)

        # Page 3: calculation_period
        page3 = tk.Frame(container)
        page3.place(relwidth=1, relheight=1)
        self.pages.append(page3)

        head3 = tk.Label(page3, text="What is the calculation period and the replacement period?", font=("Helvetica", font_size))
        head3.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head3)

        # Unit calculation period
        label21 = tk.Label(
            page3,
            text="a",
            font=("Helvetica", font_size_button)
        )
        label21.place(relx=0.6, rely=0.4, anchor="n")
        self.labels.append(label21)

        # Unit replacement period
        label97 = tk.Label(
            page3,
            text="a",
            font=("Helvetica", font_size_button)
        )
        label97.place(relx=0.6, rely=0.5, anchor="n")
        self.labels.append(label97)

        # text calculation period
        label98 = tk.Label(
            page3,
            text="calculation period = ",
            font=("Helvetica", font_size_button)
        )
        label98.place(relx=0.3, rely=0.4, anchor="n")
        self.labels.append(label98)

        # text replacement period
        label99 = tk.Label(
            page3,
            text="replacement period = ",
            font=("Helvetica", font_size_button)
        )
        label99.place(relx=0.3, rely=0.5, anchor="n")
        self.labels.append(label99)

        # Entry for calculation_period
        input_calculation_period = tk.Entry(page3, font=("Helvetica", font_size_button), textvariable = tk.StringVar(value=inda.calculation_period))
        input_calculation_period.place(relx=0.5, rely=0.4, anchor="n", width=70)
        self.inputs.append(input_calculation_period)

        # Entry for replacement_period
        input_replacement_period = tk.Entry(page3, font=("Helvetica", font_size_button), textvariable = tk.StringVar(value=inda.replacement_period))
        input_replacement_period.place(relx=0.5, rely=0.5, anchor="n", width=70)
        self.inputs.append(input_replacement_period)

        # Submit button for calculation & replacement period
        button3 = tk.Button(
            page3,
            text="submit periods",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_period(input_calculation_period, input_replacement_period, inda, button3)
        )
        button3.place(relx=0.5, rely=0.65, anchor="n")
        self.buttons.append(button3)

        # Info text below
        info3 = tk.Label(
            page3,
            text="The calculation period should match the calculation of the BESS in the Financial Model and describes the years covered in this simulation. Within the calculation period, there could be replacements of the capacity unit of the BESS. The simulation data is supported until 2050. The calculation period must be the replacement period multiplied by an integer.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info3.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info3)

        # Page 4: market
        page4 = tk.Frame(container)
        page4.place(relwidth=1, relheight=1)
        self.pages.append(page4)

        # title page 4
        head4 = tk.Label(page4, text="Choose the marketing strategies!", font=("Helvetica", font_size))
        head4.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head4)

        # Button for intraday
        button4 = tk.Button(
            page4,
            text="Intraday",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_intraday(inda, button4)
        )
        button4.place(relx=0.25, rely=0.15, anchor="n")
        self.buttons.append(button4)

        # Button for primary reserve
        button5 = tk.Button(
            page4,
            text="primary reserve",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_primary_reserve(inda, button5, button6)
        )
        button5.place(relx=0.75, rely=0.15, anchor="n")
        self.buttons.append(button5)

        # Button for secondary reserve power
        button35 = tk.Button(
            page4,
            text="secondary reserve power",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_secondary_reserve(inda, button35, button6, button44)
        )
        button35.place(relx=0.5, rely=0.15, anchor="n")
        self.buttons.append(button35)

        # Button for secondary reserve energy
        button37 = tk.Button(
            page4,
            text="secondary reserve energy (without secondary reserve power)",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_secondary_reserve_energy(inda, button37, button6)
        )
        button37.place(relx=0.5, rely=0.35, anchor="n")
        self.buttons.append(button37)

        # Button for secondary reserve power simultaneously
        button44 = tk.Button(
            page4,
            text="secondary reserve positive and negative power simultaneously",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_secondary_reserve_power_twice(inda, button44, button6, button35)
        )
        button44.place(relx=0.5, rely=0.45, anchor="n")
        self.buttons.append(button44)

        # Button for electricity purchase
        button6 = tk.Button(
            page4,
            text="electricity purchase",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_purchase(inda, button6, button35, button5, button44, button37)
        )
        button6.place(relx=0.7, rely=0.25, anchor="n")
        self.buttons.append(button6)

        # Button for self consumption
        button7 = tk.Button(
            page4,
            text="self-consumption",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_selfconsumption(inda, button7)
        )
        button7.place(relx=0.3, rely=0.25, anchor="n")
        self.buttons.append(button7)

        # Button for next page market strategies
        button8 = tk.Button(
            page4,
            text="submit market strategies",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_market_strategies(button8, inda)
        )
        button8.place(relx=0.5, rely=0.65, anchor="n")
        self.buttons.append(button8)

        # Info text below
        info4 = tk.Label(
            page4,
            text="Marketing strategies determine how money is earned by the storage. All strategies are combinable. Intraday Market, Primary and Secondary Reserve Markets are supported by the program. Predicted prices and activation probabilities are used for the calculation. The self consumption of the renewable plant can be supplied by the storage system. Electricity purchase of the BESS from the grid can be excluded in case of a peak shifting application of the battery. Self consumption and electricity purchase are only additional market strategies but not supported alone. It is possible to participate at the secondary energy markets without participation at the secondary power markets. It is possible to participate at both secondary reserve positive and negative power markets simultaneously but only for storage hours >= 2.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info4.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info4)

        # Page 5: storage capacity & power
        page5 = tk.Frame(container)
        page5.place(relwidth=1, relheight=1)
        self.pages.append(page5)

        # title page 5
        head5 = tk.Label(page5, text="Determine the main storage parameters!", font=("Helvetica", font_size))
        head5.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head5)

        # Entry for minimum capacity
        input_min_capacity = tk.Entry(page5, font=("Helvetica", font_size_button),textvariable = tk.StringVar(value=inda.capacity_storage_min))
        input_min_capacity.place(relx=0.5, rely=0.15, anchor="n", width=100)
        self.inputs.append(input_min_capacity)

        # Unit capacity 
        label1 = tk.Label(
            page5,
            text="MWh",
            font=("Helvetica", font_size_button)
        )
        label1.place(relx=0.65, rely=0.15, anchor="n")
        self.labels.append(label1)

        # capacity 
        label2 = tk.Label(
            page5,
            text="usable capacity = ",
            font=("Helvetica", font_size_button)
        )
        label2.place(relx=0.25, rely=0.15, anchor="n")
        self.labels.append(label2)

        # Entry for power factor
        input_powerfactor_min = tk.Entry(page5, font=("Helvetica", font_size_button),textvariable=tk.StringVar(value=inda.powerfactor_min))
        input_powerfactor_min.place(relx=0.5, rely=0.25, anchor="n", width=100)
        self.inputs.append(input_powerfactor_min)

        #  power factor
        label7 = tk.Label(
            page5,
            text="usable capacity / usable power = ",
            font=("Helvetica", font_size_button)
        )
        label7.place(relx=0.25, rely=0.25, anchor="n")
        self.labels.append(label7)

        # Unit power factor
        label8 = tk.Label(
            page5,
            text="MWh / MW",
            font=("Helvetica", font_size_button)
        )
        label8.place(relx=0.65, rely=0.25, anchor="n")
        self.labels.append(label8)

        # Button for next page main storage parameters
        button9 = tk.Button(
            page5,
            text="submit main storage parameters",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_main_storage_parameters(inda, button9, input_min_capacity, input_powerfactor_min)
        )
        button9.place(relx=0.5, rely=0.72, anchor="n")
        self.buttons.append(button9)

        # Info text below
        info5 = tk.Label(
            page5,
            text="The storage usable capacity and ratio of capacity to storage power can be chosen. Typical ratios of capacity to power for short-therm storages are in the range from 1 to 3, the maximum is 10. The usable capacity is constant over the whole lifetime. The maximum is 1000 MWh. Nominal capacity and power are greater due to degradation effects and will be calculated by the program, dependent on operation.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info5.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info5)

        # Page 6: detailed technical storage paramters
        page6 = tk.Frame(container)
        page6.place(relwidth=1, relheight=1)
        self.pages.append(page6)

        # title page 6
        head7 = tk.Label(page6, text="Confirm detailed technical storage parameters!", font=("Helvetica", font_size))
        head7.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head7)

        # Entry for cycles per year
        cycles_per_year_tk = tk.StringVar(value=inda.cycles_per_year)
        input_cycles_per_year = tk.Entry(page6, font=("Helvetica", font_size_button), textvariable = cycles_per_year_tk)
        input_cycles_per_year.place(relx=0.25, rely=0.15, anchor="n", width=100)
        self.inputs.append(input_cycles_per_year)

        # cycles per year
        label25 = tk.Label(
            page6,
            text="cycles per year = ",
            font=("Helvetica", font_size_button)
        )
        label25.place(relx=0.1, rely=0.15, anchor="n")
        self.labels.append(label25)
        
        # Entry for DOD
        DOD_tk = tk.StringVar(value=inda.DOD)
        input_DOD = tk.Entry(page6, font=("Helvetica", font_size_button), textvariable = DOD_tk)
        input_DOD.place(relx=0.25, rely=0.25, anchor="n", width=100)
        self.inputs.append(input_DOD)

        # DOD
        label22 = tk.Label(
            page6,
            text="average DOD = ",
            font=("Helvetica", font_size_button)
        )
        label22.place(relx=0.1, rely=0.25, anchor="n")
        self.labels.append(label22)

        # Unit DOD
        label23 = tk.Label(
            page6,
            text="%",
            font=("Helvetica", font_size_button)
        )
        label23.place(relx=0.35, rely=0.25, anchor="n")
        self.labels.append(label23)

        # roundtrip efficiency
        label24 = tk.Label(
            page6,
            text="Change the system roundtrip efficiencies in Excel file 'system_roundtip_efficiency.xlsx'.",
            font=("Helvetica", font_size_button)
        )
        label24.place(relx=0.5, rely=0.35, anchor="n")
        self.labels.append(label24)

        # Entry for recover time
        recover_time_tk = tk.StringVar(value=inda.recovery_time)
        input_recover_time = tk.Entry(page6, font=("Helvetica", font_size_button), textvariable = recover_time_tk)
        input_recover_time.place(relx=0.25, rely=0.45, anchor="n", width=100)
        self.inputs.append(input_recover_time)

        # recover time
        label26 = tk.Label(
            page6,
            text="recovery time = ",
            font=("Helvetica", font_size_button)
        )
        label26.place(relx=0.1, rely=0.45, anchor="n")
        self.labels.append(label26)

        # Unit recover time
        label27 = tk.Label(
            page6,
            text="min",
            font=("Helvetica", font_size_button)
        )
        label27.place(relx=0.4, rely=0.45, anchor="n")
        self.labels.append(label27)

        # Entry for Pu / PE
        pu_pe_tk = tk.StringVar(value=inda.pu_pe)
        input_pu_pe = tk.Entry(page6, font=("Helvetica", font_size_button), textvariable = pu_pe_tk)
        input_pu_pe.place(relx=0.8, rely=0.25, anchor="n", width=100)
        self.inputs.append(input_pu_pe)

        # Pu / PE
        label28 = tk.Label(
            page6,
            text="usable power / EOL power = ",
            font=("Helvetica", font_size_button)
        )
        label28.place(relx=0.6, rely=0.25, anchor="n")
        self.labels.append(label28)

        # Pu / PE
        label29 = tk.Label(
            page6,
            text="%",
            font=("Helvetica", font_size_button)
        )
        label29.place(relx=0.9, rely=0.25, anchor="n")
        self.labels.append(label29)

        # Entry for self-discharge
        self_discharge_tk = tk.StringVar(value=inda.self_discharge) 
        input_self_discharge = tk.Entry(page6, font=("Helvetica", font_size_button), textvariable = self_discharge_tk)
        input_self_discharge.place(relx=0.8, rely=0.15, anchor="n", width=100)
        self.inputs.append(input_self_discharge)

        # self-discharge
        label37 = tk.Label(
            page6,
            text="self-discharge rate = ",
            font=("Helvetica", font_size_button)
        )
        label37.place(relx=0.6, rely=0.15, anchor="n")
        self.labels.append(label37)

        # self-discharge
        label36 = tk.Label(
            page6,
            text="% / month",
            font=("Helvetica", font_size_button)
        )
        label36.place(relx=0.9, rely=0.15, anchor="n")
        self.labels.append(label36)

        # Entry for recovery activation
        self_recovery_activation_tk = tk.StringVar(value=inda.recovery_activation) 
        input_recovery_activation = tk.Entry(page6, font=("Helvetica", font_size_button), textvariable = self_recovery_activation_tk)
        input_recovery_activation.place(relx=0.8, rely=0.45, anchor="n", width=100)
        self.inputs.append(input_recovery_activation)

        # recovery activation
        label100 = tk.Label(
            page6,
            text="recovery activation = ",
            font=("Helvetica", font_size_button)
        )
        label100.place(relx=0.6, rely=0.45, anchor="n")
        self.labels.append(label100)

        # recovery activation
        label101 = tk.Label(
            page6,
            text="cycles",
            font=("Helvetica", font_size_button)
        )
        label101.place(relx=0.9, rely=0.45, anchor="n")
        self.labels.append(label101)

        # Entry for RTE annual degradation
        self_rte_annual_tk = tk.StringVar(value=inda.RTE_annual_degradation) 
        input_rte_annual = tk.Entry(page6, font=("Helvetica", font_size_button), textvariable = self_rte_annual_tk)
        input_rte_annual.place(relx=0.28, rely=0.55, anchor="n", width=70)
        self.inputs.append(input_rte_annual)

        # RTE annual degradation
        label102 = tk.Label(
            page6,
            text="RTE annual degradation = ",
            font=("Helvetica", font_size_button)
        )
        label102.place(relx=0.13, rely=0.55, anchor="n")
        self.labels.append(label102)

        # Unit RTE annual degradation
        label102 = tk.Label(
            page6,
            text="percentage points",
            font=("Helvetica", font_size_button)
        )
        label102.place(relx=0.4, rely=0.55, anchor="n")
        self.labels.append(label102)

        # Entry for RTE SOC dependency
        self_rte_soc_tk = tk.StringVar(value=inda.RTE_SOC_dependency) 
        input_rte_soc = tk.Entry(page6, font=("Helvetica", font_size_button), textvariable = self_rte_soc_tk)
        input_rte_soc.place(relx=0.77, rely=0.55, anchor="n", width=100)
        self.inputs.append(input_rte_soc)

        # RTE SOC dependency
        label103 = tk.Label(
            page6,
            text="at SOC = 100, RTE loss = ",
            font=("Helvetica", font_size_button)
        )
        label103.place(relx=0.6, rely=0.55, anchor="n")
        self.labels.append(label103)

        # RTE SOC dependency
        label102 = tk.Label(
            page6,
            text="percentage points",
            font=("Helvetica", font_size_button)
        )
        label102.place(relx=0.9, rely=0.55, anchor="n")
        self.labels.append(label102)

        # Button for next page detailed technical storage parameters
        button11 = tk.Button(
            page6,
            text="submit detailed technical storage parameters",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_detailed_technical_storage_parameters(inda, button11, input_DOD, input_pu_pe, input_recover_time, input_cycles_per_year, input_self_discharge, input_recovery_activation, input_rte_annual, input_rte_soc, label34, input_RES_consumption_costs, label35, input_PR_duration, label115, label116, input_SR_storage_duration, label117, label118, input_SR_trading_energy_for_direct_activation, label63, label64)
        )
        button11.place(relx=0.5, rely=0.65, anchor="n")
        self.buttons.append(button11)

        # Info text below
        info7 = tk.Label(
            page6,
            text="The faded capacity and power will be calculated by the program dependend on average DOD and the ratio of usable power to EOL (End-of-life) power. The average DOD describes how deep the storage system will be cycled, related to nominal capacity. If DOD is chosen too high, the program will correct the degradation automatically. It is also recommended to let the program calculate the average DOD. The system roundtrip efficiency describes the ratio of AC power at storage input to output of one cycle. You can lower the ratio of usable to EOL power to influence efficiency effects but this is not recommended. After uninterrupted operation, defined in 'recovery activation', the storage system needs some time for cooling, which is called 'recovery time'. Type in the number of target cycles that should be distributed annually for optimal revenue. The real number of cycles will deviate. Check how many cycles the program actually distributed and change the target cycles again to meet your goal cycles. The self-discharge rate depends on the storage technology used. 1 to 4 % can be assumed. The system RTE degradates annually and is dependent on SOC. For low SOC and high SOC, the RTE is much less than normal. You can define the RTE loss at 100 % SOC. Because the usable capacity is constant, the nominal capacity is assumed higher and charged. This is the reason why the RTE reduction for the low SOCs are neglected.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info7.place(relx=0.5, rely=0.75, anchor="n")
        self.infos.append(info7)

        # Page 7: detailed storage paramters
        page7 = tk.Frame(container)
        page7.place(relwidth=1, relheight=1)
        self.pages.append(page7)

        # title of page 7
        head6 = tk.Label(page7, text="Confirm detailed financial storage parameters!", font=("Helvetica", font_size))
        head6.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head6)

        # CAPEX storage kW
        label14 = tk.Label(
            page7,
            text="Change the power dependend CAPEX of the storage system in file 'capex_storage_kW.xlsx'.",
            font=("Helvetica", font_size_button)
        )
        label14.place(relx=0.5, rely=0.25, anchor="n")
        self.labels.append(label14)

        # capex storage kWh
        label14 = tk.Label(
            page7,
            text="Change the capacity dependend CAPEX of the storage system in file 'capex_storage_kWh.xlsx'",
            font=("Helvetica", font_size_button)
        )
        label14.place(relx=0.5, rely=0.35, anchor="n")
        self.labels.append(label14)

        # opex storage kW
        label16 = tk.Label(
            page7,
            text="Change the power dependend OPEX of the storage system in file 'opex_storage_kW.xlsx'",
            font=("Helvetica", font_size_button)
        )
        label16.place(relx=0.5, rely=0.45, anchor="n")
        self.labels.append(label16)

        # opex storage MWh
        opex_storage_MWh_tk = tk.StringVar(value=inda.opex_storage_MWh)
        input_opex_storage_MWh = tk.Entry(page7, font=("Helvetica", font_size_button), textvariable = opex_storage_MWh_tk)
        input_opex_storage_MWh.place(relx=0.5, rely=0.55, anchor="n", width=100)
        self.inputs.append(input_opex_storage_MWh)

        # Unit opex storage MWh
        label17 = tk.Label(
            page7,
            text="€ / MWh",
            font=("Helvetica", font_size_button)
        )
        label17.place(relx=0.65, rely=0.55, anchor="n")
        self.labels.append(label17)

        #  O&M storage MWh
        label18 = tk.Label(
            page7,
            text="energy related OPEX storage = ",
            font=("Helvetica", font_size_button)
        )
        label18.place(relx=0.25, rely=0.55, anchor="n")
        self.labels.append(label18)

        # Button for next page detailed financial storage parameters
        button10 = tk.Button(
            page7,
            text="submit detailed financial storage parameters",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_detailed_financial_storage_parameters(inda, button10, input_opex_storage_MWh, self_discharge_tk)
        )
        button10.place(relx=0.5, rely=0.7, anchor="n")
        self.buttons.append(button10)

        # Info text below
        info6 = tk.Label(
            page7,
            text="Investement costs (CAPEX) can be entered depending on installed capacity or power related costs. Operational costs (OPEX) can be entered depending on power related and energy generated costs. Capacity related describes the costs for the storage unit itself, whereas power related refers to the costs of power electronics. 'Energy' is related to the amount of traded energy. If the program does not find an entry for the user-defined power and capacity, these parameters will be rounded to the next valid values in the Excel-Sheet!",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info6.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info6)

        # Page 8: other electrical parameters
        page8 = tk.Frame(container)
        page8.place(relwidth=1, relheight=1)
        self.pages.append(page8)

        # title page 8
        head8 = tk.Label(page8, text="Enter other electrical parameters!", font=("Helvetica", font_size))
        head8.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head8)

        # Entry for grid limit
        grid_limit_tk = tk.StringVar(value=inda.grid_limit)
        input_grid_limit = tk.Entry(page8, font=("Helvetica", font_size_button), textvariable = grid_limit_tk)
        input_grid_limit.place(relx=0.5, rely=0.25, anchor="n", width=300)
        self.inputs.append(input_grid_limit)

        # grid limit
        label30 = tk.Label(
            page8,
            text="grid limit = ",
            font=("Helvetica", font_size_button)
        )
        label30.place(relx=0.25, rely=0.25, anchor="n")
        self.labels.append(label30)

        # Unit grid limit
        label31 = tk.Label(
            page8,
            text="MW",
            font=("Helvetica", font_size_button)
        )
        label31.place(relx=0.65, rely=0.25, anchor="n")
        self.labels.append(label31)

        # Button for next page other electrical parameters
        button12 = tk.Button(
            page8,
            text="submit grid connection parameters!",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_other_electrical_parameters(inda, button12, input_grid_limit)
        )
        button12.place(relx=0.5, rely=0.7, anchor="n")
        self.buttons.append(button12)

        # Info text below
        info8 = tk.Label(
            page8,
            text="The grid provider might not allow to feed all power produced into the grid. A grid limit in form of the maximum feed-in power can be set. If you do not have a limit, enter '-1'. If the power purchase from the grid is limited, deactivate power purchase at the market selection and the battery will take the power only from the renewable plant.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info8.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info8)

        # Page 9: other financial parameters
        page9 = tk.Frame(container)
        page9.place(relwidth=1, relheight=1)
        self.pages.append(page9)

        # title page 9
        head9 = tk.Label(page9, text="Enter fees and prices of energy!", font=("Helvetica", font_size))
        head9.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head9)

        # Entry for input_fees_BESS
        fees_BESS_tk = tk.StringVar(value=inda.fees_BESS)
        input_fees_BESS = tk.Entry(page9, font=("Helvetica", font_size_button), textvariable = fees_BESS_tk)
        input_fees_BESS.place(relx=0.5, rely=0.15, anchor="n", width=100)
        self.inputs.append(input_fees_BESS)

        # input_fees_BESS
        label32 = tk.Label(
            page9,
            text="storage fees = ",
            font=("Helvetica", font_size_button)
        )
        label32.place(relx=0.25, rely=0.15, anchor="n")
        self.labels.append(label32)

        # Unit input_fees_BESS
        label33 = tk.Label(
            page9,
            text="ct / kWh",
            font=("Helvetica", font_size_button)
        )
        label33.place(relx=0.65, rely=0.15, anchor="n")
        self.labels.append(label33)

        # Entry for RES_consumption_costs
        RES_consumption_costs_tk = tk.StringVar(value=inda.RES_consumption_costs)
        input_RES_consumption_costs = tk.Entry(page9, font=("Helvetica", font_size_button), textvariable = RES_consumption_costs_tk)
        input_RES_consumption_costs.place(relx=0.5, rely=0.25, anchor="n", width=100)
        self.inputs.append(input_RES_consumption_costs)

        # RES_consumption_costs
        label34 = tk.Label(
            page9,
            text="costs RES grid consumption = ",
            font=("Helvetica", font_size_button)
        )
        label34.place(relx=0.25, rely=0.25, anchor="n")
        self.labels.append(label34)

        # Unit RES_consumption_costs
        label35 = tk.Label(
            page9,
            text="ct / kWh",
            font=("Helvetica", font_size_button)
        )
        label35.place(relx=0.65, rely=0.25, anchor="n")
        self.labels.append(label35)

         # grid_charges_kW
        label40 = tk.Label(
            page9,
            text="power dependend grid charges = change in 'grid_charges_kW.xlsx'",
            font=("Helvetica", font_size_button)
        )
        label40.place(relx=0.5, rely=0.35, anchor="n")
        self.labels.append(label40)

        # grid_charges_kWh
        label41 = tk.Label(
            page9,
            text="energy dependend grid charges = change in 'grid_charges_kWh.xlsx'",
            font=("Helvetica", font_size_button)
        )
        label41.place(relx=0.5, rely=0.45, anchor="n")
        self.labels.append(label41)
        
        # Button for next page taxes and duties
        button16 = tk.Button(
            page9,
            text="submit taxes and duties",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_taxes_and_duties(inda, button16, input_RES_consumption_costs, input_fees_BESS)
        )
        button16.place(relx=0.5, rely=0.65, anchor="n")
        self.buttons.append(button16)

        # Info text below
        info9 = tk.Label(
            page9,
            text="Type in average prices for the calculation period. Change power and energy dependent grid charges in the related Excel file which will be imported by the program. Enter the price for energy-dependent grid consumption of RES, consisting of energy prices, grid fees and levies. Storage fees are the sum of all fees the storage system must pay when charging from the grid.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info9.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info9)

        # Page 10: other financial parameters
        page10 = tk.Frame(container)
        page10.place(relwidth=1, relheight=1)
        self.pages.append(page10)

        # title page 10
        head10 = tk.Label(page10, text="Enter other financial parameters!", font=("Helvetica", font_size))
        head10.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head10)

        # Entry for discount_rate
        discount_rate_tk = tk.StringVar(value=inda.discount_rate)
        input_discount_rate = tk.Entry(page10, font=("Helvetica", font_size_button), textvariable = discount_rate_tk)
        input_discount_rate.place(relx=0.5, rely=0.15, anchor="n", width=100)
        self.inputs.append(input_discount_rate)

        # discount_rate
        label44 = tk.Label(
            page10,
            text="discount rate = ",
            font=("Helvetica", font_size_button)
        )
        label44.place(relx=0.25, rely=0.15, anchor="n")
        self.labels.append(label44)

        # Unit discount_rate
        label45 = tk.Label(
            page10,
            text="%",
            font=("Helvetica", font_size_button)
        )
        label45.place(relx=0.65, rely=0.15, anchor="n")
        self.labels.append(label45)

        # Entry for discount
        discount_tk = tk.StringVar(value=inda.initial_discount)
        input_discount = tk.Entry(page10, font=("Helvetica", font_size_button), textvariable = discount_tk)
        input_discount.place(relx=0.5, rely=0.25, anchor="n", width=200)
        self.inputs.append(input_discount)

        # text discount
        label46 = tk.Label(
            page10,
            text="initial discount = ",
            font=("Helvetica", font_size_button)
        )
        label46.place(relx=0.25, rely=0.25, anchor="n")
        self.labels.append(label46)

        # Unit discount
        label47 = tk.Label(
            page10,
            text="€",
            font=("Helvetica", font_size_button)
        )
        label47.place(relx=0.65, rely=0.25, anchor="n")
        self.labels.append(label47)

        # Entry for input_initial_costs
        initial_costs_tk = tk.StringVar(value=inda.initial_costs)
        input_initial_costs = tk.Entry(page10, font=("Helvetica", font_size_button), textvariable = initial_costs_tk)
        input_initial_costs.place(relx=0.5, rely=0.35, anchor="n", width=200)
        self.inputs.append(input_initial_costs)

        # input_initial_costs
        label48 = tk.Label(
            page10,
            text="initial costs = ",
            font=("Helvetica", font_size_button)
        )
        label48.place(relx=0.25, rely=0.35, anchor="n")
        self.labels.append(label48)

        # Unit input_initial_costs
        label49 = tk.Label(
            page10,
            text="€",
            font=("Helvetica", font_size_button)
        )
        label49.place(relx=0.65, rely=0.35, anchor="n")
        self.labels.append(label49)

        # Entry for residual value
        initial_residual_tk = tk.StringVar(value=inda.residual_value)
        input_residual = tk.Entry(page10, font=("Helvetica", font_size_button), textvariable = initial_residual_tk)
        input_residual.place(relx=0.5, rely=0.45, anchor="n", width=200)
        self.inputs.append(input_residual)

        # residual value
        label104 = tk.Label(
            page10,
            text="residual value = ",
            font=("Helvetica", font_size_button)
        )
        label104.place(relx=0.25, rely=0.45, anchor="n")
        self.labels.append(label104)

        # Unit residual value
        label105 = tk.Label(
            page10,
            text="€ / kWh",
            font=("Helvetica", font_size_button)
        )
        label105.place(relx=0.65, rely=0.45, anchor="n")
        self.labels.append(label105)

        # Entry for penatly 
        initial_penalty_tk = tk.StringVar(value=inda.factor_penalty)
        input_penalty = tk.Entry(page10, font=("Helvetica", font_size_button), textvariable = initial_penalty_tk)
        input_penalty.place(relx=0.25, rely=0.55, anchor="n", width=100)
        self.inputs.append(input_penalty)

        # penatly
        label106 = tk.Label(
            page10,
            text="factor penalty = ",
            font=("Helvetica", font_size_button)
        )
        label106.place(relx=0.1, rely=0.55, anchor="n")
        self.labels.append(label106)

        # Entry for non optimal markets 
        non_optimal_market_tk = tk.StringVar(value=inda.loss_not_optimal_market_behavior)
        input_non_optimal_market = tk.Entry(page10, font=("Helvetica", font_size_button), textvariable = non_optimal_market_tk)
        input_non_optimal_market.place(relx=0.5, rely=0.65, anchor="n", width=100)
        self.inputs.append(input_non_optimal_market)

        # text non optimal markets
        label107 = tk.Label(
            page10,
            text="losses non optimal market behaviour = ",
            font=("Helvetica", font_size_button)
        )
        label107.place(relx=0.25, rely=0.65, anchor="n")
        self.labels.append(label107)

        # Unit non optimal markets
        label108 = tk.Label(
            page10,
            text="%",
            font=("Helvetica", font_size_button)
        )
        label108.place(relx=0.65, rely=0.65, anchor="n")
        self.labels.append(label108)

        # Entry for degradation costs
        degradation_cost_tk = tk.StringVar(value=inda.storage_degradation_costs)
        input_degradation_cost = tk.Entry(page10, font=("Helvetica", font_size_button), textvariable = degradation_cost_tk)
        input_degradation_cost.place(relx=0.75, rely=0.55, anchor="n", width=100)
        self.inputs.append(input_degradation_cost)

        # degradation costs
        label113 = tk.Label(
            page10,
            text="storage degradation costs = ",
            font=("Helvetica", font_size_button)
        )
        label113.place(relx=0.5, rely=0.55, anchor="n")
        self.labels.append(label113)

        # Unit degradation costs
        label114 = tk.Label(
            page10,
            text="€ / MW / cycle",
            font=("Helvetica", font_size_button)
        )
        label114.place(relx=0.9, rely=0.55, anchor="n")
        self.labels.append(label114)

        # Button for next page other financial parameters
        button17 = tk.Button(
            page10,
            text="submit other financial parameters",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_other_financial_parameters(inda, button17, input_discount, input_discount_rate, input_initial_costs, input_residual, input_penalty, input_non_optimal_market, input_degradation_cost)
        )
        button17.place(relx=0.5, rely=0.75, anchor="n")
        self.buttons.append(button17)

        # Info text below
        info10 = tk.Label(
            page10,
            text="Every Cash Flow evaluated by the program will be discounted by the discount rate. Discounts of any kind can be entered, that may apply for the project start, for example costs saving of a transformer. If there are any special costs at the project's start, enter it in initial costs. Enter a factor in case of penalty payments, the original price will be multiplied with. The theoretically possible revenue determined by this program will be less in practice, because the auctions will not be won to a 100 % chance. Sometimes the electricity cannot be sold for the price bid. Enter a loss factor between praxis and theory! The residual value is related to the capacity unit and will be considered as a revenue after each replacement period. If disposal costs are expected, enter negative residual values. The degradation costs are only used for the calculation of curtailment reimbursements.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info10.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info10)

        # Page 11: simulation parameters
        page11 = tk.Frame(container)
        page11.place(relwidth=1, relheight=1)
        self.pages.append(page11)

        head11 = tk.Label(page11, text="Enter simulation parameters!", font=("Helvetica", font_size))
        head11.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head11)

        # Choose the renewable technology
        label52 = tk.Label(
            page11,
            text="Choose the renewable technology:",
            font=("Helvetica", font_size_button)
        )
        label52.place(relx=0.5, rely=0.46, anchor="n")
        self.labels.append(label52)

        # Button for selecting wind technology
        button21 = tk.Button(
            page11,
            text="wind",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.choose_wind(inda, button21, button22, button23)
        )
        button21.place(relx=0.25, rely=0.55, anchor="n")
        self.buttons.append(button21)

        # Button for selecting pv technology
        button22 = tk.Button(
            page11,
            text="photovoltaic",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.choose_pv(inda, button21, button22, button23)
        )
        button22.place(relx=0.75, rely=0.55, anchor="n")
        self.buttons.append(button22)

        # Button for selecting wind and pv technology
        button23 = tk.Button(
            page11,
            text="wind and photovoltaic",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.choose_wind_pv(inda, button21, button22, button23)
        )
        button23.place(relx=0.5, rely=0.55, anchor="n")
        self.buttons.append(button23)

        # Button for next page simulation parameters
        button18 = tk.Button(
            page11,
            text="submit simulation parameters",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_simulation_paramters(inda, button18, label72, label77, label74, label75, label76, label79, label82, label80, label83, input_self_consumption_pv, label54, label55, input_self_consumption_wind, label59, label60)
        )
        button18.place(relx=0.5, rely=0.68, anchor="n")
        self.buttons.append(button18)

        # Info text below
        info11 = tk.Label(
            page11,
            text="Choose which renewable technologies should be considered. Dependent on selection, the power data of the technologies must be implemented.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info11.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info11)

        # Page 12: pv
        page12 = tk.Frame(container)
        page12.place(relwidth=1, relheight=1)
        self.pages.append(page12)

        # title page 12
        head12 = tk.Label(page12, text="Enter photovoltaic parameters!", font=("Helvetica", font_size))
        head12.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head12)

        # unit pv data
        label53 = tk.Label(
            page12,
            text="Provide the feed-in-power from the photovoltaic plant in the unit kW in 'power_pv.xlsx':",
            font=("Helvetica", font_size_button)
        )
        label53.place(relx=0.5, rely=0.15, anchor="n")
        self.labels.append(label53)

         # Entry for self_consumption_pv
        self_consumption_pv_tk = tk.StringVar(value=inda.self_consumption_pv)
        input_self_consumption_pv = tk.Entry(page12, font=("Helvetica", font_size_button), textvariable= self_consumption_pv_tk)
        input_self_consumption_pv.place(relx=0.5, rely=0.25, anchor="n", width=100)
        self.inputs.append(input_self_consumption_pv)

        # self_consumption_pv
        label54 = tk.Label(
            page12,
            text="self consumption PV = ",
            font=("Helvetica", font_size_button)
        )
        label54.place(relx=0.25, rely=0.25, anchor="n")
        self.labels.append(label54)

        # unit self_consumption_pv
        label55 = tk.Label(
            page12,
            text="kW",
            font=("Helvetica", font_size_button)
        )
        label55.place(relx=0.65, rely=0.25, anchor="n")
        self.labels.append(label55)

        # submit pv data
        button28 = tk.Button(
            page12,
            text="submit photovoltaic parameters",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_pv_parameters(inda, button28, input_self_consumption_pv)
        )
        button28.place(relx=0.5, rely=0.5, anchor="n")
        self.buttons.append(button28)

        # Info text below
        info12 = tk.Label(
            page12,
            text="The feed-in data of the photovoltaic plant must be provided as an Excel file in the unit kW in 15-min timesteps over one year. The name of the file is 'power_pv.xlsx'. Ensure that the first timestep is 01.01.JJJJ 00:15 AM. The provided data must be simulated at 100 % technical availability and without deduction of curtailments. The minimum production should be 0. Self-consumption is considered seperately as a constant power in case of lower production than self-consumption.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info12.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info12)

        # Page 13: wind
        page13 = tk.Frame(container)
        page13.place(relwidth=1, relheight=1)
        self.pages.append(page13)

        # title page 13
        head13 = tk.Label(page13, text="Enter wind parameters!", font=("Helvetica", font_size))
        head13.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head13)

        # unit wind data
        label58 = tk.Label(
            page13,
            text="Provide the feed-in-power from the wind plant in the unit kW in 'power_wind.xlsx':",
            font=("Helvetica", font_size_button)
        )
        label58.place(relx=0.5, rely=0.125, anchor="n")
        self.labels.append(label58)

        # Entry for self_consumption_wind
        self_consumption_wind_tk = tk.StringVar(value=inda.self_consumption_wind)
        input_self_consumption_wind = tk.Entry(page13, font=("Helvetica", font_size_button), textvariable=self_consumption_wind_tk)
        input_self_consumption_wind.place(relx=0.55, rely=0.4, anchor="n", width=100)
        self.inputs.append(input_self_consumption_wind)

        # self_consumption_wind
        label59 = tk.Label(
            page13,
            text="self-consumption wind = ",
            font=("Helvetica", font_size_button)
        )
        label59.place(relx=0.25, rely=0.4, anchor="n")
        self.labels.append(label59)

        # unit self_consumption_wind
        label60 = tk.Label(
            page13,
            text="kW",
            font=("Helvetica", font_size_button)
        )
        label60.place(relx=0.75, rely=0.4, anchor="n")
        self.labels.append(label60)

        # submit wind data
        button33 = tk.Button(
            page13,
            text="submit wind parameters",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_wind_parameters(inda, button33, input_self_consumption_wind)
        )
        button33.place(relx=0.5, rely=0.7, anchor="n")
        self.buttons.append(button33)

        # Info text below
        info13 = tk.Label(
            page13,
            text="The feed-in data of the wind plant must be provided as an Excel file in the unit kW in 15-min timesteps over one year. The name of the file is 'power_wind.xlsx'. Ensure that the first timestep is 01.01.JJJJ 00:15 AM. The provided data must be simulated at 100 % technical availability and without deduction of curtailments. The minimum production should be 0. Self-consumption is considered seperately as a constant power in case of lower production than self-consumption.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info13.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info13)

        # Page 14: renewable financial parameters
        page14 = tk.Frame(container)
        page14.place(relwidth=1, relheight=1)
        self.pages.append(page14)

        # title page 14
        head14 = tk.Label(page14, text="Confirm market prices!", font=("Helvetica", font_size))
        head14.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head14)

        # PR power price
        label72 = tk.Label(
            page14,
            text="Change the prices of primary reserve power in Excel file 'primary_reserve_price.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label72.place(relx=0.5, rely=0.15, anchor="n")
        self.labels.append(label72)

        # SR price power +
        label74 = tk.Label(
            page14,
            text="Change the positive prices of secondary reserve power in Excel file 'secondary_reserve_power_price_plus.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label74.place(relx=0.5, rely=0.25, anchor="n")
        self.labels.append(label74)

        # SR price power -
        label77 = tk.Label(
            page14,
            text="Change the negative prices of secondary reserve power in Excel file 'secondary_reserve_power_price_minus.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label77.place(relx=0.5, rely=0.35, anchor="n")
        self.labels.append(label77)

        # SR price energy +
        label75 = tk.Label(
            page14,
            text="Change the positive prices of secondary reserve energy in Excel file 'secondary_reserve_energy_price_plus.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label75.place(relx=0.5, rely=0.45, anchor="n")
        self.labels.append(label75)

        # SR price energy -
        label76 = tk.Label(
            page14,
            text="Change the negative prices of secondary reserve energy in Excel file 'secondary_reserve_energy_price_minus.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label76.place(relx=0.5, rely=0.55, anchor="n")
        self.labels.append(label76)

        # market_prices
        label81 = tk.Label(
            page14,
            text="Change intraday market prices in Excel file = 'intraday_prices.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label81.place(relx=0.5, rely=0.65, anchor="n")
        self.labels.append(label81)

        # Button for next page detailed financial storage parameters
        button34 = tk.Button(
            page14,
            text="submit market prices (wait for 2 min!)",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_market_prices(inda, button34)
        )
        button34.place(relx=0.5, rely=0.75, anchor="n")
        self.buttons.append(button34)

        # Info text below
        info14 = tk.Label(
            page14,
            text="The market prices deposited, are prognoses developed from historical data and considering the future impact of increased market competition. The market prices prognoses should be recalculated annually due to fast development of the electricity market. The Secondary Reserve consists of 4 markets where energy and power each positive and negative can be traded. It is also recommended to use professional market price forecasts instead of the default implementation to get more accurate results.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info14.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info14)

        # Page 15: production_parameters
        page15 = tk.Frame(container)
        page15.place(relwidth=1, relheight=1)
        self.pages.append(page15)

        head15 = tk.Label(page15, text="Enter production parameters!", font=("Helvetica", font_size))
        head15.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head15)

        # curtailments_GO
        label78 = tk.Label(
            page15,
            text="Change curtailment prognosis of the Grid Operator in file = 'curtailments_GO.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label78.place(relx=0.5, rely=0.15, anchor="n")
        self.labels.append(label78)

        # losses pv
        label79 = tk.Label(
            page15,
            text="Change outages (without curtailments) of photovoltaics in file = 'losses_pv.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label79.place(relx=0.5, rely=0.25, anchor="n")
        self.labels.append(label79)

        # losses wind
        label82 = tk.Label(
            page15,
            text="Change outages (without curtailments) of wind in file = 'losses_wind.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label82.place(relx=0.5, rely=0.35, anchor="n")
        self.labels.append(label82)

        # losses storage
        label91 = tk.Label(
            page15,
            text="Change outages (without curtailments) of the storage system in file = 'losses_storage.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label91.place(relx=0.5, rely=0.45, anchor="n")
        self.labels.append(label91)

        # PR activation probability
        label80 = tk.Label(
            page15,
            text="Change the activation probability of primary reserve energy in file = 'primary_reserve_activation.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label80.place(relx=0.5, rely=0.55, anchor="n")
        self.labels.append(label80)

        # SR activation propability
        label83 = tk.Label(
            page15,
            text="Change the activation probability of secondary reserve energy in file = 'secondary_reserve_activation.xlsx'",
            font=("Helvetica", font_size_button_min)
        )
        label83.place(relx=0.5, rely=0.65, anchor="n")
        self.labels.append(label83)

        # Button for next page renewable production parameters
        button36 = tk.Button(
            page15,
            text="submit production parameters (wait for 1 min!)",
            bg="white",
            font=("Helvetica", font_size_button_min),
            command=lambda: self.submit_production_parameters(inda, button36)
        )
        button36.place(relx=0.5, rely=0.75, anchor="n")
        self.buttons.append(button36)

        # Info text below
        info15 = tk.Label(
            page15,
            text="Curtailments of the grid operator, losses of the renewable plants and activation probability of the storage system can be determined as vectors in Excel files. The unit is % of nominal power and the resolution must be 15 min values until year 2050. Negative activation probabilities indicate discharging of the BESS.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info15.place(relx=0.5, rely=0.85, anchor="n")
        self.infos.append(info15)

        # Page 16: not used: in case some parameters must be added
        page16 = tk.Frame(container)
        page16.place(relwidth=1, relheight=1)
        self.pages.append(page16)

        # title page 16
        head16 = tk.Label(page16, text="NOT USED", font=("Helvetica", font_size))
        head16.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head16)

        # Info text below
        info16 = tk.Label(
            page16,
            text="not used",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info16.place(relx=0.5, rely=0.87, anchor="n")
        self.infos.append(info16)

        # Page 17: output parameters & simulation start
        page17 = tk.Frame(container)
        page17.place(relwidth=1, relheight=1)
        self.pages.append(page17)

        # title page 17
        head17 = tk.Label(page17, text="Determine algorithm parameters!", font=("Helvetica", font_size))
        head17.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head17)

        # Entry for SR_trading_energy_for_direct_activation 
        SR_trading_energy_for_direct_activation_tk = tk.StringVar(value=inda.SR_trading_energy_for_direct_activation)
        input_SR_trading_energy_for_direct_activation = tk.Entry(page17, font=("Helvetica", font_size_button), textvariable=SR_trading_energy_for_direct_activation_tk)
        input_SR_trading_energy_for_direct_activation.place(relx=0.75, rely=0.15, anchor="n", width=100)
        self.inputs.append(input_SR_trading_energy_for_direct_activation)

        # SR_trading_energy_for_direct_activation 
        label63 = tk.Label(
            page17,
            text="Lower price bid of secondary reserve energy for activation = ",
            font=("Helvetica", font_size_button)
        )
        label63.place(relx=0.35, rely=0.15, anchor="n")
        self.labels.append(label63)

        # unit SR_trading_energy_for_direct_activation
        label64 = tk.Label(
            page17,
            text="€ / MWh",
            font=("Helvetica", font_size_button)
        )
        label64.place(relx=0.9, rely=0.15, anchor="n")
        self.labels.append(label64)

        # Entry for prediction horizon
        predict_tk = tk.StringVar(value=inda.prediction_horizon)
        input_predict = tk.Entry(page17, font=("Helvetica", font_size_button), textvariable=predict_tk)
        input_predict.place(relx=0.75, rely=0.25, anchor="n", width=100)
        self.inputs.append(input_predict)

        # prediction horizon 
        label109 = tk.Label(
            page17,
            text="prediction horizon = ",
            font=("Helvetica", font_size_button)
        )
        label109.place(relx=0.35, rely=0.25, anchor="n")
        self.labels.append(label109)

        # unit prediction horizon
        label110 = tk.Label(
            page17,
            text="timestamps",
            font=("Helvetica", font_size_button)
        )
        label110.place(relx=0.9, rely=0.25, anchor="n")
        self.labels.append(label110)

        # Entry for matching factor 
        match_tk = tk.StringVar(value=inda.matching_factor)
        input_match = tk.Entry(page17, font=("Helvetica", font_size_button), textvariable=match_tk)
        input_match.place(relx=0.75, rely=0.35, anchor="n", width=100)
        self.inputs.append(input_match)

        # matching factor 
        label109 = tk.Label(
            page17,
            text="matching factor = ",
            font=("Helvetica", font_size_button)
        )
        label109.place(relx=0.35, rely=0.35, anchor="n")
        self.labels.append(label109)

        # Entry for capacity safty factor 
        safty_capacity_tk = tk.StringVar(value=inda.safty_factor_capactiy)
        input_safty_capacity = tk.Entry(page17, font=("Helvetica", font_size_button), textvariable=safty_capacity_tk)
        input_safty_capacity.place(relx=0.75, rely=0.45, anchor="n", width=100)
        self.inputs.append(input_safty_capacity)

        # capacity safty factor 
        label112 = tk.Label(
            page17,
            text="safety factor additional charge = ",
            font=("Helvetica", font_size_button)
        )
        label112.place(relx=0.35, rely=0.45, anchor="n")
        self.labels.append(label112)

        # capacity safty factor 
        label119 = tk.Label(
            page17,
            text="%",
            font=("Helvetica", font_size_button)
        )
        label119.place(relx=0.9, rely=0.45, anchor="n")
        self.labels.append(label119)

        # Entry for storage duration PR
        PR_duration_tk = tk.StringVar(value=inda.storage_duration_PR)
        input_PR_duration = tk.Entry(page17, font=("Helvetica", font_size_button), textvariable=PR_duration_tk)
        input_PR_duration.place(relx=0.3, rely=0.55, anchor="n", width=100)
        self.inputs.append(input_PR_duration)

        # storage duration PR
        label115 = tk.Label(
            page17,
            text="storage duration PR = ",
            font=("Helvetica", font_size_button)
        )
        label115.place(relx=0.15, rely=0.55, anchor="n")
        self.labels.append(label115)

        # unit storage duration PR
        label116 = tk.Label(
            page17,
            text="h",
            font=("Helvetica", font_size_button)
        )
        label116.place(relx=0.4, rely=0.55, anchor="n")
        self.labels.append(label116)

        # Entry for storage duration SR
        SR_storage_duration_tk = tk.StringVar(value=inda.storage_duration_SR)
        input_SR_storage_duration = tk.Entry(page17, font=("Helvetica", font_size_button), textvariable=SR_storage_duration_tk)
        input_SR_storage_duration.place(relx=0.75, rely=0.55, anchor="n", width=100)
        self.inputs.append(input_SR_storage_duration)

        # storage duration SR
        label117 = tk.Label(
            page17,
            text="storage duration SR = ",
            font=("Helvetica", font_size_button)
        )
        label117.place(relx=0.6, rely=0.55, anchor="n")
        self.labels.append(label117)

        # unit storage duration SR
        label118 = tk.Label(
            page17,
            text="h",
            font=("Helvetica", font_size_button)
        )
        label118.place(relx=0.9, rely=0.55, anchor="n")
        self.labels.append(label118)
        
        # Button for next page storage usage
        button38 = tk.Button(
            page17,
            text="submit storage usage",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.submit_storage_usage(inda, button38, input_SR_trading_energy_for_direct_activation, input_predict, input_match, input_safty_capacity, input_SR_storage_duration, input_PR_duration)
        )
        button38.place(relx=0.5, rely=0.65, anchor="n")
        self.buttons.append(button38)

        # Info text below
        info17 = tk.Label(
            page17,
            text="Trading is possible only on the SR energy market only. If you want to ensure a 100 % activation, your price bid must be lower than the average price. You can define by how much you want to underbid the price. It is recommended to charge a little bit more than needed because self-discharge and the power supply for the renewable plant will affect the available capacity. The programm calculates multiple possible cases within the prediction horizon and selects the one with the best revenue. Because either charging or discharging is allowed within the prediction horizon, a high prediction horizon limits the amount of cycles. Within 1 prediction horizon multiple operations can be planned, dependent on the matching factor. A high matching factor allows for more unfavorable prices compared to the best price, but enables more cycles. PR and SR storage durations indicate the requirements for market participation in terms of the minimal duration, the power must be available. Because recharging the storage while providing reserve power is not possible with this program, the value should be 1 h for both SR and PR to prevent penalty payments. For SR = 1 h is the right value. For PR the duration, dependend on storage hours of the battery. The defined value for PR will be devided by two because positive and negative PR or simultaneously provided.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info17.place(relx=0.5, rely=0.75, anchor="n")
        self.infos.append(info17)

        # Page 18: output parameters & simulation start
        page18 = tk.Frame(container)
        page18.place(relwidth=1, relheight=1)
        self.pages.append(page18)

        # title page 18
        head18 = tk.Label(page18, text="Start the simulation!", font=("Helvetica", font_size))
        head18.place(relx=0.5, rely=0.05, anchor="n")
        self.heads.append(head18)

        # Button for simulation start
        button39 = tk.Button(
            page18,
            text="start simulation",
            bg="white",
            font=("Helvetica", font_size_button),
            command=lambda: self.start_simulation(inda, root)
        )
        button39.place(relx=0.5, rely=0.5, anchor="n")
        self.buttons.append(button39)

        # Info text below
        info18 = tk.Label(
            page18,
            text="After starting the simulation, the window will close and the simulation will run as a background program. It will take some time. As soon as it is complete, a window will open again. The intermediate processes are visible in the console only.",
            font=("Helvetica", font_size_info),
            wraplength=info_width
        )
        info18.place(relx=0.5, rely=0.8, anchor="n")
        self.infos.append(info18)

        # Show first frame
        self.show_frame(self.pages[0])

        # run the init function in a loop to check if the user types in something or presses a button
        root.mainloop()

    
    def end(self,inda:input_data, IRR):
        
        """This function is called at the end of a program. It opens a window where the result is shown."""

        # create a window
        self.root = tk.Tk()
        self.root.title("Storage Simulation for Germany")
        self.root.state('zoomed')

        # create a container where the page is attributed to
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # set objects dependent on screen width of the user
        self.pc_width = self.root.winfo_screenwidth()
        font_size = int(self.pc_width / 60)

        # main page
        self.page_e1 = tk.Frame(self.container)
        self.page_e1.place(relwidth=1, relheight=1)

        # text on page indicates result
        tk.Label(self.page_e1, text="Simulation complete!", font=("Helvetica", font_size)).place(relx=0.5, rely=0.1, anchor="n")
        tk.Label(self.page_e1, text="Simulation result: ", font=("Helvetica", font_size)).place(relx=0.5, rely=0.3, anchor="n")
        tk.Label(self.page_e1, text="IRR = ", font=("Helvetica", font_size)).place(relx=0.4, rely=0.4, anchor="n")
        tk.Label(self.page_e1, text="%", font=("Helvetica", font_size)).place(relx=0.7, rely=0.4, anchor="n")
       
        # Info text below
        infoe1 = tk.Label(
            self.page_e1,
            text="All simulation data is available in folder: 'output'!",
            font=("Helvetica", font_size)
        )
        infoe1.place(relx=0.5, rely=0.8, anchor="n")
        self.infos.append(infoe1)

        # string variable of IRR for dynamic entries: the result is known only at the end of the program
        self.IRR_tk = tk.StringVar()
        tk.Label(self.page_e1, textvariable=self.IRR_tk, font=("Helvetica", font_size)).place(relx=0.6, rely=0.4, anchor="n")
        
        # refresh IRR on page
        self.IRR_tk.set(IRR)

        # show the only page
        self.show_frame(self.page_e1)

        # run this function until the window is closed
        self.root.mainloop()
        
    
    def fast_input(self, inda:input_data):
        
        """Use this function to provide an unchecked fast input to the program. If your input should be checked, use the grafical function gra.init()"""

        # set single input variables
        inda.start_simulation = True                        # no unit      # indicates if the simulation is active or not; will be true after all user inputs         
        inda.technology_storage_system = "Li-Ion (LFP)"     # no unit      # technology of the storage system. Allowed are: "Li-Ion (NMC)" and "Li-Ion (LFP)" // later: "Li-Ion (NCA)"  "Li-Ion (LTO)" can be added
        inda.year_commissioning = 2027                      # no unit      # year of commissioning
        inda.calculation_period = 20                        # a            # calculation period of the BESS
        inda.replacement_period = 10                        # a            # replacement period of the capacity unit of the BESS
        inda.intraday_active = True                         # no unit      # marketing strategy: sell electricity on Intraday market
        inda.primary_reserve_active = True                  # no unit      # marketing strategy: grid services: primary reserve
        inda.secondary_reserve_power_active = True          # no unit      # marketing strategy: grid services: secondary reserve power
        inda.secondary_reserve_energy_active = True         # no unit      # marketing strategy: grid services: secondary reserve energy without SR power
        inda.SR_simultaneously_active = False               # no unit      # marketing strategy: use positive and negative SR power at the same time (only possible if powerfactor >= 2)
        inda.purchase_active = True                         # no unit      # it is possible to store power from the grid
        inda.selfconsumption_active = False                 # no unit      # use storage for self consumption of the renewable plant
        inda.capacity_storage_min = float(30)               # in MWh       # (minimum) capacity of storage
        inda.capacity_storage_max = float(30)               # in MWh       # maximum capacity of storage (for optimization)
        inda.capacity_step = float(30)                      # in MWh       # step size for storage capacity from min to max (for optimization)
        inda.powerfactor_min = float(1)                     # in MWh/MW    # (minimum) factor capacity / power
        inda.powerfactor_max = float(1)                     # in MWh/MW    # maximum factor capacity / power (for optimization)
        inda.powerfactor_step = float(1)                    # in MWh/MW    # step factor capacity / power from min to max (for optimization)
        inda.grid_limit = float(164.9)                      # in MW        # The BESS might be not allowed to feed all power produced into the grid. This variable indicates such a feed-in grid limit
        inda.RES_consumption_costs = float(21.041)          # in ct/kWh    # costs, RES payes for electricity consumption incl. fee
        inda.fees_BESS = float(0.11)                        # in ct/kWh    # sum of levies for the BESS
        inda.discount_rate = float(2.0)                     # in %         # discounting future cash flows to present cash flows
        inda.initial_discount = float(564000)               # in €         # discount of any kind. Maybe there is a subsidy for the project.
        inda.initial_costs = float(0)                       # in €         # costs of any kind. Maybe the old transformer must be replaced by the new one.
        inda.renewable_technology = "wind_pv"               # no unit      # renewable technology connected to storage. Allowed are: 'wind'   'pv'   'wind_pv'   
        inda.opex_storage_MWh = float(0.273)                # in €/MWh     # Operation and Maintanance costs of storage system per MWh produced energy; variable costs due to variation of cycle number are dependent on operation
        inda.DOD = float(80)                                # in %         # the average depts of discharge describes how deep the BESS is cycled 
        inda.cycles_per_year = int(1300)                    # no unit      # how many complete cycles = charge + discharge cycles should be simulated during the operation period?
        inda.recovery_time = int(90)                        # in min/cycle # how much time does the storage need after one complete active cylce to the next one at minimum for cooling down? 
        inda.recovery_activation = float(2)                 # cycles       # after how many cycles should the recovery mode be active?
        inda.pu_pe = int(100)                               # in %         # how much power of nominal power should be used? Due to unknown degradation it is easier for the user to enter the ratio of usable power to EOL power
        inda.self_consumption_pv = float(57.8)              # in kW        # self consumption of PV park in case of night or outages. The BESS can provide supply power
        inda.self_consumption_wind = float(57.8)            # in kW        # self consumption of wind park in case of night or outages. The BESS can provide supply power
        inda.self_discharge = float(4)                              # in %/month   # how much capacity will be lost by self-discharge
        inda.SR_trading_energy_for_direct_activation = float(40)    # in €/MWh     # how much lower must the price bit be compared to average for assumed 100 % propable activation?
        inda.factor_penalty = float(1.2)                            # no unit      # if a perfomance can not be provided, a penalty must be paid. The amount can be adjusted higher than the outstanding income
        inda.prediction_horizon = int(8)                            # in 0.25 h    # number of timestamps (each 0.25 h) that are predicted by the program in simulation mode.
        inda.storage_duration_PR = float(1)                         # in h         # how much capacity will be reserved for PR ?
        inda.storage_duration_SR = float(1)                         # in h         # how much capacity will be reserved for SR ?
        inda.storage_degradation_costs = float(8.486)               # in €/MW/cycle     # for Redispatch measures, the cycle degradation costs are compensated as well. Enter the costs of one cycle.
        inda.safty_factor_capactiy  = float(2)                      # in %              # because self-discharge and RES+P are not considered in the planning phase, there should be a safty factor to charge a little more than needed to ensure stable discharge operation
        inda.loss_not_optimal_market_behavior = float(20)           # in %              # the distribution of revenues will follow the optimal possible way. In real, it should be less because in case of an auction, it will not be won every time.
        inda.matching_factor = float(1.5)                           # no unit           # the prediction horizon will calculate the revenue for multiple cases. If one case is selected, other cases can be combined with the first one but only if they are almost as good as the first. This factor describes how good the matching should be. 1 = best match, 2 = wide range of prices allowed -> will lead to more cycles
        inda.RTE_annual_degradation = float(0.2)                    # percentage points # annual degradation of RTE
        inda.RTE_SOC_dependency = float(26)                         # percentage points # for SOC = 100 %, additional RTE losses can be estimated, defined here. Better would it be to use a linear approximation
        inda.residual_value = float(38)                             # in €/kWh          # income for selling the capacity unit after operation each replacement period. If costs are estimated, negative values are allowed

        # set start and end year of Excel File
        inda.excel_year_start = 2025                        # no unit      # first year in Excel file start date: 01.01.excel_year_start 00:15
        inda.excel_year_end = 2050                          # no unit      # last year in Excel file (end date: 01.01.excel_year_end 00:00); the end year itself is not within the data, only the first date of the end year

        # calculate some variables of start and end time and capacity and power
        inda.end_year = inda.calculation_period + inda.year_commissioning   # end year is out of simulation!
        inda.simulation_capacity = inda.capacity_storage_min
        inda.simulation_power_factor = inda.powerfactor_min
        inda.simulation_power = inda.simulation_capacity / inda.simulation_power_factor
        
        # load data from Excel files
        kk=[True]

        if(inda.primary_reserve_active==True):

            xlx.load_activation_primary(inda,kk)
            xlx.load_primary_prices(inda,kk)
       
        if(inda.secondary_reserve_power_active==True or inda.secondary_reserve_energy_active == True):
    
            xlx.load_activation_secondary(inda,kk)
            xlx.load_secondary_prices(inda,kk)
        
        xlx.load_intraday(inda,kk)
        xlx.load_capex_opex(inda)
        xlx.load_curtailments_GO(inda,kk)
        xlx.load_grid_charge_vectors(inda,kk)
        xlx.load_losses_pv(inda,kk)
        xlx.load_losses_storage(inda,kk)
        xlx.load_losses_wind(inda,kk)
        xlx.load_power_pv(inda,kk)
        xlx.load_power_wind(inda,kk)
        xlx.load_system_RTE(inda)

        if(kk[0]==False):
            
            print("Input incomplete with ERROR\n")


    def  refresh_excel_data(self, inda:input_data):

        """If some variables but not all are changed between simulations, you dont have to load all the data again but call this refreshing function which will updata CAPEX, OPEX and RTE."""

        kk=[True]

        xlx.load_capex_opex(inda)
        xlx.load_system_RTE(inda)

        # trim the data to the length of the calculation period
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
        next_replacement = inda.replacement_period

        for j in range(len(inda.roundtrip_efficiency)):
            
            # if the storage should be replaced every 2 years and the simulation period is two years, the storage is not replaced. The replacement will take place after year 2 which is out of the simulation
            if(j+1>next_replacement):    
               
                next_replacement = next_replacement + inda.replacement_period
                
            elif(j>0):
              
                # annual degradation is given in percentage points; not %
                inda.roundtrip_efficiency[j] = (inda.roundtrip_efficiency[j-1] - inda.RTE_annual_degradation)  
                inda.capex_storage_kWh[j] = inda.capex_storage_kWh[j-1]
