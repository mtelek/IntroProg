import sys
import mps
import lot_sizing
import tsp

def display_menu():
	print("\n=== MENU ===")
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
			choice = input("\nEnter your choice (1-4): ")

			if choice == '1':
				mps.run_mps()
			elif choice == '2':
				lot_sizing.run_lot_sizing()
			elif choice == '3':
				tsp.run_tsp()
			elif choice == '4':
				print("Program Closed")
				sys.exit(0)
			else:
				print("Invalid choice. Please try again.")
		except EOFError: #For pressing Ctrl+D
			signal = False
			continue
		except KeyboardInterrupt: #For pressing Ctrl+C
			print("\n\nProgram interrupted. Closing program")
			sys.exit(0)
		except Exception as e: #For errors
			print(f"An error occurred: {e}")

if __name__ == "__main__":
	main()
