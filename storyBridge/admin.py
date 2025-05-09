from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Authors, Profile, Books, Genres, Bookshelfs, Reviews, ReadingChallenge, Comments

#unregister groups-
admin.site.unregister(Group)

#mix profile into user info (so that profile info gets shown in user info) 
class ProfileInline(admin.StackedInline):
    model = Profile

#extending user model- 
class UserAdmin(admin.ModelAdmin):
    model = User
    
    inlines = [ProfileInline]

admin.site.unregister(User) #unregister initial user

#reregister user:
admin.site.register(User, UserAdmin)



admin.site.register(Authors)
#admin.site.register(Profile)
admin.site.register(Books)
admin.site.register(Genres)
admin.site.register(Bookshelfs)
admin.site.register(Reviews)
admin.site.register(ReadingChallenge)
admin.site.register(Comments)

# admin.site.register(Badge_Obtained_By_User)
# admin.site.register(User_Reads_Book)



