from django import template

register = template.Library()

@register.filter(name="to_eur")
def to_eur(value):
    """Format value as EUR."""
    return f"€ {value:,.2f}"
