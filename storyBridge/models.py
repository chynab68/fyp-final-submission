from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save #any time user gets saved, send a signal to do something 
from django.utils import timezone
from django.db.models import Avg

# # Create your models here.


#user profile model: 
class Profile(models.Model):
    #associating one profile w one user-
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    #profiles need to be able follow each other- 
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)

    dateModified = models.DateTimeField(User, auto_now=True)

    profileImg = models.ImageField(null=True, blank=True, upload_to="images/")

    def __str__(self):
        return self.user.username

#create profile when user signs up:
def createProfile(sender, instance, created, **kwargs):
    if created:
        userProfile = Profile(user=instance)
        userProfile.save()

        #follow self when sign up: 
        userProfile.follows.set([instance.profile.id])
        userProfile.save()

post_save.connect(createProfile, sender=User)


#class for authors:
class Authors(models.Model):
    authorName = models.CharField(max_length=255)

    def __str__(self):
        return self.authorName

       

#class for books: 
class Books(models.Model):
    bookTitle = models.CharField(max_length=500)
    bookKey = models.CharField(max_length=250, blank=True, null=True)
    genre = models.ManyToManyField("Genres")
    bookDescription = models.TextField(blank=False)
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE, null=True, blank=True) 
    #getting image url:
    coverURL = models.URLField(blank=True, null=True)


    #user = models.ForeignKey('auth.User', on_delete=models.CASCADE) #may want to change this later (when change to customer user!)
    #bookshelf = models.ForeignKey("Bookshelf", on_delete=models.CASCADE)

    # def __str__(self):
    #     return self.bookTitle
    

#class for genres: 
class Genres(models.Model):
    genreName = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)

    # def __str__(self):
    #     return self.genreName #displays egnre name in admin 


#model for bookshelves: 
class Bookshelfs(models.Model):
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    dateAddedToShelf = models.DateTimeField(auto_now_add=True)

    CURRENTLY_READING = "CR"
    WANT_TO_READ = "WTR"
    READ = "RD"
    DID_NOT_FINISH = "DNF"
    BOOKSELF_TYPE = {
        CURRENTLY_READING: "CurrentlyReading",
        WANT_TO_READ: "WantToRead",
        READ: "Read",
        DID_NOT_FINISH: "DidNotFinish",
    }
    bookshelfType = models.CharField(max_length=20, choices=BOOKSELF_TYPE.items())
    rating = models.IntegerField(null=True, blank=True) #ratings


#model for reviews (trying diff method!):
class Reviews(models.Model):
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.DO_NOTHING)
    body = models.CharField(max_length=500, null=True, blank=True)  
    createdDate = models.DateTimeField(auto_now_add=True, null=True, blank=True )
    likes = models.ManyToManyField(User, related_name="reviewLike", blank=True)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0)

    #keep track of likes on reviews-
    def numOfLikes(self):
        return self.likes.count()

    def __str__(self):
        return (
            f"{self.user}"
            f"({self.createdDate:%d-%m-%Y %H %M}): "
            f"{self.body}..."
            f"{self.rating}"
        )



#model for reading challenge: 
class ReadingChallenge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    goal = models.PositiveIntegerField(default=0)
    booksRead = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Reading Challenge"

class Comments(models.Model):
    review = models.ForeignKey(Reviews, related_name= "comments", on_delete=models.CASCADE)
    name = models.ForeignKey(User, on_delete=models.CASCADE) 
    #name = models.CharField(max_length=255) 
    body = models.TextField()
    dateCreated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.review.body} - {self.name.username}'
        #return '%s - %s' % (self.review.body, self.name)