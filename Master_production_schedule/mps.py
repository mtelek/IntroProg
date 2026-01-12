#1. Master Production Scheduling:
########################################################################################################################
#Importing required libraries:
from pathlib import Path  # Path Management
import os  # Environment
import pandas as pd #Data handling
import pulp #Linear programming
########################################################################################################################
#Setting colors as global variables
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

#Base Directory of this Module as a Global Variable:
BASE_DIR = Path(__file__).resolve().parent
MPS_DIR = BASE_DIR.parent / "Master_production_schedule"

#Results Directory:
RESULTS_DIR = MPS_DIR / "Results"
RESULTS_DIR.mkdir(exist_ok=True)

#Loading & Cleaning Dataset:
def load_mps_dataset(csv_file='mps_data.csv'):
    """
    Loads the MPS dataset from a CSV file.
    """
    file_path = MPS_DIR / csv_file
    #Read .csv:
    if not file_path.exists():
        raise FileNotFoundError(f".csv file not found: {file_path}")
    mps_dataset = pd.read_csv(file_path, sep=";")
    #Rename columns for consistency and clarity
    mps_dataset.columns = ["Resource", "Product_X", "Product_Y", "Product_Z", "Inventory"]
    #Converting numeric columns to numbers (fix CSV string issue):
    for col in ["Product_X", "Product_Y", "Product_Z", "Inventory"]:
        mps_dataset[col] = pd.to_numeric(mps_dataset[col], errors="coerce")
    #Dropping completely empty rows (safety check):
    mps_dataset = mps_dataset.dropna(subset=["Resource"])
    return mps_dataset

#Defining Functions for printing Profits as well as current MPS-data:
def print_profit_summary(mps_dataset):
    """
    Prints a compact profit overview for each product.
    """
    profit = mps_dataset[mps_dataset["Resource"] == "Profit per piece"].iloc[0]
    print("\n--- PROFIT PER PRODUCT ---")
    print(f"Product X: {profit['Product_X']}")
    print(f"Product Y: {profit['Product_Y']}")
    print(f"Product Z: {profit['Product_Z']}")

def show_mps_overview(mps_dataset):
    """
    Shows a clear overview of the current MPS data.
    """
    print(f"\n{CYAN}{'='*80}{RESET}")
    print(f"{CYAN}{BOLD}{' '*20}CURRENT MPS DATA OVERVIEW{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")

    print_profit_summary(mps_dataset)

    print("\n--- RESOURCE CONSTRAINTS ---")
    print(mps_dataset[mps_dataset["Resource"] != "Profit per piece"])

def refresh_view(mps_dataset):
    """
    Refreshes the displayed MPS data after changes.
    """
    print("\nData updated successfully.")
    show_mps_overview(mps_dataset)
########################################################################################################################
#5. Calculating optimal production:
#Idea: Gives the optimal number of each product. End.

#Splitting the Dataset into MPS Components:
def split_mps_data(mps_dataset):
    """
    Splits the MPS dataset into:
    - Profit per product
    - Inventory per resource
    - Resource consumption matrix
    """
    #-----------------------------------
    #Step 1. Extracting profit information:
    profit_row = mps_dataset[mps_dataset["Resource"] == "Profit per piece"]
    profits = {
        "Product_X": float(profit_row["Product_X"].values[0]),
        "Product_Y": float(profit_row["Product_Y"].values[0]),
        "Product_Z": float(profit_row["Product_Z"].values[0])
    }
    #-----------------------------------
    #Step 2. Removing profit row:
    resource_mps_dataset = mps_dataset[mps_dataset["Resource"] != "Profit per piece"]
    #-----------------------------------
    #Step 3. Inventory (resource limits):
    inventories = {
        row["Resource"]: row["Inventory"]
        for _, row in resource_mps_dataset.iterrows()
    }
    #-----------------------------------
    #Step 4. Consumption coefficients:
    consumption = resource_mps_dataset.set_index("Resource")[[
        "Product_X", "Product_Y", "Product_Z"
    ]]
    return profits, inventories, consumption

#Building & Solving the MPS Model:
def solve_mps(profits, inventories, consumption):
    """
    Solves the Master Production Schedule using Linear Programming.
    """
    #-----------------------------------
    #Step 1. Creating optimization model:
    model = pulp.LpProblem("Master_Production_Schedule", pulp.LpMaximize)
    #-----------------------------------
    #Step 2. Defining the Decision variables (Assumption of no real Minimum/Maximum Production Constraints!):
    x_x = pulp.LpVariable("Produce_X", lowBound=0, cat="Integer")
    y_y = pulp.LpVariable("Produce_Y", lowBound=0, cat="Integer")
    z_z = pulp.LpVariable("Produce_Z", lowBound=0, cat="Integer")
    #-----------------------------------
    #Step 3. Defining the Objective function:
    model += (
        profits["Product_X"] * x_x +
        profits["Product_Y"] * y_y +
        profits["Product_Z"] * z_z
    ), "Total_Profit"
    #-----------------------------------
    #Step 4. Resource constraints:
    for resource in inventories:
        model += (
            consumption.loc[resource, "Product_X"] * x_x +
            consumption.loc[resource, "Product_Y"] * y_y +
            consumption.loc[resource, "Product_Z"] * z_z
        ) <= inventories[resource], f"Constraint_{resource}"
    #-----------------------------------
    #Step 5. Solving MPS model:
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    #-----------------------------------
    #Step 6. Collecting results:
    results = {
        "status": pulp.LpStatus[model.status],
        "total_profit": pulp.value(model.objective),
        "production_plan": {
            "Product X": x_x.value(),
            "Product Y": y_y.value(),
            "Product Z": z_z.value()
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
#1. Updating new profits:
#Idea: "Enter the product you want to change:", then "Enter the new profit for this product:"
def update_profit(mps_dataset):
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
    mps_dataset.loc[
        mps_dataset["Resource"] == "Profit per piece",
        column_name
    ] = new_profit
    print(f"Profit for Product {product} updated successfully!")
########################################################################################################################
#2. Updating new inventory:
#Idea: "Enter the resource:", then "Enter the new inventory:"
def update_inventory(mps_dataset):
    """
    Updates the inventory of a selected resource.
    Re-prompts only the invalid input.
    """
    resources = set(mps_dataset["Resource"])
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
    mps_dataset.loc[
        mps_dataset["Resource"] == resource,
        "Inventory"
    ] = new_inventory
    print(f"Inventory for Resource {resource} updated successfully!")
########################################################################################################################
#3. Updating new resource use:
#Idea: "Enter the product:", then "Enter the resource:", then "Enter the new resource use":
def update_resource_use(mps_dataset):
    """
    Updates the resource consumption of a product.
    Re-prompts only the invalid input instead of restarting everything.
    """
    valid_products = {"X", "Y", "Z"}
    resources = set(mps_dataset["Resource"])
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
    mps_dataset.loc[
        mps_dataset["Resource"] == resource,
        column_name
    ] = new_value
    print(f"Resource use updated: {resource} → Product {product}")
########################################################################################################################
#4. Saving data changes as .csv:
#Idea: "Saving current dataset as .csv after selecting "2. Update profits", "3. Update inventory", "4. Update resource use" inside the folder "Master Production Schedule":
def save_mps_dataset_csv(mps_dataset, file_name="mps_dataset.csv"):
    """
    Saves the current MPS dataset as .csv file.
    """
    #Cleaning user input (remove quotes):
    file_name = file_name.strip('"').strip("'")
    #Ensuring correct extension:
    if not file_name.lower().endswith(".csv"):
        file_name += ".csv"

    csv_path = MPS_DIR / file_name

    try:
        mps_dataset.to_csv(csv_path, sep=";", index=False)
        print(f"Changes saved successfully to:\n{csv_path}")
    except PermissionError:
        print(
            f"Permission denied!\n"
            f"Warning: Please close the file if it is open in Excel:\n{csv_path}"
        )
########################################################################################################################
#6. Saving optimal production quantities as .csv:
#Idea:
def save_mps_results(results, file_name="mps_results.csv"):
    """
    Saves the last MPS optimization results as .csv and .txt files:
    """
    #Removing quotes if user typed them:
    file_name = file_name.strip('"').strip("'")
    #Removing extension if user typed .csv:
    base_name = Path(file_name).stem

    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    csv_file = RESULTS_DIR / f"{base_name}_{timestamp}.csv"
    summary_file = RESULTS_DIR / f"{base_name}_{timestamp}_summary.txt"

    #Saving as .csv file:
    data = pd.DataFrame({
        "Metric": [
            "Optimization Status",
            "Maximum Profit",
            "Product X",
            "Product Y",
            "Product Z"
        ],
        "Value/Quantity": [
            results["status"],
            results["total_profit"],
            results["production_plan"]["Product X"],
            results["production_plan"]["Product Y"],
            results["production_plan"]["Product Z"]
        ]
    })
    data.to_csv(csv_file, index=False)

    #Saving summary as .txt file:
    with open(summary_file, "w") as f:
        f.write(
            f"""Master Production Schedule Summary
Generated: {pd.Timestamp.now()}

Optimization Status: {results['status']}
Maximum Profit: {results['total_profit']:.2f}

Production Plan (Quantities):
- Product X: {results['production_plan']['Product X']}
- Product Y: {results['production_plan']['Product Y']}
- Product Z: {results['production_plan']['Product Z']}
"""
        )
    print(f"Results saved to:\n{csv_file}")
    print(f"Summary saved to:\n{summary_file}")
########################################################################################################################
#Full 1. MPS-Menu Loop:
def run_mps_menu():
    """
    Interactive menu for Master Production Scheduling.
    """
    #Loading dataset:
    mps_dataset = load_mps_dataset("mps_dataset.csv")

    #Remembering results of "1. Calculate optimal production quantities":
    last_results = None

    #Printing mps-overview after selecting relevant menu-options:
    show_mps_overview(mps_dataset)

    signal = True
    while True:
        if signal:
            print(f"\n{CYAN}{'='*80}{RESET}")
            print(f"{CYAN}{BOLD}{' '*24}MASTER PRODUCTION SCHEDULE MENU{RESET}")
            print(f"{CYAN}{'='*80}{RESET}")
            print("1. Update profits")
            print("2. Update inventory")
            print("3. Update resource use")
            print("4. Save data changes as .csv")
            print("5. Calculate optimal production quantities")
            print("6. Save optimal production quantities as .csv")
            print("7. Go back to main menu")

        signal = True
        try:
            choice = input("\nEnter your choice (1-7): ")

            #1. Updating profits:
            if choice == "1":
                update_profit(mps_dataset)
                refresh_view(mps_dataset)

            #2. Updating inventory:
            elif choice == "2":
                update_inventory(mps_dataset)
                refresh_view(mps_dataset)

            #3. Updating resource use:
            elif choice == "3":
                update_resource_use(mps_dataset)
                refresh_view(mps_dataset)

            #4. Saving data updates as .csv:
            elif choice == "4":
                save = input("Save all data changes? (y/n): ").lower()
                if save == "y":
                    file_name = input(
                        "Enter file name + press 'ENTER' or press 'ENTER' for default 'mps_dataset.csv': "
                    ).strip()
                    if file_name == "":
                        file_name = "mps_dataset.csv"
                    save_mps_dataset_csv(mps_dataset, file_name)
                else:
                    print("Save cancelled.")

            #5. Calculating optimal production quantities:
            elif choice == "5":
                profits, inventories, consumption = split_mps_data(mps_dataset)
                last_results = solve_mps(profits, inventories, consumption)
                display_mps_results(last_results)

            #6. Saving optimal production quantities as .csv:
            elif choice == "6":
                if last_results is None:
                    print("No optimization results available yet. Please run option 5 first.")
                else:
                    save = input("Save optimization results? (y/n): ").lower()
                    if save == "y":
                        file_name = input(
                            "Enter file name + press 'ENTER' or press 'ENTER' for default 'mps_results.csv': "
                        ).strip()
                        if file_name == "":
                            file_name = "mps_results.csv"
                        save_mps_results(last_results, file_name)
                    else:
                        print("Save cancelled.")

            #7. Returning to main menu:
            elif choice == "7":
                print("Returning to main menu...")
                break
            else:
                print("Invalid choice. Please select a number between 1 and 7.")
                continue
            input("\nPress Enter to continue...")

        except EOFError:
            signal = False
            continue
        except KeyboardInterrupt:
            print("\n\nQuitting to main menu...")
            break
########################################################################################################################
