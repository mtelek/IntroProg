import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def visualize_lot_sizing(periods, demand, ww_plan, ww_inventory, jit_plan, jit_inventory):
	fig, ax1 = plt.subplots(figsize=(10,5))

	# SETTING PRODUCTION PLANS AS BARS
	width = 0.35
	ax1.bar([p - width/2 for p in periods], ww_plan, width, label='WW Production', color='skyblue')
	ax1.bar([p + width/2 for p in periods], jit_plan, width, label='JIT Production', color='orange')
	ax1.set_xlabel('Period')
	ax1.set_ylabel('Production units')
	ax1.legend(loc='upper left')

	# SETTING INVENTORY LEVELS AS LINES
	ax2 = ax1.twinx()
	ax2.plot(periods, ww_inventory, label='WW Inventory', color='blue', marker='o')
	ax2.plot(periods, jit_inventory, label='JIT Inventory', color='red', marker='x')
	ax2.set_ylabel('Inventory units')
	ax2.legend(loc='upper right')

	plt.title('Lot Sizing: Production & Inventory')
 
	# SAVING THE FILE
	root_dir = Path(__file__).resolve().parent.parent
	results_dir = root_dir / "Results"
	results_dir.mkdir(exist_ok=True)  # MAKE FOLDER IF DOESNT EXIST

	timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
	plt.savefig(results_dir / f"lot_sizing_plot_{timestamp}.png")
