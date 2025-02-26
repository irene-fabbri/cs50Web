from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from functools import wraps


from .forms import NewListingForm, BidForm, CommentForm

from .models import User, AuctionListing, Bid, Comment, WatchList


def index(request):

    listings = AuctionListing.objects.filter(status=True)
    if not listings:
        message = "Cannot load listings or no active listing present"
        return render(request, "auctions/index.html", {'listings':listings}, {'message':message})
    else:
        return render(request, "auctions/index.html", {'listings':listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'auctions/error.html', {'message': 'You must be logged in to view this page.'})
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@custom_login_required
def new_listing(request):

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = NewListingForm(request.POST)
        if form.is_valid():
            # get user
            user = request.user

            new = AuctionListing(
                user = user,
                title = form.cleaned_data['title'],
                description = form.cleaned_data['description'],
                start_price = form.cleaned_data['start_price'],
                image_url = form.cleaned_data['image_url'],
                category = form.cleaned_data['category']
            )
            new.save()

            messages.success(request, 'New listing added successfully')
            return redirect('index')

        messages.error(request, 'Form not valid')
        return redirect('newlisting')


    # if a GET (or any other method) we'll create a blank form

    return render(request, "auctions/newlisting.html", {'form': NewListingForm})

@custom_login_required
def listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    comments = Comment.objects.filter(listing_id=listing_id).order_by('date')

    if listing:
        # if this is a POST request we need to process the form data
        if request.method == "POST":
            if 'bid' in request.POST:
                # create a form instance and populate it with data from the request:
                bid_form = BidForm(request.POST)
                if bid_form.is_valid():
                    bid_amount = bid_form.cleaned_data['bid_amount']
                    # Call the place_bid method on the listing model
                    if listing.place_bid(request.user, bid_amount):
                        # Bid was successful
                        messages.success(request, 'New bid placed successfully')
                    else:
                        # Bid was not successful
                        messages.error(request, 'It was not possible to place the bid. The bid must be at least as large as the starting bid, and must be greater than any other bids that have been placed.')
                return redirect('listing', listing_id=listing_id)

            elif 'comment' in request.POST:
                comment_form = CommentForm(request.POST)
                if comment_form.is_valid():
                    comment = comment_form.cleaned_data['text']
                    new = Comment(
                        listing_id = listing,
                        user_id = request.user,
                        text = comment,
                    )
                    new.save()
                    return redirect('listing', listing_id=listing_id)

        else:
            bid_form = BidForm()
            comment_form = CommentForm()

        return render(request, 'auctions/listing.html', {'listing': listing, 'bid_form':bid_form, 'comment_form':comment_form, 'comments': comments})
    else:
        return render(request, 'auctions/error.html', {'message': 'Cannot access the selected listing item. Try again later'})


@custom_login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)

    if listing and request.user == listing.user:
        listing.close_auction()
        return redirect('listing', listing_id=listing_id)
    else:
        return render(request, 'auctions/error.html', {'message': 'There were some issues closing the auction'})

@custom_login_required
def watchlist_add(request, user_id, listing_id):
    if request.method == "POST":
        user = get_object_or_404(User, pk=user_id)
        listing = get_object_or_404(AuctionListing, pk=listing_id)

        if user and listing:
            WatchList.add(user, listing)
        else:
            return render(request, 'auctions/error.html', {'message': 'Issues adding the item to the watchlist'})

        return redirect('watchlist', user_id=user_id)
    else:
        return render(request, 'auctions/error.html', {'message': '405: Method Not Allowed'})


@custom_login_required
def watchlist_remove(request, user_id, listing_id):
    if request.method == "POST":
        user = get_object_or_404(User, pk=user_id)
        listing = get_object_or_404(AuctionListing, pk=listing_id)

        if user and listing:
            WatchList.remove(user, listing)
        else:
            return render(request, 'auctions/error.html', {'message': 'Issues removing the item from the watchlist'})

        return redirect('watchlist', user_id=user_id)
    else:
        return render(request, 'auctions/error.html', {'message': '405: Method Not Allowed'})


@custom_login_required
def watchlist(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if not user == request.user:
        return render(request, 'auctions/error.html', {'message': 'You can only look at your own watchlist'})

    watchlist_items = WatchList.objects.filter(user_id=user)

    return render(request, 'auctions/watchlist.html', {'watchlist_items': watchlist_items})

def category(request, category):
    category_items = AuctionListing.objects.filter(category=category, status=True)
    category_display_name = AuctionListing.CATEGORY_CHOICES_DICT[category]

    if category_items:
        return render(request, 'auctions/category.html',{'category_name': category_display_name, 'category_items': category_items})
    else:
        return render(request, 'auctions/error.html', {'message': 'No Active listings in this category'})

@custom_login_required
def my_bids(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if not user == request.user:
        return render(request, 'auctions/error.html', {'message': 'You can only look at your own bids'})

    bid_items = Bid.objects.filter(bidder_id=user)

    return render(request, 'auctions/bids.html', {'bid_items': bid_items})
