import re
def get_libs(path):
	keywords = ["library" ]
	cells = []
	library = dict()
	trace = []
	with open(path, 'r') as f:
		indent = 0
		lineid = 0
		while True:
			lineid += 1
			line = f.readline()
			if line:
				should_continue = re.match(r'\s*(.*) \\', line)
				if should_continue:
					line = should_continue.group(1)
					while True:
					    new_line = f.readline()
					    lineid += 1
					    should_continue = re.match(r'\s*(.*) \\', new_line)
					    if should_continue:
					        line += should_continue.group(1)
					    else:
					        line += new_line
					        break

				match_node = re.match(r'\s*(.*) \((.*)\) {\s*', line)
				match_value = re.match(r'\s*(.*) : (.*);\s*', line)
				match_array = re.match(r'\s*(.*) \((.*)\);\s*', line)
				match_end = re.match(r'\s*}', line)
				if match_array:
					array = re.sub(r'\s+', "", match_array.group(2))
					if array[0] == "\"" and array[-1] == "\"":
						array = array[1:-1]
						first = re.split(r'\",\"', array)
						value = [[] for i in first]
						for (c, i) in enumerate(first):
							row = i.split(',')
							new_row = []
							for element in row:

								try:
									new_row.append(float(element))
									# print('success', float(element))
								except:
									new_row.append(element)
							# print(new_row)
							value[c] = new_row
					else:
						value = array.split(',')
						new_row = []
						for element in value:
							try:
								new_row.append(float(element))
							except:
								new_row.append(element)
						value = new_row


					trace[-1][match_array.group(1)] = value

				elif match_node:
				    if match_node.group(1) == 'library':
				        trace = [library]
				    elif match_node.group(1) == 'cell':
				        cells.append(dict())
				        cells[-1]['name'] = match_node.group(2)
				        trace = [cells[-1]]
				    elif match_node.group(1) == 'pin':
				    	trace[-1][(match_node.group(1), match_node.group(2))] = dict()
				    	trace.append(trace[-1][(match_node.group(1), match_node.group(2))])
				    	trace[-1]['timing'] = []
				    	trace[-1]['internal_power'] = []
				    elif match_node.group(1) == 'timing':
				    	trace[-1]['timing'].append(dict())
				    	trace.append(trace[-1]['timing'][-1])
				    elif match_node.group(1) == 'internal_power':
				    	trace[-1]['internal_power'].append(dict())
				    	trace.append(trace[-1]['internal_power'][-1])
				    else:
				        trace[-1][(match_node.group(1), match_node.group(2))] = dict()
				        trace.append(trace[-1][(match_node.group(1), match_node.group(2))])
				elif match_value:
					value = match_value.group(2)
					# value = re.sub(r'\s+', "", value)
					# print(value)
					# value = re.sub(r'"', "", value)
					# print(value)
					try:
						value = (float(value))
					except:
						None
					trace[-1][match_value.group(1)] = value
				elif match_end:
				    trace = trace[:-1]
				else:
				    print(line)
				    print('error')

			else: 
			    # print(cells[0].keys())
			    break
	output_lib = dict()

	default_operating_conditions = library['default_operating_conditions']
	operating_conditions = library[('operating_conditions',default_operating_conditions)]
	output_lib['process'] = float(operating_conditions['process'])
	output_lib['temperature'] = float(operating_conditions['temperature'])
	output_lib['voltage'] = float(operating_conditions['voltage'])
	lu_table_template = library[('lu_table_template', 'delay_template_generic_7x7')]
	power_lut_template = library[('power_lut_template', 'power_template_generic_7x7')]
	output_lib['power_transition_index'] = power_lut_template['index_1'][0]
	output_lib['power_capacitance_index'] = power_lut_template['index_2'][0]
	output_lib['timing_transition_index'] = lu_table_template['index_1'][0]
	output_lib['timing_capacitance_index'] = lu_table_template['index_2'][0]



	output_cells = []
	for cell in cells:
		output_cells.append(dict())
		output_cells[-1]['name'] = cell['name']
		output_cells[-1]['area'] = cell['area']
		output_cells[-1]['output'] = dict()
		output_cells[-1]['input'] = dict()

		output_cells[-1]['timing'] = dict()
		output_cells[-1]['internal_power'] = dict()
		pin_name = filter(lambda x: x[0] == 'pin', cell.keys())


		output_cells[-1]['timing_transition_index'] = output_lib['timing_transition_index']
		output_cells[-1]['power_transition_index'] = output_lib['power_transition_index']
		output_cells[-1]['timing_capacitance_index'] = output_lib['timing_capacitance_index']
		output_cells[-1]['power_capacitance_index'] = output_lib['power_capacitance_index']
		output_cells[-1]['temperature'] = output_lib['temperature']
		output_cells[-1]['voltage'] = output_lib['voltage']
		c = 0
		wrong = False
		for pin in pin_name:
			pin_conf = cell[pin]
			if pin_conf['direction'] == '"output"':
				c += 1
				# print(pin_conf.keys())
				output_cells[-1]['output'][pin[1]] = pin_conf
				for timing in pin_conf['timing']:
					in_pin = re.sub(r'"', '', timing['related_pin'])
					when = timing.get('when')
					timing_table = dict()
					# print(timing.keys())
					try:

						timing_table['rise_transition'] = timing[('rise_transition',  'delay_template_generic_7x7')]['values']
						timing_table['fall_transition'] = timing[('fall_transition',  'delay_template_generic_7x7')]['values']
						timing_table['cell_rise'] = timing[('cell_rise',  'delay_template_generic_7x7')]['values']
						timing_table['cell_fall'] = timing[('cell_fall',  'delay_template_generic_7x7')]['values']
						output_cells[-1]['timing'][(in_pin, pin[1], when)] = timing_table
					except:
						print('wrong')
						wrong = True
				for internal_power in pin_conf['internal_power']:
					in_pin = re.sub(r'"', '', internal_power['related_pin'])
					when = internal_power.get('when')

					internal_power_table = dict()
					try:
						internal_power_table['rise_power'] = internal_power[('rise_power',  'power_template_generic_7x7')]['values']
						internal_power_table['fall_power'] = internal_power[('fall_power',  'power_template_generic_7x7')]['values']
						output_cells[-1]['internal_power'][(in_pin, pin[1], when)] = internal_power_table
					except:
						print('wrong')
						wrong = True
			elif pin_conf['direction'] == '"input"':
				output_cells[-1]['input'][pin[1]] = pin_conf
		if wrong:
			output_cells = output_cells[:-1]

	return output_lib, output_cells


# output_lib, output_cells = get_libs("lib1_ss0p72vm40c_base_400.tlib")
# print(output_lib['timing_transition_index'])
# print(output_lib['timing_capacitance_index'])
# print(output_lib['power_transition_index'])
# print(output_lib['power_capacitance_index'])
# print(output_lib['process'])
# print(output_lib['temperature'])
# print(output_lib['voltage'])

# print(output_cells[0]['name'])
# print(output_cells[0]['area'])
# print(output_cells[0]['input']['A'])
# print(output_cells[0]['input']['A']['max_transition'])
# print(output_cells[0]['input']['A']['capacitance'])
# print(output_cells[0]['input']['A']['rise_capacitance'])
# print(output_cells[0]['input']['A']['fall_capacitance'])
# print(output_cells[0]['input']['B'])
# print(output_cells[0]['output']['Z']['max_capacitance'])
# print(output_cells[0]['output']['Z']['function'])
# print(output_cells[0]['timing'][('A', 'Z')]['fall_transition'])
# print(output_cells[0]['timing'][('A', 'Z')]['rise_transition'])
# print(output_cells[0]['timing'][('A', 'Z')]['cell_fall'])
# print(output_cells[0]['timing'][('A', 'Z')]['cell_rise'])
# print(output_cells[0]['internal_power'][('A', 'Z')]['rise_power'])
# print(output_cells[0]['internal_power'][('A', 'Z')]['fall_power'])

