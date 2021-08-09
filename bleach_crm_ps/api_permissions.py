from rest_framework import permissions

class IsTeamInchargePermission(permissions.BasePermission):
    def check_perm(self, request, view):
        if request.user.user_type=='TEAMINCHARGE':
            return True