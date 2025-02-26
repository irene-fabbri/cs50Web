from .models import AuctionListing

def categories_processor(request):
    listings = AuctionListing.objects.filter(status=True).exclude(category=None)
    categories = listings.values_list('category', flat=True).distinct()
    category_links = [(cat, AuctionListing.CATEGORY_CHOICES_DICT[cat]) for cat in categories]

    return {'categories': category_links}
