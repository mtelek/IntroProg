import pandas as pd
import numpy as np
import os
import sys
from Lot_sizing import wagner_within as ww
from Lot_sizing import just_in_time as jit
from pathlib import Path

# COLOR CODES
BOLD = '\033[1m'
RESET = '\033[0m'
CYAN = '\033[96m'
GREEN = '\033[92m'
GREY = '\033[90m'

# GETTING BASE DIRECTORY AS A GLOBAL VARIABLE
BASE_DIR = Path(__file__).resolve().parent

def load_lot_sizing_data(csv_file='lot_sizing_data_2.csv'):
	csv_path = BASE_DIR / csv_file

	# READCSV
	if not csv_path.exists():
		raise FileNotFoundError(f"CSV file not found: {csv_path}")
	df = pd.read_csv(csv_path)

	# CHECK REQUIRED COLUMNS
	required_columns = ['Period', 'Demand', 'Setup_Cost', 'Holding_Cost', 'Min_Production', 'Max_Production']
	missing = [col for col in required_columns if col not in df.columns]
	if missing:
		raise ValueError(f"CSV missing required columns: {missing}")

	# STRIP STRINGS AND CHECK ONLY ALLOWED CHARACTERS (NUMBERS; DECIMAL POINTS; COMMA SEPERATORS)
	for col in df.columns:
		for i, val in enumerate(df[col]):
			val_str = str(val).strip()  # REMOVE SPACES
			if col in ['Period', 'Demand', 'Setup_Cost', 'Holding_Cost', 'Min_Production', 'Max_Production']:
				try:
					float(val_str)
				except ValueError:
					raise ValueError(f"Invalid value in column '{col}', row {i+2}: '{val}' (must be a number)")

	return {
		'periods': df['Period'].astype(float).tolist(),
		'demand': df['Demand'].astype(float).tolist(),
		'setup_cost': float(df['Setup_Cost'].iloc[0]),
		'holding_cost': float(df['Holding_Cost'].iloc[0]),
		'min_production': float(df['Min_Production'].iloc[0]),
		'max_production': float(df['Max_Production'].iloc[0]),
		'unit_cost': 50,
		'initial_inventory': 0 }

def generate_sample_data():
	periods = list(range(1, 13))
	demand = [120, 95, 110, 130, 115, 125, 140, 100, 135, 120, 150, 125]

	return {
		'periods': periods,
		'demand': demand,
		'setup_cost': 1000,
		'holding_cost': 0.5,
		'min_production': 50,
		'max_production': 1000,
		'unit_cost': 50,
		'initial_inventory': 0 }

def display_results(periods, demand, ww_plan, ww_inventory, ww_cost, jit_plan, jit_inventory, jit_cost, setup_cost, holding_cost):
	# PRINTING OUT RESULTS
	print(f"\n{GREEN}{'='*80}{RESET}")
	print(f"{GREEN}{BOLD}{' '*31}LOT SIZING RESULTS{RESET}")
	print(f"{GREEN}{'='*80}{RESET}")
	
	# PRINTING OUT WAGNER-WHITIN
	print("\n" + "-"*80)
	print("WAGNER-WHITIN (Optimal)")
	print("-"*80)
	print(f"Total Cost: €{ww_cost:.2f}")
	print(f"Production setups: {sum(1 for p in ww_plan if p > 0)}")
	print(f"Average inventory: {sum(ww_inventory)/len(ww_inventory):.1f} units")
	
	# PRINTING OUT JUST-IN-TIME
	print("\n" + "-"*80)
	print("JUST-IN-TIME (JIT)")
	print("-"*80)
	print(f"Total Cost: €{jit_cost:.2f}")
	print(f"Production setups: {sum(1 for p in jit_plan if p > 0)}")
	print(f"Average inventory: {sum(jit_inventory)/len(jit_inventory):.1f} units")
	
	# PRINTING OUT COMPARISON
	print("\n" + "-"*80)
	print(f"{' '*35}COMPARISON")
	print("-"*80)
	if jit_cost > 0:
		savings = jit_cost - ww_cost
		savings_percent = (savings / jit_cost) * 100
		print(f"Wagner-Whitin saves €{savings:.2f} ({savings_percent:.1f}%) compared to JIT")
	else:
		print("No cost savings to calculate")
	
	# PRINTING OUT DETAILED PRODUCTION PLAN
	print(f"\n{GREY}" + "="*80 + f"{RESET}")
	print(f"{GREY}{' '*28}DETAILED PRODUCTION PLAN{RESET}")
	print(f"{GREY}" + "="*80 + f"{RESET}")
	
	print(f"\n{'Period':<8} {'Demand':<8} {'WW Produce':<12} {'WW Inventory':<14} "
		  f"{'JIT Produce':<12} {'JIT Inventory':<12}")
	print("-" * 80)
	
	for i in range(len(periods)):
		print(f"{periods[i]:<8} {demand[i]:<8} {ww_plan[i]:<12} {ww_inventory[i]:<14.1f} "
			  f"{jit_plan[i]:<12} {jit_inventory[i]:<12.1f}")
	
	# PRINTING OUT THE TOTALS ROW
	print("-" * 80)
	print(f"{'Total':<8} {sum(demand):<8} {sum(ww_plan):<12} {'':<14} "
		  f"{sum(jit_plan):<12} {'':<12}")

def make_summary(periods, demand, ww_plan, ww_inventory, jit_plan, jit_inventory, setup_cost, holding_cost):
	#RETURNING SUMMARY IN ONE STRING
 	return f"""
Lot Sizing Analysis Summary
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Setup Cost: €{setup_cost}
Holding Cost: €{holding_cost}
Total Periods: {len(periods)}
Total Demand: {sum(demand)} units

Wagner-Whitin Results:
- Total Cost: €{sum([setup_cost if p > 0 else 0 for p in ww_plan]) + sum([h * holding_cost for h in ww_inventory]):.2f}
- Production Setups: {sum(1 for p in ww_plan if p > 0)}
- Total Production: {sum(ww_plan)} units
- Average Inventory: {sum(ww_inventory)/len(ww_inventory):.1f} units

JIT Results:
- Total Cost: €{sum([setup_cost if p > 0 else 0 for p in jit_plan]) + sum([h * holding_cost for h in jit_inventory]):.2f}
- Production Setups: {sum(1 for p in jit_plan if p > 0)}
- Total Production: {sum(jit_plan)} units
- Average Inventory: {sum(jit_inventory)/len(jit_inventory):.1f} units
"""   

def save_results_to_csv(periods, demand, ww_plan, ww_inventory, jit_plan, jit_inventory, setup_cost, holding_cost):
	try:
		root_dir = Path(__file__).resolve().parent.parent
		results_dir = root_dir / "Results"
		results_dir.mkdir(exist_ok=True)

		# GETTING FILENAMES WITH TIMESTAMPS
		timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
		csv_file = results_dir / f"lot_sizing_results_{timestamp}.csv"
		summary_file = results_dir / f"summary_lot_sizing_results_{timestamp}.txt"

		# SAVE CSV
		df = pd.DataFrame({
			'Period': periods,
			'Demand': demand,
			'WW_Production': ww_plan,
			'WW_Inventory': ww_inventory,
			'JIT_Production': jit_plan,
			'JIT_Inventory': jit_inventory
		})
		df.to_csv(csv_file, index=False)
		print(f"Results saved to {csv_file}")

		# SAVE SUMMARY
		summary = make_summary(periods, demand, ww_plan, ww_inventory, jit_plan, jit_inventory, setup_cost, holding_cost)
		with open(summary_file, 'w') as f:
			f.write(summary)
		print(f"Summary saved to {summary_file}")

	except Exception as e:
		print(f"Error saving results: {e}")

def display_menu():
    # DISPLAYING LOT SIZING MODULE MENU
	print(f"\n{CYAN}{'='*80}{RESET}")
	print(f"{CYAN}{BOLD}{' '*29}LOT SIZING MODULE MENU{RESET}")
	print(f"{CYAN}{'='*80}{RESET}")
	print("1. Run Lot Sizing Analysis (with sample data)")
	print("2. View sample CSV format")
	print("3. Load data from CSV file")
	print("4. Return to main menu")

def print_sample_data():
    # PRINTING OUT SIMPLE DATA
	sample = generate_sample_data()

	print("\n" + "-"*80)
	print(f"{' '*32}Sample CSV format:")
	print("-"*80)
	print("Period,Demand,Setup_Cost,Holding_Cost,Min_Production,Max_Production")

	for p, d in zip(sample['periods'], sample['demand']):
		print(f"{p},{d},{sample['setup_cost']},{sample['holding_cost']},"
			  f"{sample['min_production']},{sample['max_production']}")

	print("\nCreate a file with this format and save it as 'lot_sizing_data_2.csv'")

def run_lot_sizing(data=None):
	# LOAD DATA
	if data is None:
		data = load_lot_sizing_data()
	
	# EXTRACT DATA
	periods = data['periods']
	demand = data['demand']
	setup_cost = data['setup_cost']
	holding_cost = data['holding_cost']
	initial_inventory = data['initial_inventory']
	
	# RUN WAGNER-WITHIN ALGORITHM
	ww_plan, ww_inventory, ww_cost = ww.wagner_whitin_algorithm(
		demand, setup_cost, holding_cost, initial_inventory)
	
	# RUN JIT HEURISTIC
	jit_plan, jit_inventory, jit_cost = jit.jit_heuristic(
		demand, setup_cost, holding_cost, initial_inventory)
	
	# DISPLAY RESULTS
	display_results(periods, demand, ww_plan, ww_inventory, ww_cost,
		jit_plan, jit_inventory, jit_cost, setup_cost, holding_cost)
	
	# ASK IF USER WANTS TO SAVE RESULTS
	save = input("\nSave results to CSV? (y/n): ").lower()
	if save == 'y':
		save_results_to_csv(periods, demand, ww_plan, ww_inventory, 
			jit_plan, jit_inventory, setup_cost, holding_cost)
	
def main():
	signal = True
	while True:
		if (signal == True):
			display_menu()
		signal = True
		
		try:
			choice = input("\nEnter your choice (1-4): ").strip()
			
			if choice == '1':
				data = generate_sample_data()
				run_lot_sizing(data)
			elif choice == '2':
				print_sample_data()
			elif choice == '3':
				filename = input("Enter CSV filename (or press Enter for default sample data): ").strip()
				if filename == "":
					filename = "lot_sizing_data_2.csv"
				try:
					data = load_lot_sizing_data(filename)
					run_lot_sizing(data)
				
				except FileNotFoundError as e:
					print(e)
					signal = False
					continue
				except Exception as e:
					print(f"Error loading CSV: {e}")
					signal = False
					continue
			elif choice == '4':
				print("Returning to main menu...")
				break
			else:
				print("Invalid choice. Please try again.", end="")
				signal = False
				continue
			input("\nPress Enter to continue...")
			
		except EOFError: # WHEN PRESSING Ctrl+D
			signal = False
			continue
		except KeyboardInterrupt: # WHEN PRESSING Ctrl+C
			print("\n\nQuitting to main menu...")
			break
		except Exception as e: # WHEN HAVING ERRORS
			print(f"An error occured: {e}")

# FOR TESTING THE FILE INDEPENDENTLY
if __name__ == "__main__":
	print("Running Lot Sizing Module...")
	main()
