from django import forms
from django.forms import ModelForm
from .models import User, AuctionListing, Bid, Comment

class NewListingForm(ModelForm):
    class Meta:
        model = AuctionListing
        fields = ["title", "description", "start_price", "image_url", "category"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-item','placeholder':'Name'}),
            'description': forms.Textarea(attrs={'class': 'form-item', 'placeholder':'Description'}),
            'start_price' : forms.NumberInput(attrs={'class': 'form-item','placeholder':'Starting price'}),
            'image_url': forms.TextInput(attrs={'class': 'form-item', 'placeholder':'Image URL (optional)'}),
            'category': forms.Select(attrs={'class': 'form-item', 'placeholder':'Category(optional)'})
        }
        labels = {
            'title': 'Title',
            'description': 'Description',
            'start_price' : 'Starting Price',
            'image_url': 'Image URL',
            'category': 'Category',
        }

class BidForm(forms.Form):
    bid_amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Your Bid:",
        widget = forms.TextInput(attrs={'placeholder': 'Place your bid'})
    )

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 5, 'placeholder': 'Add a comment'})
        }
    # comment = forms.CharField()
