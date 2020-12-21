from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
# from image_cropping import ImageCropWidget
from .models import Account,Profile,Suggetions

User = get_user_model()


class UserRegisterForm(UserCreationForm):
	email = forms.EmailField(max_length=254, help_text='Required. Add a valid email address.')
	newsletter = forms.BooleanField(label='subscribe to our newletter',required=False)

	class Meta:
		model = User
		fields = ('email', 'username', 'password1', 'password2','newsletter',)



class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    #parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    content = forms.CharField(label='', widget=forms.Textarea(attrs={'rows': 5, 'cols': 20,'placeholder':'Ask Question'}))

class UserUpdateForm(forms.ModelForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
	image = forms.ImageField(
		label=('image'),
		required=False,
		error_messages = {'invalid':("Image files only")},
		widget=forms.FileInput
	)
	class Meta:
		model = Profile
		fields = ['image']




class SuggestionForm(forms.ModelForm):
	class Meta:
		model = Suggetions
		widgets = {
            'title' : forms.TextInput(attrs = {'placeholder': 'Suggestions/Requests/Recommendations'}),
            'content'    : forms.Textarea(attrs = {'placeholder': 'Write here..'}),
        }
		fields = ['title','content']