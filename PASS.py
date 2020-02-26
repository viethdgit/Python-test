import random, string

#len_pass=input('Password lenght? ')
#pass_power=raw_input('Contains symbols? Yes ')
def GENERATOR(len_pass,pass_power):
	list_int_all = range(33,127)
	list_int_all.remove(34); list_int_all.remove(39)
	list_int= string.letters+'0123456789'
	pass_gen=''

	for i in range(len_pass):
		if (pass_power in ['y','yes','Y','Yes','YES', '1',1]):
			pass_gen=pass_gen+chr(random.choice(list_int_all))
		else:
			pass_gen=pass_gen+random.choice(string.letters)
	#print pass_gen
	return pass_gen
