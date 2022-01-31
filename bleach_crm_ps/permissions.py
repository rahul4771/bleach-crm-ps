from django.contrib.auth.mixins import UserPassesTestMixin

class IsAdmin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='ADMIN' and self.request.user.is_active==True:
            return True       
        else:
            return False   

class IsAgent(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='AGENT' and self.request.user.is_active==True:
            return True
        else:
            return False           
                
class IsEvaluator(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='EVALUATOR' and self.request.user.is_active==True:
            return True
        else:
            return False                   

class IsSeniorTeamLeader(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='SENIORTEAMLEADER' and self.request.user.is_active==True:
            return True
        else:
            return False

class IsOperationSupervisor(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='OPERATIONSUPERVISOR' and self.request.user.is_active==True:
            return True
        else:
            return False

class IsTechnicalSupervisor(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='TECHNICALSUPERVISOR' and self.request.user.is_active==True:
            return True
        else:
            return False

class IsTeamLeader(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='TEAMINCHARGE' and self.request.user.is_active==True:
            return True
        else:
            return False            

class IsAccountant(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='ACCOUNTANT' and self.request.user.is_active==True:
            return True
        else:
            return False

class IsQualityControll(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='QUALITYCONTROLL' and self.request.user.is_active==True:
            return True
        else:
            return False

class IsSalesAdmin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='SALESADMIN' and self.request.user.is_active==True:
            return True
        else:
            return False

class IsBookingOfficer(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='BOOKINGOFFICER' and self.request.user.is_active==True:
            return True
        else:
            return False

class IsInventoryAdmin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='INVENTORYADMIN' and self.request.user.is_active==True:
            return True
        else:
            return False

class IsInventoryAdminUser(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='INVENTORYADMIN' and self.request.user.is_active==True:
            return True
        if self.request.user.is_authenticated and self.request.user.user_type=='INVENTORYUSER' and self.request.user.is_active==True:
            return True
        if self.request.user.is_authenticated and self.request.user.user_type=='STOCKCONTROLLER' and self.request.user.is_active==True:
            return True
        if self.request.user.is_authenticated and self.request.user.user_type=='PURCHASINGOFFICER' and self.request.user.is_active==True:
            return True
        else:
            return False

class IsAgentEvaluatorSalesAdmin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.user_type=='SALESADMIN' and self.request.user.is_active==True:
            return True
        elif self.request.user.is_authenticated and self.request.user.user_type=='AGENT' and self.request.user.is_active==True:
            return True
        elif self.request.user.is_authenticated and self.request.user.user_type=='EVALUATOR' and self.request.user.is_active==True:
            return True
        else:
            return False    

class IsAuthenticated(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.is_active==True:
            return True
        else:
            return False