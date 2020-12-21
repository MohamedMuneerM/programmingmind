from django.contrib import admin
from django.db import models
from .models import(
	TutorialSeries,
	Tutorial,
	BlogPost,
	BlogCategory,
	Profile,
	Comment,
	Suggetions,
	AboutPage,
	Topic,
	NewsLetter,
	User_Agreements,
	Notification_Manual,
	Connect,
)
from tinymce.widgets import TinyMCE
from django.contrib.auth.admin import UserAdmin
from .models import Account,Profile



class AboutPageAdmin(admin.ModelAdmin):
	formfield_overrides = {
		models.TextField: {'widget': TinyMCE()},
	}


class TutorialInline(admin.StackedInline):
	model = Tutorial
	formfield_overrides = {
		models.TextField: {'widget': TinyMCE()},
	}



class TutorialSeriesAdmin(admin.ModelAdmin):
	formfield_overrides = {
		models.TextField: {'widget': TinyMCE()},
	}
	inlines = [TutorialInline]

class TutorialAdmin(admin.ModelAdmin):
	formfield_overrides = {
		models.TextField: {'widget': TinyMCE()},
	}




class BlogPostAdmin(admin.ModelAdmin):

	formfield_overrides = {
		models.TextField: {'widget': TinyMCE()},
	}
	


class AccountAdmin(UserAdmin):
	list_display = ('email','username','date_joined', 'last_login', 'is_admin','is_staff')
	search_fields = ('email','username',)

	filter_horizontal = ()
	list_filter = ()
	fieldsets = ()

class CommentAdmin(admin.ModelAdmin):
	list_display = ('id',)



admin.site.register(TutorialSeries,TutorialSeriesAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Tutorial,TutorialAdmin)
admin.site.register(BlogPost,BlogPostAdmin)
admin.site.register(BlogCategory)
admin.site.register(Comment,CommentAdmin)
admin.site.register(AboutPage, AboutPageAdmin)
admin.site.register(Suggetions)
admin.site.register(Topic)

admin.site.register(NewsLetter)
admin.site.register(User_Agreements)
admin.site.register(Notification_Manual)
admin.site.register(Connect)