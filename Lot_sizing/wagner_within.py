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

	if n == 0 or sum(demands) == 0:
		return [0]*n, [0]*n, 0.0
	cumsum = compute_cumsum(demands)

	F = [float('inf')] * (n + 1)
	F[0] = 0
	prev = [-1] * (n + 1)
	for i in range(1, n + 1):
		for j in range(1, i + 1):
			holding = 0
			for k in range(j, i):
				holding += sum_between(cumsum, k, i - 1) * holding_cost_per_unit
			cost = F[j - 1] + setup_cost + holding
			if cost < F[i]:
				F[i] = cost
				prev[i] = j - 1

	production_plan = [0] * n
	inventory = initial_inventory
	inventory_levels = [0] * n

	i = n
	while i > 0:
		j = prev[i]
		production_plan[j] = sum_between(cumsum, j, i - 1)
		i = j

	for t in range(n):
		inventory += production_plan[t]
		inventory -= demands[t]
		inventory_levels[t] = inventory

	return production_plan, inventory_levels, F[n]
