from django.contrib import admin
from evaluator.models import ServiceType,LocationType,CleaningType,CleaningMethod,Evaluation,EvaluationDetails,EvaluationMedia
# Register your models here.

admin.site.register(ServiceType)
admin.site.register(LocationType)
admin.site.register(CleaningType)
admin.site.register(CleaningMethod)
admin.site.register(Evaluation)


class EvaluationMediaInline(admin.TabularInline):
    model = EvaluationMedia
    extra = 1

class EvaluationDetailsAdmin(admin.ModelAdmin):
	inlines = (EvaluationMediaInline,)
	radio_fields = {"service_type":admin.VERTICAL,"location_type":admin.VERTICAL,"cleaning_type":admin.VERTICAL,
					"bed_type":admin.HORIZONTAL,"sanitization_type":admin.HORIZONTAL,"set_type":admin.HORIZONTAL,"fabric_type":admin.HORIZONTAL}

class EvaluationMediaAdmin(admin.ModelAdmin):
	radio_fields = {"media_type":admin.HORIZONTAL,"taken_status":admin.HORIZONTAL}

admin.site.register(EvaluationDetails,EvaluationDetailsAdmin)
admin.site.register(EvaluationMedia,EvaluationMediaAdmin)