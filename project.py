import sys
from Lot_sizing import lot_sizing as ls
from Master_production_schedule import mps
from Travelling_salesmen_problem import tsp

# USED FOR COLORING OUTPUT MESSAGES
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

def display_menu():
    # DISPLAYING MAIN MENU
	print(f"\n{BLUE}{'='*80}{RESET}")
	print(f"{BLUE}{BOLD}{' '*38}MENU{RESET}")
	print(f"{BLUE}{'='*80}{RESET}")
	print("1. Master Production Schedule(MPS)")
	print("2. Lot Sizing")
	print("3. Travelling Salesmen Problem(TSP)")
	print("4. Exit")

def main():
	signal = True
	while True:
		if (signal == True):
			display_menu()
		signal = True
  
		try:
			choice = input("\nEnter your choice (1-4): ").strip()

			if choice == '1':
				mps.run_mps()
			elif choice == '2':
				ls.main()
			elif choice == '3':
				tsp.run_tsp()
			elif choice == '4':
				print("Program closing...")
				sys.exit(0)
			else:
				print("Invalid choice. Please try again.", end="")
				signal = False
		except EOFError: # WHEN PRESSING Ctrl+D
			signal = False
			continue
		except KeyboardInterrupt: # WHEN PRESSING Ctrl+C
			print("\n\nProgram interrupted. Closing program...")
			sys.exit(0)
		except Exception as e: # WHEN HAVING ERRORS
			print(f"An error occurred: {e}")

if __name__ == "__main__":
	main()
