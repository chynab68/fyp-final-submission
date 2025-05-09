from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, UpdateUserForm, ReviewForm, ProfilePictureForm, ReadingChallengeForm, CommentForm, UpdatePasswordForm
import requests
from django.http import JsonResponse
import time
from django.utils import timezone
from datetime import timedelta
from datetime import datetime 
from django.contrib.auth.decorators import login_required
from .models import Books, Bookshelfs, Authors, Profile, Reviews, ReadingChallenge, Comments

#from .forms import RegistrationForm


def landingPage(request):
    return render(request, 'storyBridge/landingpage.html')

#@login_required
def home(request):

    if request.user.is_authenticated:
        currentlyReading = Bookshelfs.objects.filter(user=request.user, bookshelfType='CR'[:4])

        #allow profile image to be shown:
        profile = Profile.objects.get(user  = request.user)

        #want to show my reviews and those from followed accoutns: 
        usersFollowed = profile.follows.all().values_list('user__id',flat=True)
        myUserPlusFollowedIds = list(usersFollowed) + [request.user.id]

        reviews = Reviews.objects.filter(user__id__in=myUserPlusFollowedIds).order_by("-createdDate")

        return render(request, 'storyBridge/homePage.html',{
            'currentlyReading': currentlyReading, 'reviews': reviews, "profile": profile
        })

#view that deals w likes on a review:
def reviewLike(request, pk): #pk tells you what review is being dealt w 
    if request.user.is_authenticated:
        review = get_object_or_404(Reviews, id=pk)
        if review.likes.filter(id=request.user.id):
            #if review has a like with the requesting users id, remove their like 
            review.likes.remove(request.user)

        else: #if they've not likes the review yet
            review.likes.add(request.user)
        
        return redirect("storyBridge_home")

#view to let users create a comment on a review- 
def createReviewComment(request, pk):
    #comment section that appears on same section as review: 
    review = get_object_or_404(Reviews, pk=pk)

    if request.method == "POST":
        body = request.POST.get('body')

        if body:
            Comments.objects.create(
                review = review,
                name=request.user,
                body=body
            )

    return redirect("storyBridge_home")
     


def login_user(request):
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        #check its the right username/password combo: 
        if user is not None:
            login(request, user)
            messages.success(request, ("You have been logged in"))
            return redirect('storyBridge_home')
        #if not successful-
        else:
            return redirect('storyBridge_login')

    else:
       return render(request, 'storyBridge/login.html') 



def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out"))
    return redirect('storyBridge_login')


def signUp(request):
    form = SignUpForm()

    # are they filling out form?  
    if request.method == "POST":
        form = SignUpForm(request.POST) 
        #is this valid? 
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            #log user in:
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('storyBridge_home')
        
        else:
            messages.error(request, ('Incorrect information entered, please try again')) 
            return redirect('storyBridge_signup')

    else:
        return render(request, 'storyBridge/signUpPage.html', {'form':form})


def signUpSuccess(request):
    return render(request, 'StoryBridge/registrationSuccess.html' )  


# views for profile section:
def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)

        #getting personal reviews to show on profile page-
        reviews = Reviews.objects.filter(user_id=pk).order_by("-createdDate")

        #reading challenge- 
        challenge, created = ReadingChallenge.objects.get_or_create(user= request.user)

        form = ReadingChallengeForm(request.POST, instance=challenge)

        #form logic (follow/unfollow):
        if request.method == "POST":

            #get current user id: 
            currentUserProfile = request.user.profile

            #get form data:
            # action = request.POST['follow']
            action = request.POST.get('follow')

            #decising to follow or unfollow- 
            if action == "unfollow":
                currentUserProfile.follows.remove(profile)

            elif action =="follow":
                currentUserProfile.follows.add(profile)

            currentUserProfile.save()

            if form.is_valid():
                form.save()
                # return redirect(goals)
            
            else:
                form = ReadingChallengeForm(instance=challenge)

        currentlyReading = Bookshelfs.objects.filter(user=profile.user, bookshelfType='CR'[:4])

        return render(request, 'StoryBridge/profileSection/profilePage.html', {
            "profile": profile, 'currentlyReading': currentlyReading, 'reviews': reviews, 'form':form, 'challenge': challenge 
            } )

    else:
        return redirect('storyBridge_home')






#view to handle deletting review
def deleteReview(request, pk):
    #is user logged in? 
    if request.user.is_authenticated:
        review = get_object_or_404(Reviews, id=pk)

        #make sure you can only delete your own review: 
        if request.user.username == review.user.username:
            review.delete()
            return redirect('storyBridge_profile', pk=request.user.id)
        
    else: 
        return redirect('storyBridge_home')
    


def profileList(request):
    profiles = Profile.objects.exclude(user=request.user) #gives list of other users
    

    return render(request, 'StoryBridge/profileSection/profileList.html', {"profiles": profiles} )

def editProfile(request):
    if request.user.is_authenticated:

        #allow profile image to be shown:
        profile = Profile.objects.get(user  = request.user)

        #look up user id in user model 
        currentUser = User.objects.get(id=request.user.id)
        userProfile = Profile.objects.get(user__id=request.user.id) #grabs profile info 


        #get forms-
        userForm = UpdateUserForm(request.POST or None, request.FILES or None, instance=currentUser) #when user goes to profile page, it will already have their info in the form
        profileForm = ProfilePictureForm(request.POST or None, request.FILES or None, instance=userProfile)

        if userForm.is_valid() and profileForm.is_valid():
            userForm.save() #once info has been updated, log them back in w that updated info 
            profileForm.save()

            login(request, currentUser)
            messages.success(request, "User has been updated!")
            return redirect('storyBridge_profile', pk=request.user.id)
    
        return render(request, 'StoryBridge/profileSection/editProfile.html', {'userForm': userForm, 'profileForm':profileForm, "profile": profile }) 
    
    #if not logged in:
    else:
        messages.success(request, "You must be logged in to access this page ")
        return redirect('storyBridge_home')


def accountSettings(request):

    if request.user.is_authenticated:
        currentUser = request.user 

        #form filled out?? 
        if request.method == 'POST':
            form = UpdatePasswordForm(currentUser, request.POST)
            #is form valid?
            if form.is_valid():
                form.save() 
                messages.success(request, "Your password has been successfully updated!")
                login(request, currentUser)
                return redirect('storyBridge_home')
            
            else: 
                for error in list(form.errors.values()):
                    messages.error(request, error)


        else:
            form = UpdatePasswordForm(currentUser)
            
        return render(request, 'StoryBridge/profileSection/accountSettings.html', {'form': form} )


#this fetches data from open library and allows users to search for books based on title, author, subject- API CALL
def searchBooks(request):
    query = request.GET.get('query', '').strip() #this is the search term 

    if not query:
        return JsonResponse({"error": "no query provided"}, status=400)
    
    #make request to open library api to search for books: 
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)

    if response.status_code == 200: #if request has been processed properly 
        booksData = response.json()
        books = booksData.get('docs', [])

        #debugging by printing api response: 
        print("Raw API Response: ", booksData)
        print("Extracted books: ", books)

        if not books:
            return JsonResponse([], safe=False) #return an empty list if no books are found 


        bookInfo = []
        for book in books[:10]: #limits results to 10 items 
            title = book.get('title', 'No Title')
            author_name = book.get('author_name', ['Unknown Author'])[0]
            first_publish_year = book.get('first_publish_year', 'N/A')
            cover_id = book.get('cover_i', None)
            cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else ''

            bookInfo.append({
                'title': title,
                'author': author_name,
                'first_publish_year': first_publish_year,
                'cover_url': cover_url,
                'openlibrary_url': f"https://openlibrary.org{book.get('key', '')}"
            })

        #print("Final Book info: ", bookInfo ) #debug
        return render(request, 'storyBridge/explore/searchResults.html', {'books': bookInfo, 'query': query})
    
        
    return JsonResponse({"error": "Failed to fetch data from Open Library API"}, status=500)


#page view that renders results 
def searchResults(request):

     #allow profile image to be shown:
    profile = Profile.objects.get(user  = request.user)

    query = request.GET.get('query', '').strip()
    print(f"Received query: {query}") #debug 
    
    if not query:
        return render(request, 'storyBridge/explore/searchResults.html', {'books': [], 'query': query}) 
    
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)

    if response.status_code == 200: 
        booksData = response.json()
        books = booksData.get('docs', [])

        bookInfo = []
        for book in books[:10]:
            title = book.get('title', 'No Title')
            author_name = book.get('author_name', ['Unknown Author'])[0]
            first_publish_year = book.get('first_publish_year', 'N/A')
            cover_id = book.get('cover_i', None)
            cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else ''

            #bookKey = book.get('key', '').lstrip('/') #NEWLY ADDED
            bookKey = book.get('key', '')

            bookInfo.append({
                'title': title,
                'author': author_name,
                'first_publish_year': first_publish_year,
                'cover_url': cover_url,
                'openlibrary_url': f"https://openlibrary.org{book.get('key', '')}",

                'book_key': bookKey,
            })
        print(f"Final Book Info: {bookInfo}") #debugging 
        return render(request, 'storyBridge/explore/searchResults.html', {'books': bookInfo, 'query': query, 'profile': profile})
    
    return render(request, 'storyBridge/explore/searchResults.html', {'books': [], 'query': query})


#views for explore section:
def explore(request): 
     #allow profile image to be shown:
    profile = Profile.objects.get(user  = request.user)

    return render(request, 'storyBridge/explore/explorePage.html', {'profile':profile}) 

def browseByGenre(request, genre): #passes in genre from open library 'genre' 

    #allow profile image to be shown:
    profile = Profile.objects.get(user  = request.user)

    url = f"https://openlibrary.org/subjects/{genre}.json" 
    response = requests.get(url)

    if response.status_code == 200:
        booksData = response.json()
        books = booksData.get('works', [])

        bookInfo = []
        for book in books[:10]: #limit results being shown
            title = book.get('title', 'No Title')
            author = book.get('authors', [{'name': 'Unknown author'}])[0]['name']
            cover_id = book.get('cover_id') or book.get('cover_i') #get image to show 

            bookKey = book.get('key', '')
            print(f"Extracted book key: {bookKey}") #debugging

            cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else ''
            book_url = f"https://openlibrary.org{book.get('key', '')}"

            bookInfo.append({
                'title': title,
                'author': author,
                'cover_url': cover_url,
                'book_url': book_url,

                'book_key': bookKey, 
            })

        return render(request, 'storyBridge/explore/browseByGenre.html', {'books': bookInfo, 'genre': genre, 'profile':profile})
    
    return render(request, 'storyBridge/explore/browseByGenre.html', {'books': [], 'genre': genre})


#view to show details when book is clicked on:
def displayBookDetails(request, book_key): 

    #allow profile image to be shown:
    profile = Profile.objects.get(user  = request.user)

    if not book_key.startswith("/works/"):
        book_key = f"/works/{book_key}"

    url = f"https://openlibrary.org{book_key}.json" 

    print(f"Fetching: {url}") #debugging to see the url being requested 

    response = requests.get(url)

    print(f"Response status code: {response.status_code}") 

    #if request works: 
    if response.status_code == 200:
        bookData = response.json()

        print(f"Book data: {bookData}") #debugging: print api response

        #extracting relevant details open library: 

        #title extraction:
        title = bookData.get('title', 'No Title')
        
        #extracting author data  
        authors = []
        if 'authors' in bookData:

            print("Authors field exists in bookDate: ", bookData['authors']) #debugging statement 

            for author_entry in bookData['authors']:
                #author_key = author_entry.get('key', '')

                author_key = author_entry.get('author', {}).get('key')

                if author_key:  # Ensure author_key is not empty
                    author_url = f"https://openlibrary.org{author_key}.json"  # Correct API URL

                    print(f"fetching author details from: {author_url}") #debug 

                    #having issues w timeout, so adding retries and increasing timeout
                    retries = 3
                    for attempt in range (retries):
                    
                        try:
                            author_response = requests.get(author_url, timeout=15)  
                            author_response.raise_for_status()  # Raise HTTP errors

                            author_data = author_response.json()
                            print("Author data response: ", author_data) #debug 

                            author_name = author_data.get('name', 'Unknown Author')
                            authors.append(author_name)
                            break #stop if successful 
                        
                        except requests.exceptions.Timeout:
                            print(f"Timeout error on attempt number: {attempt + 1}. Retrying...")
                            time.sleep(2) #wait before retry 

                        except requests.exceptions.RequestException as e:
                            print(f"Failed to fetch author details: {e}")
                            break #stop if another error occurs 

                    else:
                        authors.append('Unknown author')  

        # If no authors were found, use "Unknown Author"
        if not authors:
            print("no authors found in api response, setting to 'unknown author' ") #debug 
            authors = ['Unknown Author']

        #decription extraction
        description = bookData.get('description', {}).get('value', 'No description available') if isinstance(bookData.get('description', {}), dict) else bookData.get('description', 'No description available')
        
        
        #publishDate extraction
        #year of release: 
        publish_date = bookData.get('created', {}).get('value', 'N/A')

        try:
            publish_year = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%S.%f").year if publish_date != 'N/A' else 'N/A'
        except ValueError:
            publish_year = 'N/A' #deals w unexpected date formats 


        #cover id/url extraction
        cover_id = bookData.get('covers', [None])[0]
        cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else ''
        
        #stripping /works/:
        book_keyClean = book_key.replace("/works/", "")

        #storing extracted data: 
        bookInfo = {
            'book_key': book_keyClean, #new!!!!!!
            #'book_key': book_key,
            'title': title,
            'authors': authors,
            'description': description,
            'publish_date': publish_year,
            'cover_url': cover_url,
        }
        
        #allows author info to be displayed-
        authorName = bookInfo['authors']
        authorObject, _ = Authors.objects.get_or_create(authorName=authorName)

        
        book, created = Books.objects.get_or_create(
            bookKey=bookInfo['book_key'],
            defaults={
                'bookTitle': bookInfo['title'],
                'author': authorObject,
                'bookDescription': bookInfo['description'] ,
                'coverURL': bookInfo['cover_url'] 
            }
        )

    
         
        # if user has left a review already, want to give them option to update review:
        existingReview = None
        if request.user.is_authenticated:
            try:
                existingReview = Reviews.objects.get(user=request.user, book=book)
            except Reviews.DoesNotExist:
                existingReview = None

        if request.method == "POST" and request.user.is_authenticated: #if from is submitted and user is logged in 
            if existingReview: #if they've already written a review
                form = ReviewForm(request.POST, instance=existingReview)
            else:
                form = ReviewForm(request.POST)
            if form.is_valid(): 
                review = form.save(commit=False) 
                review.user = request.user #saves review to user that created it 
                review.book = book #associates review w displayed book 
                review.save()
                return redirect('storyBridge_bookDetails', book_key = book_keyClean)
        
        else:
            form = ReviewForm(instance=existingReview) if request.user.is_authenticated else None


        return render(request, 'storyBridge/explore/bookDetails.html' , {'book': bookInfo,'form':form, 'existingReview':existingReview, 'profile':profile})

        
    #print("book not found :(") #debug 
    return render(request, 'storyBridge/explore/bookDetails.html' , {'book': None, 'error': 'Book not found!'})



#view that deals w book selection:

@login_required
def addToShelf(request, book_key):
    if request.method == "POST":
        bookshelfChoice = request.POST.get("bookshelfChoice")

        #get book details from open library- 
        url = f"https://openlibrary.org/works/{book_key}.json"
        response = requests.get(url)

        if response.status_code == 200:
            bookData = response.json()
            print("Fetched book data: ", bookData) #to debug

            #extracting book deets:
            title = bookData.get("title", "Unknown Title")
            description = bookData.get("description", {}).get("value", "No description available") if isinstance(bookData.get("description", {}), dict) else bookData.get("description", "No description available")

            #extracting book cover url: 
            coverURL = ""
            if "covers" in bookData:
                coverId = bookData["covers"][0]
                coverURL = f"https://covers.openlibrary.org/b/id/{coverId}-L.jpg"

            authorObject = None
            authorNames = [] #store names to debug

            if "authors" in bookData:
                authorKeys = [author['author']['key'] for author in bookData['authors']]

                for author_key in authorKeys: 
                    authorResponse = requests.get(f"https://openlibrary.org{author_key}.json")

                    if authorResponse.status_code == 200:
                        authorName = authorResponse.json().get("name", "Unknown author") #CHANGED name FROM authorName!
                        authorNames.append(authorName)

                    #authorObject, _ = Authors.objects.get_or_create(authorName=authorName) #may have to change second author name 91st is name in Authors model)

                    break
            
            #debug to check whats being fetched: 
            print("Featched author- ", authorNames)

            if authorObject is None:
                authorObject, _ = Authors.objects.get_or_create(authorName="Unknown author")


            #check if book exists in db:
            book, created = Books.objects.get_or_create(
                bookKey = book_key, 
                defaults={
                    #storing book descriptiona and cover url:
                    "bookTitle": title,
                    "bookDescription": description,
                    "author": authorObject,
                    "coverURL" : coverURL,
                }
            )

            #get author to appear in shelf: 
            if not created and book.author is None:
                book.author = authorObject #update author if its missing
                book.save()

            #saving to users bookshelf: 
            bookshelfEntry, created = Bookshelfs.objects.get_or_create(
                book = book,
                user = request.user,
                defaults={
                    "bookshelfType": bookshelfChoice,
                }
            )
            if not created:
                bookshelfEntry.bookshelfType = bookshelfChoice #updating if it already exists!
                bookshelfEntry.save()

            #reading challenge section- checking if book has been added to 'read' shelf: 
            if bookshelfChoice == 'RD': #might need to change 'rd' to read, not sre yet!
                challenge, created = ReadingChallenge.objects.get_or_create(user=request.user)
                challenge.booksRead += 1 
                challenge.save()


            print("Redirecting to shelf: ", bookshelfEntry.bookshelfType) #debug 
            
            return redirect("storyBridge_myBooks") #redirecting to bookshelf 
        
    return redirect("displayBookDetails", book_key=book_key)  
 



#views for books sections:
@login_required
def myBooks(request):

    #allow profile image to be shown:
    profile = Profile.objects.get(user  = request.user)

    #show books in different bookshelves
    wantToRead = Bookshelfs.objects.filter(user=request.user, bookshelfType='WTR'[:5]) 
    currentlyReading = Bookshelfs.objects.filter(user=request.user, bookshelfType='CR'[:5])
    read = Bookshelfs.objects.filter(user=request.user, bookshelfType='RD'[:5])
    didNotFinish = Bookshelfs.objects.filter(user=request.user, bookshelfType='DNF'[:5])
    

    return render(request, 'storyBridge/books/myBooks.html',{
        'wantToRead': wantToRead,
        'currentlyReading': currentlyReading,
        'read': read,
        'didNotFinish': didNotFinish,
        'profile':profile
    })

#individual bookshelves
def viewBookshelf(request, shelfType):

    #allow profile image to be shown:
    profile = Profile.objects.get(user  = request.user)

    books = Bookshelfs.objects.filter(user = request.user, bookshelfType=shelfType).select_related('book')
    return render(request, 'storyBridge/books/bookshelf.html', {"books": books, "shelfType": shelfType, 'profile':profile} )

#review view:    
def rateBooks(request, entryId, book_key):
    book = Books.objects.get(pk = book_key)
    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect("displayBookDetails", book_key=book.id)
    else:
        form = ReviewForm()
    return render(request, 'storyBridge/explore/bookDetails.html', {'form':form, 'book':book})
    # if request.method == "POST":
    #     bookshelfEntry = get_object_or_404(Bookshelfs, id=entryId, user=request.user)
    #     rating = request.POST.get("rating")

    #     if rating:
    #         bookshelfEntry.rating = int(rating)
    #         bookshelfEntry.save() 

    # if bookshelfEntry.bookshelfType:
    #     return redirect("storyBridge_viewShelf", shelfType = bookshelfEntry.bookshelfType)
    # else:
    #     print("error: bookshelf type is none for entry ", bookshelfEntry.id)

#view to delete book from shelf: 
@login_required
def deleteBook(request):
    if request.method == "POST":
        selectedBook = request.POST.getlist("chosenBook")

        if selectedBook:
            Bookshelfs.objects.filter(id__in=selectedBook, user=request.user).delete()

    # Redirect back to the same shelf
    referer = request.META.get("HTTP_REFERER", "/")
    return redirect(referer)



