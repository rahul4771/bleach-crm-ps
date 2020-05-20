from django.contrib import admin
from evaluator.models import ServiceType,LocationType,CleaningType,CleaningMethod,Evaluation,EvaluationDetails,EvaluationMedia,EvaluationBook
# Register your models here.

admin.site.register(ServiceType)
admin.site.register(LocationType)
admin.site.register(CleaningType)
admin.site.register(CleaningMethod)
admin.site.register(Evaluation)


class EvaluationMediaInline(admin.TabularInline):
    model = EvaluationMedia
    extra = 1

class EvaluationBookInline(admin.TabularInline):
	model = EvaluationBook
	extra = 1   

class EvaluationDetailsAdmin(admin.ModelAdmin):
	inlines = (EvaluationMediaInline,EvaluationBookInline)
	radio_fields = {"service_type":admin.VERTICAL,}

class EvaluationMediaAdmin(admin.ModelAdmin):
	radio_fields = {"media_type":admin.HORIZONTAL,"taken_status":admin.HORIZONTAL}

admin.site.register(EvaluationDetails,EvaluationDetailsAdmin)
admin.site.register(EvaluationMedia,EvaluationMediaAdmin)
admin.site.register(EvaluationBook)

#Django Panel Customisation
admin.site.site_header = "Bleach Kuwait"