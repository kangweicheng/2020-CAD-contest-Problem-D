import pickle
def loadFunction(func_Str, literal_index_List, index_literal_list):
	temp_literal =""
	function_represent = []
	for i in func_Str:
		if i.isdigit() or i.isalpha():
			temp_literal += i
		elif temp_literal != "":
			if temp_literal in literal_index_List.keys():
				function_represent .append(str(literal_index_List[temp_literal]))
				temp_literal = ""
			else:
				literal_index_List[temp_literal] = len(literal_index_List)
				index_literal_list[len(literal_index_List)] = temp_literal
				function_represent .append(str(literal_index_List[temp_literal]))
				temp_literal = ""
		else: 
			if i in literal_index_List.keys():
				function_represent .append(str(literal_index_List[i]))
			else:
				literal_index_List[i] = len(literal_index_List)
				index_literal_list[len(literal_index_List)] = i
				function_represent .append(str(literal_index_List[i]))
	function_represent = ('"%s"'%','.join(function_represent))
	return function_represent, literal_index_List, index_literal_list
# 0 is negative
# 1 is positive
# 2 is dont care
# 3 is dont exist in the cell
def loadWhen(When_Str, literal_index_List, index_literal_list, inputs):
	print(When_Str)
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
	
	return ('"%s"'%','.join([str(i) for i in whenLiteral]))



def parse(cells_list, timing_file, power_file, literal_index_List, index_literal_list):
	timing_index = 1
	power_index = 1
	timing = open(timing_file, 'w')
	power = open(power_file, 'w')
	for cells in cells_list:
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
							timing.write('%d,%f,%d,%f,%f,%d,%f,%d,%f,%f,%s,%s\n'% (
									timing_index, element, Type[0], transition, capacitance,
									cell['process'], cell['voltage'], cell['temperature'],
									cell['input'][inPin]['rise_capacitance'], cell['input'][inPin]['fall_capacitance'], functionLiteral, whenLiteral
								))
							timing_index += 1
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
							power.write('%d,%f,%d,%f,%f,%d,%f,%d,%f,%f,%s,%s\n'% (
									power_index, element, Type[0], transition, capacitance,
									cell['process'], cell['voltage'], cell['temperature'],
									cell['input'][inPin]['rise_capacitance'], cell['input'][inPin]['fall_capacitance'], functionLiteral, whenLiteral
								))
							power_index += 1
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

	return 0
