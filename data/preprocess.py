import read
# import evaluator
from parse import parse
import pickle
literal_index_List = {'pad': 0, '(': 1, ')': 2, '!': 3, '^': 4, '|': 5, '&': 6}
index_literal_list = {0: 'pad', 1: '(', 2:')', 3:'!', 4: '^', 5: '|', 6: '&'}
try:
	with open('./literal.pickle', 'rb') as f:
		liter_dict = pickle.load(f)
		literal_index_List = liter_dict['literal_index_List']
		index_literal_list = liter_dict['index_literal_list']
except:
	None
train_cells1 = read.get_libs("train/lib1_tt1p0v25c_base_400.tlib")
print('lib 1 is done')
train_cells2 = read.get_libs("train/lib1_ss0p9vm40c_base_400.tlib")
print('lib 2 is done')
train_cells3 = read.get_libs("train/lib1_ss0p9v125c_base_400.tlib")
print('lib 3 is done')
train_cells4 = read.get_libs("train/lib1_ff1p1vm40c_base_400.tlib")
print('lib 4 is done')
train_cells5 = read.get_libs("train/lib1_ff1p1v125c_base_400.tlib")
print('lib 5 is done')
# test_lib, test_cells = read.get_libs("./release/partial/lib1_ff0p88v125c_alpha_100.lib")
p = parse([train_cells1, train_cells2, train_cells3, train_cells4, train_cells5], 'train/timing.pkl', 'train/power.pkl', literal_index_List, index_literal_list)

test_cells1 = read.get_libs("test/lib1_ff0p99v125c_alpha_100.lib")
print('lib 1 is done')
test_cells2 = read.get_libs("test/lib1_ff0p99vm40c_alpha_100.lib")
print('lib 2 is done')
test_cells3 = read.get_libs("test/lib1_ss0p81v125c_alpha_100.lib")
print('lib 3 is done')
test_cells4 = read.get_libs("test/lib1_ss0p81vm40c_alpha_100.lib")
print('lib 4 is done')
test_cells5 = read.get_libs("test/lib1_tt0p9v25c_alpha_100.lib")
print('lib 5 is done')
# test_lib, test_cells = read.get_libs("./release/partial/lib1_ff0p88v125c_alpha_100.lib")
p = parse([test_cells1, test_cells2, test_cells3, test_cells4, test_cells5], 'test/timing.pkl', 'test/power.pkl', literal_index_List, index_literal_list)

# print(evaluator.evaluator(train_cells, train_cells))