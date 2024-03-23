from django.contrib import admin
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin
from import_export.resources import ModelResource
from admin_panel.models import User, Museum, Exhibit, Report, Dispatcher, Post


class CustomImportExport(ImportExportModelAdmin, ExportActionModelAdmin):
    pass


# setup import
class UserResource(ModelResource):
    class Meta:
        model = User
        import_id_fields = ('id',)


@admin.register(User)
class UserAdmin(CustomImportExport):
    resource_classes = [UserResource]
    list_display = ('id', 'museum', 'fio', 'phone', 'email', 'link', 'user_id', 'created_at')
    list_display_links = ('id', 'user_id')
    list_editable = ('museum', 'fio', 'phone', 'email')


@admin.register(Museum)
class MuseumAdmin(CustomImportExport):
    list_display = [field.name for field in Museum._meta.fields]
    list_editable = ('name',)


@admin.register(Exhibit)
class ExhibitAdmin(CustomImportExport):
    list_display = [field.name for field in Exhibit._meta.fields]
    list_editable = [field.name for field in Exhibit._meta.fields if field.name != 'id']


@admin.register(Report)
class ReportAdmin(CustomImportExport):
    list_display = [field.name for field in Report._meta.fields]


@admin.register(Dispatcher)
class DispatcherAdmin(CustomImportExport):
    list_display = [field.name for field in Dispatcher._meta.fields]


@admin.register(Post)
class PostAdmin(CustomImportExport):
    list_display = [field.name for field in Post._meta.fields]
    list_editable = [field.name for field in Post._meta.fields if field.name != 'id' and field.name != 'created_at']


# sort models from admin.py by their registering (not alphabetically)
def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    app_list = list(app_dict.values())
    return app_list


admin.AdminSite.get_app_list = get_app_list
