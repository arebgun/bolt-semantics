from myrandom import nprandom as random

def categorical_sample(prob_array):
	return prob_array.cumsum().searchsorted( random.sample(1) )[0]

def index_max(prob_array):
	return max(enumerate(prob_array), key=lambda x:x[1])[0]