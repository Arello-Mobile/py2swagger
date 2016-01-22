from rest_framework.serializers import ModelSerializer
from rest_framework.fields import IntegerField
from .models import TestModel, RelatedModel


class CustomField(IntegerField):
    type_label = None


class IncludedSerializer(ModelSerializer):

    class Meta:
        model = RelatedModel


class TestModelSeriazlizer(ModelSerializer):
    """
    ---
    fields:
    - name: text_field
      response:
        type: array
        items:
          type: string
    """

    related_models = IncludedSerializer(many=True)
    related_model = IncludedSerializer()
    custom_field = CustomField()
    custom_integer_field = IntegerField(min_value=0, max_value=10, default=lambda: 5, required=False)

    class Meta:
        model = TestModel
