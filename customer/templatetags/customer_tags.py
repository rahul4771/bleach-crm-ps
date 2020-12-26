from django import template

register = template.Library()

@register.simple_tag
def get_month(month):
	if month == 1:
		return "January"
	elif month == 2:
		return "February"
	elif month == 3:
		return "March"
	elif month == 4:
		return "April"
	elif month == 5:
		return "May"
	elif month == 6:
		return "June"
	elif month == 7:
		return "July"
	elif month == 8:
		return "August"
	elif month == 9:
		return "Septemper"
	elif month == 10:
		return "October"
	elif month == 11:
		return "November"
	elif month == 12:	
		return "December"
	else:
		return "Unknown Month"