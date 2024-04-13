from django.contrib import admin
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin
from import_export.resources import ModelResource
from admin_panel.models import User, Museum, Exhibit, Report, Dispatcher, Post


class CustomImportExport(ImportExportModelAdmin, ExportActionModelAdmin):
    pass


# setup export
class UserResource(ModelResource):
    class Meta:
        model = User
        fields = ['id', 'museum__name', 'fio', 'phone', 'email', 'link', 'user_id', 'username', 'status', 'created_at']
        export_order = ['id', 'museum__name', 'fio', 'phone', 'email', 'link', 'user_id', 'username', 'status',
                        'created_at']
        import_id_fields = ('id',)


class ReportResource(ModelResource):
    class Meta:
        model = Report
        fields = ['id', 'status', 'description', 'exhibit__name', 'museum__name', 'creator__fio', 'created_at']
        export_order = ['id', 'status', 'description', 'exhibit__name', 'museum__name', 'creator__fio', 'created_at']


@admin.register(User)
class UserAdmin(CustomImportExport):
    resource_classes = [UserResource]
    list_display = ('id', 'museum', 'fio', 'phone', 'email', 'link', 'user_id', 'is_reports_receiver', 'created_at')
    list_display_links = ('id', 'user_id')
    list_editable = ('museum', 'fio', 'phone', 'email', 'is_reports_receiver')
    list_filter = ('museum',)


@admin.register(Museum)
class MuseumAdmin(CustomImportExport):
    list_display = [field.name for field in Museum._meta.fields]
    list_editable = ('name',)


@admin.register(Exhibit)
class ExhibitAdmin(CustomImportExport):
    list_display = [field.name for field in Exhibit._meta.fields]
    list_editable = [field.name for field in Exhibit._meta.fields if field.name != 'id']
    list_filter = ('museum',)


@admin.register(Report)
class ReportAdmin(CustomImportExport):
    resource_classes = [ReportResource]
    list_display = [field.name for field in Report._meta.fields]
    list_filter = ('status', 'museum', 'creator', 'created_at')


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
