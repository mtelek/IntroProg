# COMPUTE CUMULATIVE SUMS
def compute_cumsum(array):
	n = len(array)
	cumsum = [0] * (n + 1)
	for i in range(n):
		cumsum[i + 1] = cumsum[i] + array[i]
	return cumsum

# CALCULATING SUM BETWEEN i AND j
def sum_between(cumsum, i, j):
	return cumsum[j + 1] - cumsum[i]

# WAGNER-WITHIN ALGORITHM
def wagner_whitin_algorithm(demands, setup_cost, holding_cost_per_unit, initial_inventory=0):
	n = len(demands)

	#IF NO DEMAND RETURN FROM THE FUNCTION
	if n == 0 or sum(demands) == 0:
		return [0]*n, [0]*n, 0.0
	cumsum = compute_cumsum(demands) #PRECOMPUTE CUMULLATIVE SUM FOR DEMAND

	F = [float('inf')] * (n + 1) #CREATING AN N+1 LONG COST LIST WITH INFINITIES
	F[0] = 0
	prev = [-1] * (n + 1) #STORES IN WHICH PERIOD THE LAST PRODUCTION WAS MADE
	for i in range(1, n + 1):
		for j in range(1, i + 1):
			holding = 0
			# CALCULATE HOLDING COST FOR INVENTORY CARRIED
			for k in range(j, i):
				# INVENTORY HELD FROM PERIOD k TO i-1
				holding += sum_between(cumsum, k, i - 1) * holding_cost_per_unit
			# TOTAL COST = PREVIOUS COST + SETUP COST + HOLDING COST
			cost = F[j - 1] + setup_cost + holding
			# KEEP THE CHEAPEST OPTION
			if cost < F[i]:
				F[i] = cost
				prev[i] = j - 1

	# INITIALIZE OUTPUT STRUCTURES
	production_plan = [0] * n
	inventory = initial_inventory
	inventory_levels = [0] * n

	# BACKTRACKING TO FIND THE OPTIMAL PRODUCTION PLAN
	i = n
	while i > 0:
		j = prev[i] # LAST PRODUCTION PERIOD
		# PRODUCE ENOUGH TO COVER DEMAND FROM j TO i-1
		production_plan[j] = sum_between(cumsum, j, i - 1)
		i = j # MOVE BACKWARD

	# COMPUTE INVENTORY LEVELS PERIOD BY PERIOD
	for t in range(n):
		inventory += production_plan[t]  # ADD PRODUCTION
		inventory -= demands[t]	# SUBTRACT DEMAND
		inventory_levels[t] = inventory # STORE INVENTORY LEVEL

	return production_plan, inventory_levels, F[n]
