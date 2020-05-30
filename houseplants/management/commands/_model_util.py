from houseplants.models import HouseplantItem


def remove_items():
    """
    Removes all model objects.
    """
    print('Removing %s items' % len(HouseplantItem.objects.all()))
    for model_item in HouseplantItem.objects.all():
        model_item.delete()
        print("Removal of %s complete." % model_item)
