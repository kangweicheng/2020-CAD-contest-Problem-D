import read

train_lib, train_cells = read.get_libs("lib1_ss0p72vm40c_base_400.tlib")
test_lib, test_cells = read.get_libs("./release/partial/lib1_ff0p88v125c_alpha_100.lib")

def get_functions(cells):
	functions = set()
	for cell in cells:
		outputs = cell['output'].keys()
		for output in outputs:
			functions.add(cell['output'][output]['function'])
	return functions

train_function = get_functions(train_cells)
test_function = get_functions(test_cells)
print(train_function)
print(test_function)
print(test_function - train_function)