import read
import evaluator
from parse import parse

train_cells1 = read.get_libs("lib1_tt1p0v25c_base_400.tlib")
print('lib 1 is done')
train_cells2 = read.get_libs("lib1_ss0p9vm40c_base_400.tlib")
print('lib 2 is done')
train_cells3 = read.get_libs("lib1_ss0p9v125c_base_400.tlib")
print('lib 3 is done')
train_cells4 = read.get_libs("lib1_ff1p1vm40c_base_400.tlib")
print('lib 4 is done')
train_cells5 = read.get_libs("lib1_ff1p1v125c_base_400.tlib")
print('lib 5 is done')
# test_lib, test_cells = read.get_libs("./release/partial/lib1_ff0p88v125c_alpha_100.lib")
p = parse([train_cells1, train_cells2,train_cells3,train_cells4,train_cells5], './timing.csv', './power.csv')

# print(evaluator.evaluator(train_cells, train_cells))