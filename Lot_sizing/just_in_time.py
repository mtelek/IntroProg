# CALCULATING JUST IN TIME PRODUCTION METHOD
def jit_heuristic(demand, setup_cost, holding_cost, initial_inventory=0):
	n = len(demand)
	production_plan = [0] * n
	inventory_levels = [0] * n
	
	inventory = initial_inventory
	total_setup_cost = 0
	total_holding_cost = 0
	
	for i in range(n):
		if demand[i] > 0:
			# ALWAYS PRODUCE JIT
			production_qty = max(0, demand[i] - inventory)
			production_plan[i] = production_qty
			# UPDATE INVENTORY
			inventory = inventory + production_qty - demand[i]
			inventory_levels[i] = inventory
			# CALCULATE COSTS
			if production_qty > 0:
				total_setup_cost += setup_cost
			if inventory > 0:
				total_holding_cost += inventory * holding_cost
		else:
			inventory_levels[i] = inventory
	
	total_cost = total_setup_cost + total_holding_cost
	return production_plan, inventory_levels, total_cost
