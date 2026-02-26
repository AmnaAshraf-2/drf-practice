from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Car
from django.db.models import (
    Count, Avg, Min, Max, Sum,
    StdDev, Variance, F, Q, FloatField,
    ExpressionWrapper, Value, Func, DecimalField, Subquery, OuterRef
)

from rest_framework.generics import ListCreateAPIView
from .serializers import CarSerializer
from .aggregations import DoubleSum


class CarListCreateAPIView(ListCreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

# APIView to show the difference between Aggregate and Annotate
class CarAggregateAndAnnotateView(APIView):

    def get(self, request):

        overallStat = Car.objects.aggregate(
            count = Count('model'),
            min_price = Min('price'),
            max_price = Max('price'),
            avg_price = Avg('price'),
            sum_price = Sum('price'),
            std_dev = StdDev('price'),
            variance = Variance('price'),
            # Custom Aggregate
            double_sum = DoubleSum('price'),
        )

        statPerModel = Car.objects.values('model').annotate(
            count=Count('model'),
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
            sum_price=Sum('price'),
            std_dev=StdDev('price'),
            variance=Variance('price'),
            double_sum=DoubleSum('price'),
            # Using F() object and ExpressionWraper()
            discounted_price=ExpressionWrapper(F('price') * 0.9, FloatField())
        ).order_by('model')

        return Response({
            'overll_stat': overallStat,
            'stat_per_model': statPerModel,
        })


# Using Q() and F() object together
class FQView(APIView):
    def get(self, request):
        Car.objects.filter(
            Q(price__gt=2000000) | Q(year__lt=2020)
        ).update(price=F('price') * Value(1.2))

        car = Car.objects.filter(
            Q(price__gt=2000000) | Q(year__lt=2020)
        )
        serializer = CarSerializer(car, many=True)
        return Response(serializer.data)



# Func() is used to call database-level functions such as UPPER, LOWER, ROUND, LENGTH, ABS, etc
class CarFuncView(APIView):
    def get(self, request):
        cars = Car.objects.annotate(
            model_upper=Func(
                F('model'),
                function='UPPER'
            ),
            rounded_price=Func(
                F('price'),
                Value(0),
                function='ROUND',
                output_field=DecimalField(max_digits=10, decimal_places=0)
            )
        ).values('model', 'model_upper', 'price', 'rounded_price')

        return Response(cars)


# Subquery() is used to embed one query inside another query, similar to a nested SQL subquery.
class CarSubqueryView(APIView):
    def get(self, request):
        avg_price_subquery = (
            Car.objects
            .filter(model=OuterRef('model')) # OuterRef references a field from the outer query inside the subquery
            .values('model')
            .annotate(avg_price=Avg('price'))
            .values('avg_price')
        )

        cars = Car.objects.annotate(
            model_avg_price=Subquery(
                avg_price_subquery,
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).values('model', 'price', 'model_avg_price')

        return Response(cars)