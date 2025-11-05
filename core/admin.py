from django.contrib import admin

from .models import Post, Profile, SustainabilityInterests, TradingInterests

admin.site.register(Profile)
admin.site.register(Post)

# Each row in admin shows all profiles that have this sustainability interest
@admin.register(SustainabilityInterests)
class SustainabilityInterestsAdmin(admin.ModelAdmin):
    list_display = ("name", "users_list")

    def users_list(self, obj):
        return ", ".join([p.user.username for p in obj.profile_set.all()])
    users_list.short_description = "Users"

@admin.register(TradingInterests)
class TradingInterestsAdmin(admin.ModelAdmin):
    list_display = ("name", "users_list")

    def users_list(self, obj):
        return ", ".join([p.user.username for p in obj.profile_set.all()])
    users_list.short_description = "Users"