from django.db import models


def get_default():
    return 0


class AbstractModel(models.Model):
    parent_field = models.IntegerField()

    class Meta:
        abstract = True


class RelatedModel(models.Model):
    related_field = models.IntegerField()


class TestModel(AbstractModel):

    choices = (
        ('a', 'Choice 1'),
        ('b', 'Choice 2')
    )

    datetime_field = models.DateTimeField(help_text='Date time field')
    date_field = models.DateField(help_text='Date field')
    time_field = models.TimeField(help_text='Date field')

    char_field = models.CharField(help_text='Char field', max_length=50)
    choices_field = models.CharField(max_length=1, choices=choices, default='a')
    text_field = models.TextField(help_text='Text field')

    decimal_field = models.DecimalField(decimal_places=5, blank=True, null=True, default=100.0, max_digits=10)
    float_field = models.FloatField(help_text='Float field')
    integer_field = models.IntegerField(help_text='Integer field', default=get_default, null=True)
    boolean_field = models.BooleanField(default=False)

    file_field = models.FileField(verbose_name='File', help_text='File field', upload_to='media')

    related_field = models.ForeignKey('RelatedModel')
