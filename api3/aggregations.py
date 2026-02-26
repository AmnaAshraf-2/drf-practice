from django.db.models import Aggregate, FloatField, Sum

class DoubleSum(Aggregate):
    function = 'SUM'
    template = 'SUM(%(expressions)s * 2)'
    output_field = FloatField()