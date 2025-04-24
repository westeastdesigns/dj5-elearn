from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class OrderField(models.PositiveIntegerField):
    """OrderField is a custom model field allowing an order to be defined for the objects. It inherits from Django's PositiveIntegerField and takes an optional for_fields parameter that allows indication of the fields used to order the data.

    Args:
        models (PositiveIntegerField): OrderField overrides PositiveIntegerField's pre_save() method executed before saving the field to the database.
    """
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)
    
    def pre_save(self, model_instance, add):
        """pre_save method checks whether a value already exists for this field in the model instance. self.attname is the attribute name given to the field in the model. If the attribute's value is None, the order is calculated.

        Args:
            model_instance (PositiveIntegerField): This represents the object's order. If there is no value, it is calculated. If there is a value, it is returned.
            add (Boolean): If the model is being saved to the database for the first time, this parameter will be True. Otherwise, it is False.

        Returns:
            PositiveIntegerField: the value of the object's order
        """
        if getattr(model_instance, self.attname) is None:
            # if there is no current value
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    # filter by objects with the same field values
                    # for the fields in "for_fields"
                    query = {
                        field: getattr(model_instance, field)
                        for field in self.for_fields
                    }
                    qs = qs.filter(**query)
                # get the order of the last item
                last_item = qs.latest(self.attname)
                value = getattr(last_item, self.attname) + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)