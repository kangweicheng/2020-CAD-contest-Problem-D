def evaluator(predicts, truths):
	score_sum = 0.0
	score_num = 0
	for predict, truth in zip(predicts, truths):

		for info in truth['timing'].keys():
			if predict['timing'].get(info):
				for matrix_type in ['cell_rise', 'cell_fall', 'rise_transition', 'fall_transition']:
					predict_matrix = predict['timing'][info][matrix_type]
					truth_matrix = truth['timing'][info][matrix_type]
					for (predict_row, truth_row) in zip(predict_matrix, truth_matrix):
						for(predict_value, truth_value) in zip(predict_row, truth_row):
							score_sum += min(1, abs(predict_value - truth_value)/truth_value) ** 2
							score_num += 1
			else:
				raise 'missing timing'
	for info in truth['internal_power'].keys():
			if predict['internal_power'].get(info):
				for matrix_type in ['rise_power', 'fall_power']:
					predict_matrix = predict['internal_power'][info][matrix_type]
					truth_matrix = truth['internal_power'][info][matrix_type]
					for (predict_row, truth_row) in zip(predict_matrix, truth_matrix):
						for(predict_value, truth_value) in zip(predict_row, truth_row):
							score_sum += min(1, abs(predict_value - truth_value)/truth_value) ** 2
							score_num += 1
			else:
				raise 'missing internal_power'
	score = 100 - 100 * (score_sum/score_num) ** (1/2)
	return score
