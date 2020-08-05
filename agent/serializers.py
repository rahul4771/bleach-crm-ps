from django.core import serializers

from user.models import UserProfile,Address,Governorate,Area
from evaluator.models import Evaluation,EvaluationDetails,EvaluationBook,EvaluationMedia,CleaningMethod,ServiceType
from order.models import OrderScheduler,FollowUpScheduler,FeedBack,Order,Investigation,InvestigationMedia,FollowUp,Question
from senior_team_leader.models import CleaningTeam,FollowUpTeam,CleaningTeamMember,FollowUpTeamMember,CleaningTeamMedia
from accountant.models import PaymentHistory 

class EvaluationDetailsSerializer(serializers.ModelSerializer):
    address      =  ProductsSerializer(read_only=True)      

    class Meta:      
        model    = EvaluationDetails   
        fields   = ('address',)  
        

class AddressSerializer(serializers.ModelSerializer): 
    governorate     = GovernorateSerializer(read_only=True)
    area            = AreaSerializer(read_only=True)
    class Meta: 
        model  = Address 
        fields = ('governorate','area','block','avenue','building','street','floor','apartment',)  

class GovernorateSerializer(serializers.ModelSerializer):
    class Meta:      
        model = Governorate   
        fields = ('name',)  

class AreaSerializer(serializers.ModelSerializer):
    class Meta:      
        model = Area   
        fields = ('name',)  
