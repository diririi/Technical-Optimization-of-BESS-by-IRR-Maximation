# import libraries and classes needed

from grafics import Grafics
from input_data import input_data
from output_data import output_data
from calculation import calculation
from simulation_data import simulation_data
import pickle
import types
import numpy as np

# it is possible to generate a exe with commands: # pip install pyinstaller # pyinstaller --onefile .\.venv\main.py

# generate objects of included classes

inda = input_data()
sim = simulation_data()
gra = Grafics(inda)
out = output_data(inda)
calc = calculation(inda, sim)

# exclude some variables from loading previousely saved values

EXCLUDE_VARS = {"IRRs", "usable_powers", "usable_capacities", "predict", "match", "replace", "power_factor", "grid", "cycles"}     # exclud from storage in program backup data


def start_main_program():

    """The main program is activated by default including a single simulation and a graphical interface with user input checks."""

    # The user determines all relevant simulation parameters via grafical interface. They are checked and stored in 'inda'. The user starts the simulation.
    gra.init(inda)                          
    print("user: started simulation\n")

    # generates the renewable production vector and converts all simulation vectors to the required length.
    calc.equalize_vectors(inda)     
    print("vectors have equal length.\n")

    # excecutes a single simulation including all defined excel outputs
    single_simulation()
    print("simulation and output complete.\n")

    gra.end(inda,round(sim.IRR,2))


def start_default_simulation():

    """Some calculation functions are summarized within this function that should be activated together. This includes: main, degradation and financial simulation."""
    
    calc.simulation_main_program(inda, sim)
    print("main simulation completed.\n")

    calc.degradation_calculation(inda,sim)
    print("degradation calculation completed.\n")

    calc.calc_annual_costs_revenue(inda,sim)
    print("financial calculation completed.\n")


def build_planfile():   

    """Some calculation functions are summarized within this function that should be activated together. This includes: comparable prices, optimum price matrices, possible operation periods, sorted prices and corrected plan operation."""

    calc.generate_comparable_price_timelines(inda)
    print("comparable price timelines generated.\n")    

    calc.generate_optimum_price_matrices(inda)     
    print("optimum price matrices generated.\n")

    calc.extract_possible_operation_periods(inda, sim)
    print("possile operation periodes extracted.\n")

    calc.generate_plan_operation(inda) 
    print("plan operation calculated.\n")

    calc.sort_price_vectors(inda,sim)       
    print("all price matrices sorted.\n")

    calc.correct_plan_reserve_period(inda)
    print("plan corrected by considering 4 h periodes of reserve markets.\n")


def optimum_IRR_capacity_power():

    """Call this function to perform a stack simulation with variable power and capacity, defined in this function. The other input parameters will be imported from the function gra.fast_input. The result with optimum IRR is displayed in an Excel File."""

    gra.fast_input(inda)
    print("The default input is loaded into the program.\n")

    # Because loading the input data takes most of the time, the whole actual program is stored in a file that can be imported much faster.
    variables_to_save_a = {
        k: v for k, v in globals().items()
        if not isinstance(v, types.ModuleType)
    }
    with open("variables_input.pkl", "wb") as f:
        pickle.dump(variables_to_save_a, f)
    print("Safe File of Input data complete.\n")

    # define the amount of simulations for power and capacity in gra.fast_input by setting min, max & step size. The program sill needs all the data also in the Excel file, otherwhise the input will be rounded to the next valid value.
    # + 1 to simulate inclusive min & max; e.g. from 2 to 10 MWh in step 2 = 2,4,6,8,10 = 5 steps  
    amount_steps_capacity = int((inda.capacity_storage_max - inda.capacity_storage_min) / inda.capacity_step + 1)          
    amount_steps_powerfactor = int((inda.powerfactor_max - inda.powerfactor_min) / inda.powerfactor_step + 1)         

    # number of stack simlation: each simulation belongs to one output file
    simulation_number = 0       

    # saved results as vectors over multiple simulations
    IRRs = np.full(amount_steps_capacity * amount_steps_powerfactor, -100, dtype=float)  
    usable_powers = np.full(amount_steps_capacity * amount_steps_powerfactor, 0, dtype=float)
    usable_capacities = np.full(amount_steps_capacity * amount_steps_powerfactor, 0, dtype=float)  

    # loop for iteration of capacity
    for C in range(amount_steps_capacity):                       

        # loop for iteration of power_factor
        for P in range(amount_steps_powerfactor):                   

            print("Simulation Number ", simulation_number, "started!\n")

            #regenerate original input variables created in gra.init() or gra.fast_input() to overwrite previous simulation results
            
            # delete all data
            inda.__dict__.clear()
            inda.__init__()
            sim.__dict__.clear()
            sim.__init__()

            # load previous saved input data to safe time
            with open("variables_input.pkl", "rb") as f:
                loaded_vars = pickle.load(f)
            # do not refresh excluded variables of simulation results
            for k, v in loaded_vars.items():
                if k not in EXCLUDE_VARS:
                    globals()[k] = v

            # change simulation power & capacity linearly:
            inda.simulation_capacity = inda.capacity_storage_min + C * inda.capacity_step
            inda.simulation_power_factor = inda.powerfactor_min + P * inda.powerfactor_step
            inda.simulation_power = inda.simulation_capacity / inda.simulation_power_factor

            # if simulation capacity & power change, CAPEX & OPEX change as well   # the simulation power & capacity may be adjusted to valid values!
            gra.refresh_excel_data(inda)   

            # convert all vectors to the desired length
            calc.equalize_vectors(inda)

            # perform a simulaiton with changed input variables
            build_planfile()    
            start_default_simulation()  
            
            # save for each simulation a file of summarized in- and outputs
            out.generate_individual_simulation_output(inda,simulation_number,sim)   

            IRRs[simulation_number] = sim.IRR
            usable_powers[simulation_number] = inda.simulation_power
            usable_capacities[simulation_number] = inda.simulation_capacity

            simulation_number = simulation_number + 1

    # print results as Excel File
    out.IRR_martix(IRRs, usable_capacities, usable_powers)

    # determine best result
    j = np.argmax(IRRs)
    print("optimum result at index: ", j, ". Results available in IRR Matrix Excel File.")

    # clear all again
    inda.__dict__.clear()
    inda.__init__()
    sim.__dict__.clear()
    sim.__init__()

    # load saved input variables of best result again
    with open("variables_input.pkl", "rb") as f:
        loaded_vars = pickle.load(f)
    for k, v in loaded_vars.items():
        if k not in EXCLUDE_VARS:
            globals()[k] = v

    inda.simulation_capacity = usable_capacities[j]
    inda.simulation_power = usable_powers[j]
    inda.simulation_power_factor = inda.simulation_capacity / inda.simulation_power

    # performed simulation of best result again
    gra.refresh_excel_data(inda)       
    calc.equalize_vectors(inda)
    build_planfile()
    start_default_simulation()

    # outputs
    out.print_res_production(inda)
    out.print_modified_input_prices(inda)
    out.print_output_main(sim,inda)
    out.print_battery_parameters(sim,inda)
    out.print_annual_costs(sim)

    gra.end(inda, round(IRRs[j],2))


def optimum_IRR_cycles_predict():

    """Call this function to perform a stack simulation with variable cycles and prediction horizon, defined in this function. The other input parameters will be imported from the function gra.fast_input. The result with optimum IRR is displayed in an Excel File."""

    # load default import defined in this function:
    gra.fast_input(inda)

    # save input variables in extra file to be faster importable
    variables_to_save_a = {
        k: v for k, v in globals().items()
        if not isinstance(v, types.ModuleType)
    }
    with open("variables_input.pkl", "wb") as f:
        pickle.dump(variables_to_save_a, f)
    print("Safe File Input complete.\n")

    simulation_number = 0      

    # output variables
    IRRs = np.full(4 * 4, -100, dtype=float)  
    predict = np.full(4 * 4, 0, dtype=float)
    cycles = np.full(4 * 4, 0, dtype=float)  

    for C in range(4):                         

        for P in range(4):                        

            print("Simulation Number ", simulation_number, "started!\n")

            # reset structures for new input
            inda.__dict__.clear()
            inda.__init__()
            sim.__dict__.clear()
            sim.__init__()

            # load saved input_file without result variables
            with open("variables_input.pkl", "rb") as f:
                loaded_vars = pickle.load(f)
            for k, v in loaded_vars.items():
                if k not in EXCLUDE_VARS:
                    globals()[k] = v

            # refresh prediction horizon and cycles per year linear for each simulation
            inda.prediction_horizon = 6 + P * 1
            inda.cycles_per_year = 1000 + C * 100
          
            # perform new simulation with refreshed variables
            gra.refresh_excel_data(inda)   
            calc.equalize_vectors(inda)
            build_planfile()  
            start_default_simulation() 
            
            # Excel output of each simulation
            out.generate_individual_simulation_output(inda,simulation_number,sim) 

            # save results of each simulation
            IRRs[simulation_number] = sim.IRR
            predict[simulation_number] = inda.prediction_horizon
            cycles[simulation_number] = sim.count_cycles

            simulation_number = simulation_number + 1

    # determine best result and create output file of all results
    out.IRR_matrix_cycles_predict(IRRs,cycles,predict)
    j = np.argmax(IRRs)
    print("optimum result at index: ", j, ". Results are visible in Excel File.")


def single_simulation():

    """Call this function after the import of all input parameters into the program and cutting the vectors to the desired lengths. One Simulation inclusive outputs will be performed."""

    # calculations
    calc.generate_comparable_price_timelines(inda)
    print("comparable price timelines generated.\n")       
    calc.generate_optimum_price_matrices(inda)     
    print("optimum price matrices generated.\n")
    calc.extract_possible_operation_periods(inda, sim)
    print("possile operation periodes extracted.\n")
    calc.generate_plan_operation(inda) 
    print("plan operation calculated.\n")
    calc.sort_price_vectors(inda,sim)      
    print("all price matrices sorted.\n")
    calc.correct_plan_reserve_period(inda)
    print("plan corrected by considering 4 h periodes of reserve markets.\n")
    calc.simulation_main_program(inda, sim)
    print("main simulation complete\n")
    calc.degradation_calculation(inda,sim)
    print("degradation calculation complete\n")
    calc.calc_annual_costs_revenue(inda,sim)
    print("financial output calculation complete\n")

    # outputs
    number_simulation = 0
    out.generate_individual_simulation_output(inda,number_simulation,sim)
    out.print_annual_costs(sim)
    out.print_res_production(inda)
    out.print_norm_prices(inda)
    out.print_modified_input_prices(inda)
    out.print_plan_operation(inda)
    out.print_battery_parameters(sim,inda)
    out.print_output_main(sim,inda)


if __name__ == "__main__":   

    # This is the main function where all starts. Dependent on program usage, choose the related functions!                  

    # The main program includes the grafical user input inclusive input validation and a single simulation with Excel Outputs. The other functions must be commented.
    start_main_program() 

    # To simulate a sensitivity analysis of variable capacity and power, select the following function and comment the others.     
    #optimum_IRR_capacity_power()

    # To simulate a sensitivity analysis of variable cycles and prediction horizon, select the following function and comment the others.     
    #optimum_IRR_cycles_predict()

    # Add here other possible functions to test parameter variation or simular.

