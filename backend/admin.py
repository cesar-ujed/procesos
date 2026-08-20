from django.contrib import admin
from backend.models import *


# Profile detallado
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user','user_group')
    search_fields = ('user_username', 'usergroups_name')
    list_filter = ('user__groups',)

    def user_group(self, obj):
        return " - ".join([t.name for t in obj.user.groups.all().order_by('name')])

    user_group.short_description = 'Grupo'

admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Proceso)
admin.site.register(Actividad)
admin.site.register(Evidencia)
admin.site.register(FeedbackEvidencia)