from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from orders.models import OrderFish

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=OrderFish)
def update_fish_store_on_create(sender, instance, created, **kwargs):
    """
    Aktualizuje zásobu ryb pouze při vytvoření objednávky.
    """
    if created:
        # Nová objednávka - snížíme zásobu
        instance.fish.store -= instance.amount
        instance.fish.save()


@receiver(post_delete, sender=OrderFish)
def update_fish_store_on_delete(sender, instance, **kwargs):
    """
    Přičte zpět množství ryb do zásoby při odstranění objednávky.
    """
    instance.fish.store += instance.amount
    instance.fish.save()
