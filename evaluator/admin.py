from django.contrib import admin
from evaluator.models import ServiceType,LocationType,CleaningType,CleaningMethod,AreaType,CleaningSection,Evaluation,EvaluationDetails,EvaluationMedia,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote
# Register your models here.

admin.site.register(ServiceType)
admin.site.register(LocationType)
admin.site.register(CleaningType)
admin.site.register(CleaningMethod)
admin.site.register(AreaType)
admin.site.register(CleaningSection)
admin.site.register(Evaluation)


class EvaluationMediaInline(admin.TabularInline):
    model = EvaluationMedia
    extra = 1

class EvaluationBookInline(admin.TabularInline):
	model = EvaluationBook
	extra = 1   





class EvaluationMediaAdmin(admin.ModelAdmin):
	radio_fields = {"media_type":admin.HORIZONTAL,"taken_status":admin.HORIZONTAL}

class EvaluationBookAdmin(admin.ModelAdmin):
	inlines = (EvaluationMediaInline,)

class EvaluationDetailsAdmin(admin.ModelAdmin):
	inlines = (EvaluationBookInline,)

admin.site.register(EvaluationDetails,EvaluationDetailsAdmin)
admin.site.register(EvaluationMedia,EvaluationMediaAdmin)
admin.site.register(EvaluationBook,EvaluationBookAdmin)
admin.site.register(EvaluationBookSection)
admin.site.register(EvaluationSectionKeynote)
#Django Panel Customisation
admin.site.site_header = "Bleach Kuwait"