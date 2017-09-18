from django.contrib import admin
from apps.core.models import Profile, Company, Skills
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Perfis"
    verbose_name = "Perfil"
    fk_name = "usuario"

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Company) # , CompanyAdmin)
admin.site.register(Skills) # , CompanyAdmin)
