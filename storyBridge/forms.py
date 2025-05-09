#this is going to be the user registration section (using django built in registration)

from django import forms 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import Reviews, Profile, ReadingChallenge, Comments

#creating a form that lets user register: 
class SignUpForm(UserCreationForm):

        class Meta:
                model = User
                fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
 
        def __init__(self, *args, **kwargs):
                super(SignUpForm, self).__init__(*args, **kwargs)
                self.fields['username'].widget.attrs['class'] = 'signUpInputs'
                self.fields['username'].widget.attrs['placeholder'] = 'User Name'
                self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'
                
                self.fields['first_name'].widget.attrs['class'] = 'signUpInputs'
                self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'

                self.fields['last_name'].widget.attrs['class'] = 'signUpInputs'
                self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'

                self.fields['email'].widget.attrs['class'] = 'signUpInputs'
                self.fields['email'].widget.attrs['placeholder'] = 'Email Address'

                self.fields['password1'].widget.attrs['class'] = 'signUpInputs'
                self.fields['password1'].widget.attrs['placeholder'] = 'Password'

                #help text: 
                self.fields['password1'].help_text = """
                <small>
                        <ul>
                                <li>Your password must contain at least 8 characters.</li>
                                <li>Your password can't be a commonly used password.</li>
                                <li>Your password can't be entirely numeric.</li>
                        </ul>
                </small>
                """
                
                self.fields['password2'].widget.attrs['class'] = 'signUpInputs'
                self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'


#form that allows users profile to be updated 
class UpdateUserForm(UserChangeForm):

        class Meta:
                model = User
                fields = ('username', 'first_name', 'last_name', 'email')

        def __init__(self, *args, **kwargs):
                super(UpdateUserForm, self).__init__(*args, **kwargs)
                self.fields['username'].widget.attrs['class'] = 'form-control'
                self.fields['username'].widget.attrs['placeholder'] = 'User name'

                self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
                self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'
                self.fields['email'].widget.attrs['placeholder'] = 'Email address'
                #thi stells uers what required (small text) 
                #self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'
                

class UpdatePasswordForm(SetPasswordForm):
        class Meta:
                model = User
                fields = ['new_password1', 'new_password2']

        def __init__(self, *args, **kwargs):
                super(UpdatePasswordForm, self).__init__(*args, **kwargs)
                
                self.fields['new_password1'].widget.attrs['class'] = 'signUpInputs'
                self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'

                #same help text: 
                self.fields['new_password1'].help_text = """
                <small>
                        <ul>
                                <li>Your password must contain at least 8 characters.</li>
                                <li>Your password can't be a commonly used password.</li>
                                <li>Your password can't be entirely numeric.</li>
                        </ul>
                </small>
                """
                
                self.fields['new_password2'].widget.attrs['class'] = 'signUpInputs'
                self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'


#form to create a review 
class ReviewForm(forms.ModelForm):
        # body = forms.CharField(required=True, widget=forms.widgets.Textarea(attrs={
        #         "placeholder": "what do you think of the book?",
        #         }),
        #         label="",
        # )

        class Meta:
                model = Reviews
                # exclude = ('user', 'book', 'likes',)
                fields = ['rating', 'body'] #new- trying to get star rating!!!!
                widgets = {
                        'rating': forms.HiddenInput(),
                        'body': forms.Textarea(attrs={'rows':4}),
                }
                 


# update profile pic
class ProfilePictureForm(forms.ModelForm):
        profileImg = forms.ImageField(label="profile picture")

        #saving to profile model-
        class Meta:
                model = Profile
                fields = ('profileImg',)


#form to update reading goal -
class ReadingChallengeForm(forms.ModelForm):
        class Meta:
                model = ReadingChallenge
                fields = ('goal',)


#form to let users add a comment to a review: 
class CommentForm(forms.ModelForm):
        class Meta:
                model = Comments
                fields = ['name', 'body']