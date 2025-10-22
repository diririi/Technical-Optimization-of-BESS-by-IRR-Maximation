# import libraries and classes
import pandas as pd 
import os
import sys
import numpy as np
from input_data import input_data

# main class of file
class excel_data:

    def __init__(self, inda: input_data):

        """initialization function of this class. The input vectors of Excel files are extracted in this class."""

        # helping command for IDE
        self.inda = inda   

        # get relative paths of computer to enable usage on different computers
        if getattr(sys, 'frozen', False):

            # If the programm is as .exe compiled take folder of .exe
            self.current_dir = os.path.dirname(sys.executable)     

        else:
            
            # enable usage on multiple computers as variable directory of program file
            self.current_dir = os.path.dirname(__file__)    


    def load_grid_charge_vectors(self, inda, k):

        """This function imports power and energy dependent grid charges from Excel files to the simulation."""

        # read Excel grid_charges_kW
        input_file = os.path.join(self.current_dir, 'data\\grid_charges_kW.xlsx')
        df = pd.read_excel(input_file)

        # ensure that columns A (years) and B grid charges exist
        if 'year' not in df.columns or 'grid_charges_kW' not in df.columns:
            raise ValueError("check column names of Excel!")
        
        # filter the rows based on the year range   # end year is excluded from calculation
        filtered_df = df[(df['year'] >= inda.year_commissioning) & (df['year'] < inda.end_year)]    

        # extract the values from column B
        inda.grid_charges_kW = filtered_df['grid_charges_kW'].values.flatten()


        # read Excel: grid_charges_kWh.xlsx
        input_file = os.path.join(self.current_dir, 'data\\grid_charges_kWh.xlsx')
        df = pd.read_excel(input_file)

        # trim all column names and strip whitespace
        df.columns = df.columns.map(lambda x: str(x).strip())

        # filter defined years of operation
        selected_years = [str(year) for year in range(inda.year_commissioning, inda.end_year)]

        # extract row related to commissioning year
        filtered_row = df[df['year'] == inda.year_commissioning]

        # covert values to vector
        inda.grid_charges_kWh = filtered_row[selected_years].values.flatten()


    def load_power_pv(self, inda, k):
        
        """This function imports the power of the PV plant from an Excel file to the program."""

        # read Excel power_pv.xlsx
        input_file = os.path.join(self.current_dir, 'data\\power_pv.xlsx')
        df = pd.read_excel(input_file)
        
        if "power_pv" in df.columns:

            # convert the column to a numpy vector
            inda.power_pv = df["power_pv"].to_numpy()
           
        else:
            
            k[0]=False

    
    def load_power_wind(self, inda, k):

        """This function imports the power of the wind plant from an Excel file to the program."""

        # read Excel power_wind.xlsx
        input_file = os.path.join(self.current_dir, 'data\\power_wind.xlsx')
        df = pd.read_excel(input_file)
        
        if "power_wind" in df.columns:

            # convert the column to a numpy vector
            inda.power_wind = df["power_wind"].to_numpy()

        else:

            k[0]=False


    def load_intraday(self, inda, k):

        """This function imports the Intraday prices from an Excel file to the program."""

        input_file = os.path.join(self.current_dir, 'data\\intraday_prices.xlsx')
        df = pd.read_excel(input_file)

        if "intraday_prices" in df.columns:

            inda.intraday_prices = df["intraday_prices"].to_numpy()

        else:

            k[0]=False


    def load_primary_prices(self, inda, k):
            
        """This function imports the primary reserve prices from an Excel file to the program."""

        input_file = os.path.join(self.current_dir, 'data\\primary_reserve_price.xlsx')
        df = pd.read_excel(input_file)

        if "primary_reserve_price" in df.columns:

            inda.primary_reserve_price = df["primary_reserve_price"].to_numpy()

        else:

            k[0]=False


    def load_secondary_prices(self, inda, k):
            
        """This function imports the positive and negative secondary reserve energy and power prices from an Excel file to the program."""

        input_file = os.path.join(self.current_dir, 'data\\secondary_reserve_energy_price_minus.xlsx')
        df = pd.read_excel(input_file)

        if "secondary_reserve_energy_price_minus" in df.columns:

            inda.secondary_reserve_price_MWh_minus = df["secondary_reserve_energy_price_minus"].to_numpy()

        else:

            k[0]=False

        input_file = os.path.join(self.current_dir, 'data\\secondary_reserve_energy_price_plus.xlsx')
        df = pd.read_excel(input_file)

        if "secondary_reserve_energy_price_plus" in df.columns:

            inda.secondary_reserve_price_MWh_plus = df["secondary_reserve_energy_price_plus"].to_numpy()

        else:

            k[0]=False

        input_file = os.path.join(self.current_dir, 'data\\secondary_reserve_power_price_minus.xlsx')
        df = pd.read_excel(input_file)

        if "secondary_reserve_power_price_minus" in df.columns:

            inda.secondary_reserve_price_MW_minus = df["secondary_reserve_power_price_minus"].to_numpy()

        else:

            k[0]=False

        input_file = os.path.join(self.current_dir, 'data\\secondary_reserve_power_price_plus.xlsx')
        df = pd.read_excel(input_file)

        if "secondary_reserve_power_price_plus" in df.columns:

            inda.secondary_reserve_price_MW_plus = df["secondary_reserve_power_price_plus"].to_numpy()

        else:

            k[0]=False

    
    def load_losses_wind(self, inda, k):

        """This function imports the wind outages from an Excel file to the program."""

        input_file = os.path.join(self.current_dir, 'data\\losses_wind.xlsx')
        df = pd.read_excel(input_file)
        
        if "losses_wind" in df.columns:

            inda.losses_wind = df["losses_wind"].to_numpy()

        else:

            k[0]=False

    
    def load_losses_pv(self, inda, k):

        """This function imports the PV outages from an Excel file to the program."""

        input_file = os.path.join(self.current_dir, 'data\\losses_pv.xlsx')
        df = pd.read_excel(input_file)
        
        if "losses_pv" in df.columns:

            inda.losses_pv = df["losses_pv"].to_numpy()

        else:

            k[0]=False


    def load_losses_storage(self, inda, k):

        """This function imports the BESS outages from an Excel file to the program."""

        input_file = os.path.join(self.current_dir, 'data\\losses_storage.xlsx')
        df = pd.read_excel(input_file)
        
        if "losses_storage" in df.columns:

            inda.losses_storage = df["losses_storage"].to_numpy()

        else:

            k[0]=False


    def load_activation_secondary(self, inda, k):

        """This function imports the activation vector of the secondary reserve from an Excel file to the program."""

        input_file = os.path.join(self.current_dir, 'data\\secondary_reserve_activation.xlsx')
        df = pd.read_excel(input_file)
        
        if "secondary_reserve_activation" in df.columns:

            inda.secondary_reserve_activation = df["secondary_reserve_activation"].to_numpy()

        else:

            k[0]=False


    def load_activation_primary(self, inda, k):

        """This function imports the activation vector of the primary reserve from an Excel file to the program."""

        input_file = os.path.join(self.current_dir, 'data\\primary_reserve_activation.xlsx')
        df = pd.read_excel(input_file)
        
        if "primary_reserve_activation" in df.columns:

            inda.primary_reserve_activation = df["primary_reserve_activation"].to_numpy()

        else:

            k[0]=False

    
    def load_curtailments_GO(self, inda, k):

        """This function imports the curtailments of the grid operator from an Excel file to the program."""

        input_file = os.path.join(self.current_dir, 'data\\curtailments_GO.xlsx')
        df = pd.read_excel(input_file)
        
        if "curtailments_GO" in df.columns:

            inda.curtailments_GO = df["curtailments_GO"].to_numpy()

        else:

            k[0]=False


    def round_to_nearest(self, value, valid_values):   
            
        """This function rounds the 'value' to the nearest 'valid_value'"""
            
        return min(valid_values, key=lambda x: abs(x - value))

    
    def load_capex_opex(self, inda:input_data):   

        """This function imports CAPEX and OPEX from Excel files to the program."""
      
        # read Excel: capex_storage_kWh.xlsx
        input_file = os.path.join(self.current_dir, 'data\\capex_storage_kWh.xlsx')
        df = pd.read_excel(input_file)

        # convert column to string
        df.columns = df.columns.map(str)
        
        # round to next valid value of list
        rounded_total_power = self.round_to_nearest(inda.simulation_power, inda.valid_total_power)
        rounded_hours = self.round_to_nearest(inda.simulation_power_factor, inda.valid_hours)
      
        # refresh recent simulation values by considering next valid values
        inda.simulation_capacity = rounded_total_power * rounded_hours
        inda.simulation_power = rounded_total_power
        inda.simulation_power_factor = rounded_hours

        print("\nSimulation capacity and power may be changed by program because of missing data in Excel Import Files. For this simulation: usable power = ", inda.simulation_power, " MW // usable capacity = ", inda.simulation_capacity, "MWh\n")

        # filter Excel for entries needed and make a copy
        filtered = df[
            (df['technology_storage_system'] == inda.technology_storage_system) &
            (df['total_power'] == rounded_total_power) &
            (df['hours'] == rounded_hours)
        ].copy()

        # create list of years with strings as column names
        year_columns = [str(jahr) for jahr in range(inda.year_commissioning, inda.end_year)]

        # check if years are existing
        year_columns = [jahr for jahr in year_columns if jahr in filtered.columns]
        
        # convert to numerical values
        filtered.loc[:, year_columns] = filtered.loc[:, year_columns].apply(pd.to_numeric, errors='coerce')

        # extract values for valid arguments as vector (dependent on years)
        inda.capex_storage_kWh = filtered.loc[:, year_columns].values.flatten()


        # read Excel: capex_storage_kW.xlsx
        input_file = os.path.join(self.current_dir, 'data\\capex_storage_kW.xlsx')
        df = pd.read_excel(input_file)

        # convert column to string
        df.columns = df.columns.map(str)

        # filter Excel for entries needed and make a copy
        filtered = df[
            (df['technology_storage_system'] == inda.technology_storage_system) &
            (df['total_power'] == rounded_total_power)
        ].copy()

        # create list of years with strings as column names
        year_columns = [str(jahr) for jahr in range(inda.year_commissioning, inda.end_year)]

        # check if years are existing
        year_columns = [jahr for jahr in year_columns if jahr in filtered.columns]
        
        # convert to numerical values
        filtered.loc[:, year_columns] = filtered.loc[:, year_columns].apply(pd.to_numeric, errors='coerce')

        # extract values for valid arguments as vector (dependent on years)
        inda.capex_storage_kW = filtered.loc[:, year_columns].values.flatten()


        # read Excel: opex_storage_kW.xlsx
        input_file = os.path.join(self.current_dir, 'data\\opex_storage_kW.xlsx')
        df = pd.read_excel(input_file)

        # convert column to string
        df.columns = df.columns.map(str)

        # filter Excel for entries needed and make a copy
        filtered = df[
            (df['technology_storage_system'] == inda.technology_storage_system) &
            (df['total_power'] == rounded_total_power) &
            (df['hours'] == rounded_hours)
        ].copy()

        # create list of years with strings as column names
        year_columns = [str(jahr) for jahr in range(inda.year_commissioning, inda.end_year)]

        # check if years are existing
        year_columns = [jahr for jahr in year_columns if jahr in filtered.columns]
        
        # convert to numerical values
        filtered.loc[:, year_columns] = filtered.loc[:, year_columns].apply(pd.to_numeric, errors='coerce')

        # extract values for valid arguments as vector (dependent on years)
        inda.opex_storage_kW = filtered.loc[:, year_columns].values.flatten()


    def load_system_RTE(self, inda):

        """This function imports the system RTE from an Excel file to the program."""
        
        # read Excel: system_roundtrip_efficiency.xlsx
        input_file = os.path.join(self.current_dir, 'data\\system_roundtrip_efficiency.xlsx')
        df = pd.read_excel(input_file)

        # Trim all column names and strip whitespace
        df.columns = df.columns.map(lambda x: str(x).strip())

        # Round to the nearest valid value
        rounded_pu_pe = self.round_to_nearest(inda.pu_pe, inda.valid_pu_pe)
        
        # Filter the DataFrame for valid entries
        filtered = df[
            (df['technology_storage_system'].str.strip() == inda.technology_storage_system.strip()) &
            (df['P_U / P_E'] == rounded_pu_pe)
        ].copy()

        # Extract year columns that exist in the DataFrame
        year_columns = [str(jahr) for jahr in range(inda.year_commissioning, inda.end_year)]
        year_columns = [col for col in year_columns if col in filtered.columns]

        # Ensure year columns are numeric
        filtered.loc[:, year_columns] = filtered.loc[:, year_columns].apply(pd.to_numeric, errors='coerce')

        # Flatten the values into a vector
        inda.roundtrip_efficiency = filtered.loc[:, year_columns].values.flatten()


    