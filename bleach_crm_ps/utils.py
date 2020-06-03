def get_error(form):
	errors=dict(form.errors)
	key=tuple(errors.keys())[0]
	error=errors[key]
	key=key.replace('__all__','')
	if isinstance(error,(tuple,list)):
		return key +' : '+error[0]
	tkey=tuple(error.keys())[0]
	tkey=tkey.replace('__all__','')
	message=key +' : '+ error[tkey][0]
	return message 