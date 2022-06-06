from django.contrib import admin
from django.contrib.sessions.models import Session
from evaluator.models import ServiceType,LocationType,CleaningType,CleaningMethod,AreaType,CleaningSection,Evaluation,EvaluationDetails,EvaluationMedia,EvaluationBook,EvaluationBookSection,EvaluationSectionKeynote,EvaluationSectionAddons
# Register your models here.

admin.site.register(ServiceType)
admin.site.register(LocationType)
admin.site.register(CleaningType)
admin.site.register(CleaningMethod)
admin.site.register(AreaType)
admin.site.register(CleaningSection)
admin.site.register(Session)


class EvaluationAdmin(admin.ModelAdmin):
	search_fields =['evaluation_id']
admin.site.register(Evaluation,EvaluationAdmin)

   

class EvaluationMediaAdmin(admin.ModelAdmin):
	radio_fields = {"media_type":admin.HORIZONTAL,"taken_status":admin.HORIZONTAL}
admin.site.register(EvaluationMedia,EvaluationMediaAdmin)



class EvaluationMediaInline(admin.TabularInline):
    model = EvaluationMedia
    extra = 1
class EvaluationBookAdmin(admin.ModelAdmin):
	inlines = (EvaluationMediaInline,)
	search_fields =['evaluation_details__evaluation__evaluation_id']
admin.site.register(EvaluationBook,EvaluationBookAdmin)



class EvaluationBookInline(admin.TabularInline):
	model = EvaluationBook
	extra = 1
class EvaluationDetailsAdmin(admin.ModelAdmin):
	inlines = (EvaluationBookInline,)
	search_fields       =['evaluation__evaluation_id']
admin.site.register(EvaluationDetails,EvaluationDetailsAdmin)



class EvaluationBookSectionAdmin(admin.ModelAdmin):
	search_fields =['evaluation_book__evaluation_details__evaluation__evaluation_id']
admin.site.register(EvaluationBookSection,EvaluationBookSectionAdmin)



class EvaluationSectionKeynoteAdmin(admin.ModelAdmin):
	search_fields =['evaluation_section__evaluation_book__evaluation_details__evaluation__evaluation_id']
admin.site.register(EvaluationSectionKeynote,EvaluationSectionKeynoteAdmin)

class EvaluationSectionAddonsAdmin(admin.ModelAdmin):
	search_fields =['evaluation_section__evaluation_book__evaluation_details__evaluation__evaluation_id']
admin.site.register(EvaluationSectionAddons,EvaluationSectionAddonsAdmin)



#Django Panel Customisation
admin.site.site_header = "Bleach Kuwait"