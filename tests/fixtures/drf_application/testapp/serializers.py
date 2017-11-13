import datetime

from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.fields import IntegerField, CharField, EmailField, DateTimeField

from .models import TestModel, RelatedModel


class CustomField(IntegerField):
    """
    ---
    request:
      type: array
      items:
        type: string
    response:
      type: string
    """
    type_label = None


class IncludedSerializer(ModelSerializer):

    class Meta:
        model = RelatedModel
        exclude = []


class TestModelSeriazlizer(ModelSerializer):
    """
    ---
    fields:
      text_field:
        required: true
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
        exclude = []


class TestSimpleSerializer(Serializer):
    test_field = IntegerField(min_value=0, max_value=10, default=lambda: 5, required=False)


# URL Parser tests
class CommentSerializer(Serializer):
    email = EmailField()
    content = CharField(max_length=200)
    created = DateTimeField(default=datetime.datetime.now)


class QuerySerializer(Serializer):
    query = CharField(max_length=100)

