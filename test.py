import read
import evaluator
train_lib, train_cells = read.get_libs("lib1_tt1p0v25c_base_400.tlib")
# test_lib, test_cells = read.get_libs("./release/partial/lib1_ff0p88v125c_alpha_100.lib")

def get_functions(cells):
	functions = set()
	for cell in cells:
		outputs = cell['output'].keys()
		for output in outputs:
			functions.add(cell['output'][output]['function'])
	return functions

print(evaluator.evaluator(train_cells, train_cells))