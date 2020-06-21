def parse(cells_list, timing_file, power_file):
	timing_index = 1
	power_index = 1
	timing = open(timing_file, 'w')
	power = open(power_file, 'w')
	for cells in cells_list:
		for cell in cells:
			for timing_pair in cell['timing'].keys():
				inPin, outPin, when = timing_pair
				for Type in [(0, 'fall_transition'), (1, 'rise_transition'), (2, 'cell_fall'), (3, 'cell_rise')]:
					table = cell['timing'][timing_pair][Type[1]]
					timing_transition_index = cell['timing_transition_index']
					timing_capacitance_index = cell['timing_capacitance_index']
					for transition, row in zip(timing_transition_index, table):
						for capacitance, element in zip(timing_capacitance_index, row):
							timing.write('%d,%f,%d,%f,%f,%d,%f,%d,%f,%f\n'% (
									timing_index, element, Type[0], transition, capacitance,
									cell['process'], cell['voltage'], cell['temperature'],
									cell['input'][inPin]['rise_capacitance'], cell['input'][inPin]['fall_capacitance']
								))
							timing_index += 1
			for power_pair in cell['internal_power'].keys():
				inPin, outPin, when = power_pair
				for Type in [(0, 'rise_power'), (1, 'fall_power')]:
					table = cell['internal_power'][power_pair][Type[1]]
					power_transition_index = cell['power_transition_index']
					power_capacitance_index = cell['power_capacitance_index']
					for transition, row in zip(power_transition_index, table):
						for capacitance, element in zip(power_capacitance_index, row):
							power.write('%d,%f,%d,%f,%f,%d,%f,%d,%f,%f\n'% (
									power_index, element, Type[0], transition, capacitance,
									cell['process'], cell['voltage'], cell['temperature'],
									cell['input'][inPin]['rise_capacitance'], cell['input'][inPin]['fall_capacitance']
								))
							power_index += 1


	return 0
