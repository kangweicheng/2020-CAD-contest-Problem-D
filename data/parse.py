import pickle
import pandas as pd
import numpy as np
def pad(arr, constant_value):
        arr = np.array(arr)
        pad_length = 32
        if len(arr) < pad_length:
            arr = np.pad(arr, ((0, pad_length - len(arr))), 'constant', constant_values = constant_value)
        else:
            arr = arr[:pad_length]
        return arr
def loadFunction(func_Str, literal_index_List, index_literal_list):
	# print(func_Str)
	temp_literal =""
	function_represent = []
	for i in func_Str:
		if i.isdigit() or i.isalpha():
			temp_literal += i
		elif temp_literal != "":
			if temp_literal in literal_index_List.keys():
				function_represent .append((literal_index_List[temp_literal]))
				temp_literal = ""
			else:
				new_ind = len(literal_index_List)
				literal_index_List[temp_literal] = new_ind
				index_literal_list[new_ind] = temp_literal
				function_represent .append((literal_index_List[temp_literal]))
				temp_literal = ""
			if i in literal_index_List.keys():
				function_represent .append((literal_index_List[i]))
			else:
				new_ind = len(literal_index_List)
				literal_index_List[i] = new_ind
				index_literal_list[new_ind] = i
				function_represent .append((literal_index_List[i]))
		else: 
			if i in literal_index_List.keys():
				function_represent .append((literal_index_List[i]))
			else:
				new_ind = len(literal_index_List)
				literal_index_List[i] = new_ind
				index_literal_list[new_ind] = i
				function_represent .append((literal_index_List[i]))
		# print(literal_index_List, i)
	if temp_literal != "":
		if temp_literal in literal_index_List.keys():
			function_represent .append((literal_index_List[temp_literal]))
			temp_literal = ""
		else:
			new_ind = len(literal_index_List)
			literal_index_List[temp_literal] = new_ind
			index_literal_list[new_ind] = temp_literal
			function_represent .append((literal_index_List[temp_literal]))
			temp_literal = ""
	return pad(function_represent, 0), literal_index_List, index_literal_list
# 0 is negative
# 1 is positive
# 2 is dont care
# 3 is dont exist in the cell
def loadWhen(When_Str, literal_index_List, index_literal_list, inputs):
	
	whenLiteral = [3 for i in index_literal_list.keys()]
	for i in inputs:
		try:
			whenLiteral[literal_index_List[i]] = 2
		except:
			None
	if When_Str:
		When_Str = When_Str[1:-1].split('&')
		for i in When_Str:
			if i[0] == '!':
				literal = i[1:]
				whenLiteral[literal_index_List[literal]] = 0
			else :
				literal = i
				whenLiteral[literal_index_List[literal]] = 1
	
	return pad(whenLiteral, 0)



def parse(cells_list, timing_file, power_file, literal_index_List, index_literal_list):
	timing_index = 1
	power_index = 1
	timing = pd.DataFrame()
	power = pd.DataFrame()
	# timing = open(timing_file, 'w')
	# power = open(power_file, 'w')
	for c, cells in enumerate(cells_list):
		print('dealing with %d th cell list'%c)
		tmp_timing = []
		tmp_power = []
		for cell in cells:
			for timing_pair in cell['timing'].keys():
				inPin, outPin, when = timing_pair
				function = cell['output'][outPin]['function'][1:-1]
				functionLiteral, literal_index_List, index_literal_list = loadFunction(function, literal_index_List, index_literal_list)

				whenLiteral = loadWhen(when, literal_index_List, index_literal_list, cell['input'].keys())
				for Type in [(0, 'fall_transition'), (1, 'rise_transition'), (2, 'cell_fall'), (3, 'cell_rise')]:
					table = cell['timing'][timing_pair][Type[1]]
					timing_transition_index = cell['timing_transition_index']
					timing_capacitance_index = cell['timing_capacitance_index']
					for transition, row in zip(timing_transition_index, table):
						for capacitance, element in zip(timing_capacitance_index, row):
							if element > 0:
								try:
									tmp_timing.append([
											timing_index, element, Type[0], transition, capacitance,
											cell['process'], cell['voltage'], cell['temperature'],
											cell['input'][inPin]['rise_capacitance'], cell['input'][inPin]['fall_capacitance'],
											functionLiteral, whenLiteral,literal_index_List[inPin]
										])
									timing_index += 1
								except:
									None

			for power_pair in cell['internal_power'].keys():
				inPin, outPin, when = power_pair
				function = cell['output'][outPin]['function'][1:-1]
				functionLiteral, literal_index_List, index_literal_list = loadFunction(function, literal_index_List, index_literal_list)
				whenLiteral = loadWhen(when, literal_index_List, index_literal_list, cell['input'].keys())
				for Type in [(0, 'rise_power'), (1, 'fall_power')]:
					table = cell['internal_power'][power_pair][Type[1]]
					power_transition_index = cell['power_transition_index']
					power_capacitance_index = cell['power_capacitance_index']
					for transition, row in zip(power_transition_index, table):
						for capacitance, element in zip(power_capacitance_index, row):
							if element >1e-5:
								try:
									tmp_power.append([
											timing_index, element, Type[0], transition, capacitance,
											cell['process'], cell['voltage'], cell['temperature'],
											cell['input'][inPin]['rise_capacitance'], cell['input'][inPin]['fall_capacitance'],
											functionLiteral, whenLiteral,literal_index_List[inPin]
										])
									power_index += 1
								except:
									# print('Error')
									None
		print('writing timing to pd')
		new_timing = pd.DataFrame(tmp_timing, columns = [
				'id', 'ans', 'type', 'transition', 'capacitance', 'process',
				'voltage', 'temperature', 'rise_capcitance', 'fall_capacitance',
				'function', 'when', 'related_pin'
			])
		timing = timing.append(new_timing, ignore_index=True)
		print('writing power to pd')
		new_power = pd.DataFrame(tmp_power, columns = [
				'id', 'ans', 'type', 'transition', 'capacitance', 'process',
				'voltage', 'temperature', 'rise_capcitance', 'fall_capacitance',
				'function', 'when', 'related_pin'
			])
		power = power.append(new_power, ignore_index=True)

	# timing.to_csv(timing_file)
	# power.to_csv(power_file)

	print({
	    	'literal_index_List': literal_index_List,
	    	'index_literal_list': index_literal_list
	    	})
	with open('literal.pickle', 'wb') as f:
	    # Pickle the 'data' dictionary using the highest protocol available.
	    pickle.dump({
	    	'literal_index_List': literal_index_List,
	    	'index_literal_list': index_literal_list
	    	}, f, pickle.HIGHEST_PROTOCOL)

	with open(timing_file, 'wb+') as f:
		pickle.dump(timing, f)
	with open(power_file, 'wb+') as f:
		pickle.dump(power, f)
	return 0
