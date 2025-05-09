# creating urls: 

#from django.contrib import admin

from django.urls import path, include 
from . import views
from .views import addToShelf, viewBookshelf, createReviewComment




#from .views import getBooks

urlpatterns = [
    #specifying paths: 
    path('', views.landingPage, name = "storyBridge_landingPage"),


    path('home/', views.home, name = "storyBridge_home"),

    path('reviewLikes/<int:pk>', views.reviewLike, name = "storyBridge_reviewLike"),
    path('home/<int:pk>/comment', views.createReviewComment, name = "storyBridge_createComment"),

    path('deleteReview/<int:pk>', views.deleteReview, name = "storyBridge_deleteReview"),

    path('login/', views.login_user, name= 'storyBridge_login'),
    path('logout/', views.logout_user, name= 'storyBridge_logout'),

    path('signUp/', views.signUp, name= 'storyBridge_signup'),
    path('signUpSuccess/', views.signUpSuccess, name= 'storyBridge_signupcomplete'),

    path('profile/<int:pk>', views.profile, name= 'storyBridge_profile'),
    path('editProfile/', views.editProfile, name= 'storyBridge_editProfile'),
    path('accountSettings/', views.accountSettings, name= 'storyBridge_accountSettings'),

    #path to display profile pages- 
    path('profileList/', views.profileList, name= 'storyBridge_profileList'),

    path('books/', views.myBooks, name='storyBridge_myBooks'),
    path('bookshelf/add/<str:book_key>/', views.addToShelf, name='storyBridge_addToShelf'),
    path('bookshelf/delete/', views.deleteBook, name='storyBridge_deleteBookFromShelf'),
    
    path('bookshelf/<str:shelfType>/', views.viewBookshelf, name='storyBridge_viewShelf'),
    path('bookshelf/rate/<int:entryId>/', views.rateBooks, name='storyBridge_rateBooks'),

    path('search-books/', views.searchBooks, name='storyBridge_searchBooks'),
    path('search-results/', views.searchResults, name='storyBridge_searchResults'),

    path('browse/', views.explore, name='storyBridge_explore'),
    path('browse/<str:genre>/', views.browseByGenre, name='storyBridge_genreBrowse'),

    path('books/<str:book_key>/', views.displayBookDetails, name='storyBridge_bookDetails'), #for book details 

    # path('goals/', views.goals, name='storyBridge_goals'),
    # path('badges/', views.badges, name='storyBridge_badges'),
    
    
 

]