# import libraries and classes needed into this class
import pandas as pd 
import os
import sys
import numpy as np
import locale
from input_data import input_data
from simulation_data import simulation_data

# create the class output_data
class output_data:

    def __init__(self, inda: input_data):

        """This is the initialization function."""

        # needed for programming support by the IDE
        self.inda = inda    

        # A variable path is set which enables the activation of different PCs and via exe file or IDE.
        if getattr(sys, 'frozen', False):
            self.current_dir = os.path.dirname(sys.executable)     
        else:
            self.current_dir = os.path.dirname(__file__)   


    def print_res_production(self, inda: input_data):

        """An Excel Output with RES production is generated, including outages and GO curtailments. The resolution is 15-min and the length of the calculation period."""

        # define name of output file
        output_file = os.path.join(self.current_dir, 'output\\res_production.xlsx')

        # select data that should be written in output file
        df = pd.DataFrame()
        help_period = np.full(len(inda.RES_production), 0, dtype=float)
        for i in range(len(inda.RES_production)): help_period[i] = i
        df['timestamp (15-min)'] = help_period
        df['Renewable Production (kW)'] = inda.RES_production

        # convert the dataframe to the Excel File which is stored.
        df.to_excel(output_file, index=False)


    def print_norm_prices(self, inda:input_data):

        """The nominal prices of all selected markets are output in the unit € / MW / 15-min / full active. These prices are used for internal price comparison and calculation of the plan operation."""

        # output file name
        output_file = os.path.join(self.current_dir, 'output\\nominal_prices_EUR_MW_15_min_full_active.xlsx')

        # select the data needed for output
        df = pd.DataFrame() 
        help_period = np.full(len(inda.nominal_price_intraday), 0, dtype=float)
        for i in range(len(inda.nominal_price_intraday)): help_period[i] = i
        df['timestamp (15-min)'] = help_period
        df['Intraday norm Prices (€/(MW*full_active))'] = inda.nominal_price_intraday
        df['Buying RES Power norm Prices (€/(MW*full_active))'] = inda.nominal_price_RES_power

        # some data depend on the selected markets. If the market is not selected, then the prices are not included in the output.

        if(inda.secondary_reserve_energy_active==True or inda.secondary_reserve_power_active==True or inda.SR_simultaneously_active == True):

            df['Secondary positive Energy norm Prices (direct activation) (€/(MW*full_active))'] = inda.nominal_price_SR_energy_plus
            df['Secondary negative Energy norm Prices (direct activation) (€/(MW*full_active))'] = inda.nominal_price_SR_energy_minus

        if(inda.secondary_reserve_power_active==True):

            df['Secondary positive Power norm Prices (€/(MW*full_active))'] = inda.nominal_price_SR_power_plus
            df['Secondary negative Power norm Prices (€/(MW*full_active))'] = inda.nominal_price_SR_power_minus

        if(inda.SR_simultaneously_active==True):

            df['Secondary positive & negative combined Power norm Prices (€/(MW*full_active))'] = inda.nominal_price_SR_power_twice 

        if(inda.primary_reserve_active==True):

            df['Primary norm Prices (€/(MW*full_active))'] = inda.nominal_price_PR 

        # convert data frame to Excel
        df.to_excel(output_file, index=False)


    def print_modified_input_prices(self, inda: input_data):

        """These are the prices of markets in the original unit. All markets used in the simulation are output."""

        # Output file name
        output_file = os.path.join(self.current_dir, 'output\\modified_input_prices.xlsx')

        # select the data needed for output
        df = pd.DataFrame() 
        help_period = np.full(len(inda.intraday_prices), 0, dtype=float)
        for i in range(len(inda.intraday_prices)): help_period[i] = i
        df['timestamp (15-min)'] = help_period
        df['Intraday Prices (€ / MWh)'] = inda.intraday_prices
        
        # some data depend on the selected markets. If the market is not selected, then the prices are not included in the output.

        if (inda.primary_reserve_active==True):

            df['PR Prices in (€ / MW)'] = inda.primary_reserve_price

        if (inda.secondary_reserve_energy_active==True or inda.secondary_reserve_power_active==True or inda.SR_simultaneously_active==True):
          
            df['SR+E Prices (€ / MWh)'] = inda.secondary_reserve_price_MWh_plus
            df['SR-E Prices (€ / MWh)'] = inda.secondary_reserve_price_MWh_minus
            
        if(inda.secondary_reserve_power_active==True or inda.SR_simultaneously_active==True):
        
            df['SR+P Prices (€ / MW)'] = inda.secondary_reserve_price_MW_plus
            df['SR-P Prices (€ / MW)'] = inda.secondary_reserve_price_MW_minus

        # convert the data frame to an Excel
        df.to_excel(output_file, index=False)


    def print_plan_operation(self, inda:input_data):

        """Generates an output of the plan operation vector with length of the calculation period in 15-min resolution. The plan operation consists of inactive periods and the markets planned to participate."""

        # output file name
        output_file = os.path.join(self.current_dir, 'output\\plan_operation.xlsx')

        # select the data needed for output
        df = pd.DataFrame() 
        help_period = np.full(len(inda.V_plan_operation), 0, dtype=float)
        for i in range(len(inda.V_plan_operation)): help_period[i] = i
        df['timestamp (15-min)'] = help_period
        df['plan_operation'] = inda.V_plan_operation

        # convert the data frame to an Excel
        df.to_excel(output_file, index=False)


    def print_output_main(self, sim:simulation_data, inda:input_data):

        """Creates an Excel File of the most important output vectors: revenue, usable SOC and operation. Additional vectors are shown to understand the programs processes."""

        # output file name
        output_file = os.path.join(self.current_dir, 'output\\main_output_vectors.xlsx')

        # select the data needed for output 
        df = pd.DataFrame() 
        help_period = np.full(len(sim.SOC_sim), 0, dtype=float)
        for i in range(len(sim.SOC_sim)): help_period[i] = i
        df['timestamp (15-min)'] = help_period
        df['usable SOC (%)'] = sim.SOC_sim
        df['operation'] = sim.real_operation
        df['revenue (€)'] = sim.revenue
        df['real plan operation'] = sim.real_plan_operation
        df['old plan operation'] = inda.V_plan_operation
        df['best charging prices (€/(MW*full_active))'] = inda.M_best_charging_prices[:,0]
        df['best charging markets'] = inda.M_best_charging_prices[:,1]
        df['best discharging prices (€/(MW*full_active))'] = inda.M_best_discharging_prices[:,0]
        df['best discharging markets'] = inda.M_best_discharging_prices[:,1]
        df['best power prices (€/(MW*full_active))'] = inda.M_best_power_prices[:,0]
        df['best power markets'] = inda.M_best_power_prices[:,1]
        df['numbered charging'] = sim.sorted_charge
        df['numbered discharging'] = sim.sorted_discharge
        df['numbered reserve power'] = sim.sorted_reserve

        # convert the data frame to an Excel
        df.to_excel(output_file, index=False)


    def print_battery_parameters(self, sim:simulation_data, inda:input_data):

        """Creates an Excel file of battery parameters as degradation, cycles and costs of each replacement period."""

        # output file name
        output_file = os.path.join(self.current_dir, 'output\\battery_parameters.xlsx')

        # select the data needed for output and convert it to the length of the replacement period
        df = pd.DataFrame() 
        help_nominal_capacity = np.full(len(sim.capex_kWh_replacement), sim.nominal_capacity, dtype=float)
        help_nominal_power = np.full(len(sim.capex_kWh_replacement), sim.nominal_power, dtype=float)
        help_capacity_degradation = np.full(len(sim.capex_kWh_replacement), sim.degradation, dtype=float)
        help_power_degradation = np.full(len(sim.capex_kWh_replacement), sim.corrected_P_loss, dtype=float)
        help_DOD = np.full(len(sim.capex_kWh_replacement), sim.corrected_DOD, dtype=float)
        help_SOC = np.full(len(sim.capex_kWh_replacement), sim.average_SOC, dtype=float)
        help_cycles = np.full(len(sim.capex_kWh_replacement), sim.count_cycles, dtype=float)
        help_period = np.full(len(sim.capex_kWh_replacement), 0, dtype=float)
        for i in range(len(sim.capex_kWh_replacement)): help_period[i] = i

        # assign variables with description to data frame
        df['replacement period'] = help_period
        df['average number cycles'] = help_cycles
        df['nominal capacity (MWh)'] = help_nominal_capacity
        df['nominal power (MW)'] = help_nominal_power
        df['average DOD (%)'] = help_DOD
        df['average SOC (%)'] = help_SOC
        df['capacity degradation (%)'] = help_capacity_degradation
        df['power degradation (%)'] = help_power_degradation
        df['roundtrip efficiency (%)'] = sim.system_RTE_replacement
        df['CAPEX (€/kWh)'] = sim.capex_kWh_replacement

        # covert data frame to Excel
        df.to_excel(output_file, index=False)

    
    def print_annual_costs(self, sim:simulation_data):

        """Creates an Excel File of annual financial variables as costs and revenue. The IRR and NPV are indicated as well."""

        # output file name
        output_file = os.path.join(self.current_dir, 'output\\main_financial_output.xlsx')

        # select variables needed for output
        df = pd.DataFrame() 
        help_period = np.full(len(sim.annual_costs), 0, dtype=float)
        for i in range(len(sim.annual_costs)): help_period[i] = i
        df['year'] = help_period
        df['costs (€)'] = sim.annual_costs
        df['revenue (€)'] = sim.annual_revenue
        df['cashflow (€)'] = sim.cashflow
        df['result IRR (%)'] = sim.IRR
        df['result NPV (€)'] = sim.NPV
        df['annual production (MWh)'] = sim.annual_production
        df['annual consumption (MWh)'] = sim.annual_consumption

        # convert data frame to Excel
        df.to_excel(output_file, index=False)

    
    def generate_individual_simulation_output(self, inda: input_data, number, sim:simulation_data):

        """Creates an Excel File of the most important in- and output variables."""

        # output file name with variable number dependent on simulation number. First simulation = number 0
        output_file = os.path.join(self.current_dir, f'output\\individual_output_{number}.xlsx')
        
        # create data frame of 3 columns
        df = pd.DataFrame({
            'variable name': [],
            'value': [],
            'unit': []
        })

        # fill Excel with data considering 3 columns
        new_line = pd.DataFrame({'variable name': ['technology_storage_system'], 'value': [inda.technology_storage_system]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['year_commissioning'], 'value': [inda.year_commissioning]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['calculation_period'], 'value': [inda.calculation_period], 'unit': ['a']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['replacement_period'], 'value': [inda.replacement_period], 'unit': ['a']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['intraday_active'], 'value': [inda.intraday_active]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['primary_reserve_active'], 'value': [inda.primary_reserve_active]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['secondary_reserve_power_active'], 'value': [inda.secondary_reserve_power_active]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['purchase_active'], 'value': [inda.purchase_active]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['selfconsumption_active'], 'value': [inda.selfconsumption_active]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['simulation_capacity'], 'value': [inda.simulation_capacity], 'unit': ['MWh']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['nominal_capacity'], 'value': [sim.nominal_capacity], 'unit': ['MWh']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['simulation_power'], 'value': [inda.simulation_power], 'unit': ['MW']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['nominal_power'], 'value': [sim.nominal_power], 'unit': ['MW']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['grid_limit'], 'value': [inda.grid_limit], 'unit': ['MW']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['discount_rate'], 'value': [inda.discount_rate], 'unit': ['%']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['initial_discount'], 'value': [inda.initial_discount], 'unit': ['€ / a']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['initial_costs'], 'value': [inda.initial_costs], 'unit': ['€']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['renewable_technology'], 'value': [inda.renewable_technology]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['capex_storage_kWh[0]'], 'value': [inda.capex_storage_kWh[0]], 'unit': ['€ / kWh']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['capex_storage_kW[0]'], 'value': [inda.capex_storage_kW[0]], 'unit': ['€ / kW']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['opex_storage_MWh'], 'value': [inda.opex_storage_MWh], 'unit': ['€ / (kWh * a)']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['opex_storage_kW[0]'], 'value': [inda.opex_storage_kW[0]], 'unit': ['€ / (kW * a)']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['roundtrip_efficiency[0]'], 'value': [inda.roundtrip_efficiency[0]], 'unit': ['%']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['corrected_DOD'], 'value': [sim.corrected_DOD], 'unit': ['%']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['real cycles each replacement period'], 'value': [sim.count_cycles]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['target cycles per year'], 'value': [inda.cycles_per_year]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['recovery_time'], 'value': [inda.recovery_time], 'unit': ['min']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['recovery_activation'], 'value': [inda.recovery_activation], 'unit': ['cycles']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['usable power / EOL power'], 'value': [inda.pu_pe], 'unit': ['%']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['self_discharge'], 'value': [inda.self_discharge], 'unit': ['% / month']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['SR_trading_energy_for_direct_activation'], 'value': [inda.SR_trading_energy_for_direct_activation], 'unit': ['€ / MWh']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['factor_penalty'], 'value': [inda.factor_penalty]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['prediction_horizon'], 'value': [inda.prediction_horizon]})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['IRR'], 'value': [sim.IRR], 'unit': ['%']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['NPV'], 'value': [sim.NPV], 'unit': ['€']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['SOC Error'], 'value': [(sim.SOC_error / 35063 / inda.calculation_period * 100)], 'unit': ['%']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['storage_degradation_costs'], 'value': [inda.storage_degradation_costs], 'unit': ['€/MW/cycle']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['safty_factor_capactiy'], 'value': [inda.safty_factor_capactiy], 'unit': ['%']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['loss_not_optimal_market_behavior'], 'value': [inda.loss_not_optimal_market_behavior], 'unit': ['%']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['matching_factor'], 'value': [inda.matching_factor], 'unit': ['%']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['RTE_annual_degradation'], 'value': [inda.RTE_annual_degradation], 'unit': ['percentage points']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['at SOC=100 RTE degradation'], 'value': [inda.RTE_SOC_dependency], 'unit': ['percentage points']})
        df = pd.concat([df, new_line], ignore_index=True)
        new_line = pd.DataFrame({'variable name': ['residual_value'], 'value': [inda.residual_value], 'unit': ['€/kWh']})
        df = pd.concat([df, new_line], ignore_index=True)

        if(inda.primary_reserve_active==True):

            new_line = pd.DataFrame({'variable name': ['storage_duration_PR'], 'value': [inda.storage_duration_PR], 'unit': ['h']})
            df = pd.concat([df, new_line], ignore_index=True)

        if(inda.secondary_reserve_power_active==True or inda.SR_simultaneously_active==True):

            new_line = pd.DataFrame({'variable name': ['storage_duration_SR'], 'value': [inda.storage_duration_SR], 'unit': ['h']})
            df = pd.concat([df, new_line], ignore_index=True)

        if(inda.purchase_active==True or inda.selfconsumption_active == True):

            new_line = pd.DataFrame({'variable name': ['RES_consumption_costs'], 'value': [inda.RES_consumption_costs], 'unit': ['ct / kWh']})
            df = pd.concat([df, new_line], ignore_index=True)
            new_line = pd.DataFrame({'variable name': ['fees_BESS'], 'value': [inda.fees_BESS], 'unit': ['ct / kWh']})
            df = pd.concat([df, new_line], ignore_index=True)
            
        if(inda.renewable_technology=="pv" or inda.renewable_technology =="wind_pv"):
        
            new_line = pd.DataFrame({'variable name': ['self_consumption_pv'], 'value': [inda.self_consumption_pv], 'unit': ['kW']})
            df = pd.concat([df, new_line], ignore_index=True)
            
        if(inda.renewable_technology=="wind" or inda.renewable_technology =="wind_pv"):

            new_line = pd.DataFrame({'variable name': ['self_consumption_wind'], 'value': [inda.self_consumption_wind], 'unit': ['kW']})
            df = pd.concat([df, new_line], ignore_index=True)

        # data frame to Excel
        df.to_excel(output_file, index=False)


    def IRR_martix(self, IRR, capacity, power):

        """Creates an Excel file of the IRR of multiple Simulation Results dependent on usable capacity and power."""

        # output file name
        output_file = os.path.join(self.current_dir, 'output\\IRR_matrix.xlsx')

        # select variables for output
        df = pd.DataFrame() 
        df['IRR (%)'] = IRR
        df['usable capacity (MWh)'] = capacity
        df['usable power (MW)'] = power

        # convert data frame to Excel
        df.to_excel(output_file, index=False)

    
    def IRR_matrix_cycles_predict(self, IRR, cycles, predict):

        """Creates an Excel file of the IRR of multiple Simulation Results dependent on cycles per replacement period and the prediction horizon."""

        # output file name
        output_file = os.path.join(self.current_dir, 'output\\IRR_matrix.xlsx')

        # select variables for output
        df = pd.DataFrame() 
        df['IRR (%)'] = IRR
        df['cycles each replacement period'] = cycles
        df['prediction horizon'] = predict

        # convert data frame to Excel
        df.to_excel(output_file, index=False)
