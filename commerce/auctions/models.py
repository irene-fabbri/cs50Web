from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max


class User(AbstractUser):
    pass

class AuctionListing(models.Model):

    CATEGORY_CHOICES = [
        ('elettronica', 'Elettronica'),
        ('gaming', 'Gaming'),
        ('elettrodomestici', 'Elettrodomestici'),
        ('casa', 'Casa e Giardino'),
        ('diy', 'Fai da te'),
        ('collezionismo', 'Collezionismo'),
        ('moda', 'Moda'),
        ('sport', 'Sport'),
        ('motori', 'Motori'),
        ('altro', 'Altro')
    ]

    CATEGORY_CHOICES_DICT = dict(CATEGORY_CHOICES)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings") # related_name so that I can do user.listings.all()
    title = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add = True)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, blank=True, null=True)
    start_price = models.DecimalField(max_digits=8, decimal_places=2)
    current_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.BooleanField(default = True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="bids_won") # user.bid_won.all()

    def place_bid(self, bidder, bid_amount):
        if ( not self.bids.all() and bid_amount >= self.start_price) or (self.bids.all() and bid_amount > self.current_price):
            # create bid object
            new = Bid(
                listing_id = self,
                bidder_id = bidder,
                amount = bid_amount
            )
            new.save()

            # update current price
            self.current_price = bid_amount
            self.save()
            return True
        return False

    def bid_count(self):
        return self.bids.count()

    def close_auction(self):
        if self.bids.all():
            winning_bid = self.bids.order_by('-amount').first()
            self.winner = winning_bid.bidder_id
            winning_bid.winner = True
            winning_bid.save()
            self.status = False
            self.save()
        return f"{self.winner}"

    def save(self, *args, **kwargs):
        if not self.image_url:
            self.image_url = 'https://upload.wikimedia.org/wikipedia/commons/f/f8/No-image-available-4X3.png'

        if not self.current_price:
            self.current_price = self.start_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    listing_id = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids") # listing.bids.all()
    bidder_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_placed") # user.bids_placed.all()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    winner = models.BooleanField(default = False)

    def __str__(self):
        return f"{self.amount} €"

class Comment(models.Model):
    listing_id = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments") # listing.comments.all()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_posted") # user.comments_posted.all()
    date = models.DateTimeField(auto_now_add = True)
    text = models.TextField()

    def __str__(self):
        return f"{self.text}"

class WatchList(models.Model):
    listing_id = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="whatched") # listing.whatched.all()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist") # user.watchlist.all()

    def add(user, listing):
        # Check if the listing is already in the user's watchlist
        if not user.watchlist.filter(listing_id = listing).exists():
            # If not, create a new WatchList entry
            new = WatchList(
                listing_id = listing,
                user_id = user
            )
            new.save()
            return True
        return False

    def remove(user, listing):
        # Check if the listing in the user's watchlist
        if user.watchlist.filter(listing_id = listing).exists():
            # cancel it
            user.watchlist.filter(listing_id = listing).delete()
            return True
        return False

    def __str__(self):
        return f"User: {self.user_id.username} Item: {self.listing_id}"
