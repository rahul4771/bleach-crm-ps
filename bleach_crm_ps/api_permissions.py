from rest_framework import permissions



class CommonPermission(permissions.BasePermission):
	message='You are not an not authorized for this action.'
	def has_permission(self, request, view):
		if not request.user.is_authenticated:
			return False
		return self.check_perm(request,view)

	def check_perm(self, request, view):
		raise NotImplementedError('Not implemented')


class IsTeamInchargePermission(CommonPermission):
    def check_perm(self, request, view):
        if request.user.user_type=='TEAMINCHARGE':
            return True

class IsCustomerPermission(CommonPermission):
    def check_perm(self, request, view):
        if request.user.user_type=='CUSTOMER':
            return True