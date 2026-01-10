#1. Master Production Scheduling:
########################################################################################################################
#Importing required libraries:
import pandas as pd #Data handling
import pulp #Linear programming
########################################################################################################################
#Setting colors as global variables
CYAN = '\033[96m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'
#Loading & Cleaning Dataset:
def load_mps_dataset_csv(file_path):
	"""
	Loads the MPS dataset from a CSV file.
	"""
	#Read CSV file
	dataset_MPS = pd.read_csv(file_path, sep=";")  #sep=";" because dataset uses semicolons
	#Rename columns for consistency and clarity
	dataset_MPS.columns = ["Resource", "Product_X", "Product_Y", "Product_Z", "Inventory"]
	#Converting numeric columns to numbers (fix CSV string issue):
	for col in ["Product_X", "Product_Y", "Product_Z", "Inventory"]:
		dataset_MPS[col] = pd.to_numeric(dataset_MPS[col], errors="coerce")
	#Dropping completely empty rows (safety check):
	dataset_MPS = dataset_MPS.dropna(subset=["Resource"])
	return dataset_MPS
#dataset_MPS = load_mps_dataset_csv("Master_production_schedule/Dataset MPS.csv")
#Saving updated Dataset as csv.file:
def save_mps_dataset_csv(dataset_MPS, file_path="Dataset MPS.csv"):
	"""
	Saves the current MPS dataset back to CSV.
	"""
	dataset_MPS.to_csv(file_path, sep=";", index=False)
	print("Changes saved successfully.")

#Defining Functions for printing Profits aswell as current MPS-data:
def print_profit_summary(dataset_MPS):
	"""
	Prints a compact profit overview for each product.
	"""
	profit = dataset_MPS[dataset_MPS["Resource"] == "Profit per piece"].iloc[0]
	print("\n--- PROFIT PER PRODUCT ---")
	print(f"Product X: {profit['Product_X']}")
	print(f"Product Y: {profit['Product_Y']}")
	print(f"Product Z: {profit['Product_Z']}")

def show_mps_overview(dataset_MPS):
	"""
	Shows a clear overview of the current MPS data.
	"""
	print(f"\n{YELLOW}{'='*80}{RESET}")
	print(f"{YELLOW}{BOLD}{' '*27}CURRENT MPS DATA OVERVIEW{RESET}")
	print(f"{YELLOW}{'='*80}{RESET}")

	print_profit_summary(dataset_MPS)

	print("\n--- RESOURCE CONSTRAINTS ---")
	print(dataset_MPS[dataset_MPS["Resource"] != "Profit per piece"])

def refresh_view(dataset_MPS):
	"""
	Refreshes the displayed MPS data after changes.
	"""
	print("\nData updated successfully.")
	show_mps_overview(dataset_MPS)
########################################################################################################################
#1. Calculating optimal production:
#Idea: Gives the optimal number of each product. End.

#Splitting the Dataset into MPS Components:
def split_mps_data(dataset_MPS):
	"""
	Splits the MPS dataset into:
	- profit per product
	- inventory per resource
	- resource consumption matrix
	"""
	#-----------------------------------
	#1. Extracting profit information:
	profit_row = dataset_MPS[dataset_MPS["Resource"] == "Profit per piece"]
	profits = {
		"Product_X": float(profit_row["Product_X"].values[0]),
		"Product_Y": float(profit_row["Product_Y"].values[0]),
		"Product_Z": float(profit_row["Product_Z"].values[0])
	}
	#-----------------------------------
	#2. Removing profit row:
	resource_dataset_MPS = dataset_MPS[dataset_MPS["Resource"] != "Profit per piece"]
	#-----------------------------------
	#3. Inventory (resource limits):
	inventories = {
		row["Resource"]: row["Inventory"]
		for _, row in resource_dataset_MPS.iterrows()
	}
	#-----------------------------------
	#4. Consumption coefficients:
	consumption = resource_dataset_MPS.set_index("Resource")[[
		"Product_X", "Product_Y", "Product_Z"
	]]
	return profits, inventories, consumption

#Building & Solving the MPS Model:
def solve_mps(profits, inventories, consumption):
	"""
	Solves the Master Production Schedule using Linear Programming.
	"""
	#-----------------------------------
	#1. Creating optimization model:
	model = pulp.LpProblem("Master_Production_Schedule", pulp.LpMaximize)
	#-----------------------------------
	#2. Defining the Decision variables (Assumption of no real Minimum/Maximum Production Constraints!):
	x_X = pulp.LpVariable("Produce_X", lowBound=0)
	x_Y = pulp.LpVariable("Produce_Y", lowBound=0)
	x_Z = pulp.LpVariable("Produce_Z", lowBound=0)
	#-----------------------------------
	#3. Defining the Objective function:
	model += (
		profits["Product_X"] * x_X +
		profits["Product_Y"] * x_Y +
		profits["Product_Z"] * x_Z
	), "Total_Profit"
	#-----------------------------------
	#4. Resource constraints:
	for resource in inventories:
		model += (
			consumption.loc[resource, "Product_X"] * x_X +
			consumption.loc[resource, "Product_Y"] * x_Y +
			consumption.loc[resource, "Product_Z"] * x_Z
		) <= inventories[resource], f"Constraint_{resource}"
	#-----------------------------------
	#5. Solving MPS model:
	model.solve(pulp.PULP_CBC_CMD(msg=False))
	#-----------------------------------
	#6. Collecting results:
	results = {
		"status": pulp.LpStatus[model.status],
		"total_profit": pulp.value(model.objective),
		"production_plan": {
			"Product X": x_X.value(),
			"Product Y": x_Y.value(),
			"Product Z": x_Z.value()
		}
	}
	return results

#Displaying Results (for 1. MPS-Menu Output):
def display_mps_results(results):
	"""
	Prints MPS results in a clean and readable format.
	"""
	print("\n--- MASTER PRODUCTION SCHEDULE RESULTS ---")
	print(f"Optimization status: {results['status']}")
	print(f"Maximum profit: {results['total_profit']:.2f}\n")

	print("Optimal production quantities:")
	for product, quantity in results["production_plan"].items():
		print(f"  {product}: {quantity:.2f}")
########################################################################################################################
#2. Updating new profits:
#Idea: "Enter the product you want to change:", then "Enter the new profit for this product:"
def update_profit(dataset_MPS):
	"""
	Updates the profit of a selected product.
	Re-prompts only the invalid input.
	"""
	valid_products = {"X", "Y", "Z"}
	#--- PRODUCT LOOP ---
	while True:
		product = input("Enter the product you want to change (X, Y, Z): ").upper()
		if product in valid_products:
			break
		print("Invalid product. Please choose X, Y or Z.")
	#--- PROFIT LOOP ---
	while True:
		try:
			new_profit = float(input("Enter the new profit for this product: "))
			break
		except ValueError:
			print("Invalid number. Please enter a numeric value.")
	column_name = f"Product_{product}"
	dataset_MPS.loc[
		dataset_MPS["Resource"] == "Profit per piece",
		column_name
	] = new_profit
	print(f"Profit for Product {product} updated successfully!")
########################################################################################################################
#3. Updating new inventory:
#Idea: "Enter the resource:", then "Enter the new inventory:"
def update_inventory(dataset_MPS):
	"""
	Updates the inventory of a selected resource.
	Re-prompts only the invalid input.
	"""
	resources = set(dataset_MPS["Resource"])
	#--- RESOURCE LOOP ---
	while True:
		resource = input("Enter the resource name (e.g. Material A): ")
		if resource in resources:
			break
		print("Invalid resource name. Please enter an existing resource.")
	#--- INVENTORY LOOP ---
	while True:
		try:
			new_inventory = float(input("Enter the new inventory level: "))
			break
		except ValueError:
			print("Invalid number. Please enter a numeric value.")
	dataset_MPS.loc[
		dataset_MPS["Resource"] == resource,
		"Inventory"
	] = new_inventory
	print(f"Inventory for Resource {resource} updated successfully!")
########################################################################################################################
#4. Updating new resource use:
#Idea: "Enter the product:", then "Enter the resource:", then "Enter the new resource use":
def update_resource_use(dataset_MPS):
	"""
	Updates the resource consumption of a product.
	Re-prompts only the invalid input instead of restarting everything.
	"""
	valid_products = {"X", "Y", "Z"}
	resources = set(dataset_MPS["Resource"])
	#--- PRODUCT LOOP ---
	while True:
		product = input("Enter the product (X, Y, Z): ").upper()
		if product in valid_products:
			break
		print("Invalid product. Please choose X, Y or Z.")
	#--- RESOURCE LOOP ---
	while True:
		resource = input("Enter the resource (e.g. Material A): ")
		if resource in resources:
			break
		print("Invalid resource name. Please enter an existing resource.")
	#--- VALUE LOOP ---
	while True:
		try:
			new_value = float(input("Enter the new resource use: "))
			break
		except ValueError:
			print("Invalid number. Please enter a numeric value.")
	#Updating dataset:
	column_name = f"Product_{product}"
	dataset_MPS.loc[
		dataset_MPS["Resource"] == resource,
		column_name
	] = new_value
	print(f"Resource use updated: {resource} → Product {product}")
########################################################################################################################
#Full 1. MPS-Menu Loop:
def run_mps_menu():
	"""
	Interactive menu for Master Production Scheduling.
	"""
	#Loading dataset:
	dataset_MPS = load_mps_dataset_csv("Master_production_schedule/Dataset MPS.csv")

	#Printing mps-overview after selecting relevant menu-options:
	show_mps_overview(dataset_MPS)

	signal = True
	while True:
		if signal == True:
			print(f"\n{CYAN}{'='*80}{RESET}")
			print(f"{CYAN}{BOLD}{' '*24}MASTER PRODUCTION SCHEDULE MENU{RESET}")
			print(f"{CYAN}{'='*80}{RESET}")
			print("1. Calculate optimal production")
			print("2. Update profits")
			print("3. Update inventory")
			print("4. Update resource use")
			print("5. Save data changes as .csv")
			print("6. Go back to main menu")

		signal = True
		try:
			choice = input("\nEnter your choice (1-6): ")

			#1. Calculating optimal production:
			if choice == "1":
				profits, inventories, consumption = split_mps_data(dataset_MPS)
				results = solve_mps(profits, inventories, consumption)
				display_mps_results(results)

			#2. Updating profits:
			elif choice == "2":
				update_profit(dataset_MPS)
				refresh_view(dataset_MPS)

			#3. Updating inventory:
			elif choice == "3":
				update_inventory(dataset_MPS)
				refresh_view(dataset_MPS)

			#4. Updating resource use:
			elif choice == "4":
				update_resource_use(dataset_MPS)
				refresh_view(dataset_MPS)

			#5. Saving changes:
			elif choice == "5":
				confirm = input("Save all changes to CSV? (Y/N): ").upper()
				if confirm == "Y":
					save_mps_dataset_csv(dataset_MPS)
				else:
					print("Save canceled.")

			#6. Returning to main menu:
			elif choice == "6":
				print("Returning to main menu...")
				break

			else:
				print("Invalid choice. Please select a number between 1 and 6.")
				continue

			input("\nPress Enter to continue...")

		except EOFError:
			signal = False
			continue
		except KeyboardInterrupt:
			print("\n\nQuitting to main menu...")
			break
########################################################################################################################
