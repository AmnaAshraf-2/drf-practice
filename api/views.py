from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Max, Min

from .serializers import CarSerializer
from .models import Car


# to get all the rows/instances of the model Cars use .all()
class CarGetView(APIView):
    def get(self, request):
        cars = Car.objects.all()
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)


# to get one instance at a time use .get() with pk or id
class CarGetOneView(APIView):
    def get(self, request, id):
        car = Car.objects.get(id=id)
        serializer = CarSerializer(car)
        return Response(serializer.data)


# Get all Toyotas using custom manager method
class CarGetToyotasView(APIView):
    def get(self, request):
        cars = Car.car.by_make("Toyota")  # using custom manager method
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)


# Get all cars older than 2010 using custom manager method
class CarGetOldCarsView(APIView):
    def get(self, request):
        cars = Car.car.older_than(2010)  # using custom manager method
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)



# use .get(id=pk) to display the item and .delete() to delete that item
class CarDeleteView(APIView):
    def get(self,request,pk):
        car = Car.objects.get(id=pk)
        serializer = CarSerializer(car)
        return Response(serializer.data)

    def delete(self, request, pk):
        car = Car.objects.get(id=pk)
        car.delete()
        return Response(
            {"message": "car deleted"},
            status=status.HTTP_204_NO_CONTENT
        )


# use .create() to create a new instance in db for model Car
# also this bypasses the serializers and manually create an instance
class CarCreateAPIView(APIView):
    def post(self,request):
        car = Car.objects.create(
            make=request.data['make'],
            model=request.data['model'],
            year=request.data['year']
        )
        return Response(CarSerializer(car).data, status=status.HTTP_201_CREATED)


#.get_or_create() adds a check that if the same instance exists it does not create a new instance
class CarGetOrCreateView(APIView):
    def post(self, request):
        car, created = Car.objects.get_or_create(
            make=request.data['make'],
            model=request.data['model'],
            defaults={'year': request.data['year']}
        )
        return Response({
            'created': created,
            'car': CarSerializer(car).data
        })


# .update_or_create() adds a check so that if a car already exists it updates the fields to new values
# and if not exist creates a new instance
class CarUpdateOrCreateView(APIView):
    def post(self, request):
        car, created = Car.objects.update_or_create(
            make=request.data['make'],
            model=request.data['model'],
            defaults={'year': request.data['year']}
        )
        return Response({
            'created': created,
            'car': CarSerializer(car).data
        })


# this automatically updates the year to 2025 of the cars having the name toyota
class CarUpdateView(APIView):
    def get(self, request, id):
        car = Car.objects.get(id=id)
        serializer = CarSerializer(car)
        return Response(serializer.data)

    def put(self, request, id):
        updated = Car.objects.filter(id=id).update(
            make=request.data['make'],
            model=request.data['model'],
            year=request.data['year']
        )
        return Response({"updated_rows": updated})


# to use .bulk_create() create a list and run a loop to get all the new added data and
class CarBulkCreateView(APIView):
    def post(self, request):
        cars = [
            Car(**item) for item in request.data
        ]
        Car.objects.bulk_create(cars)
        return Response({"message": "Cars created"}, status=201)


# .bulk_update() updates multiple instances alltogether. Here only the field year is updated
class CarBulkUpdateView(APIView):
    def put(self, request):
        cars = []
        for item in request.data:
            car = Car.objects.get(id=item['id'])
            car.year = item['year']
            cars.append(car)

        Car.objects.bulk_update(cars, ['year'])
        return Response({"message": "Cars updated"})


# to update different fields of multiple instances
class CarBulkPatchView(APIView):
    def patch(self, request):
        cars = []
        fields_to_update = set()

        for item in request.data:
            car = Car.objects.get(id=item['id'])

            for key, value in item.items():
                if key != 'id':
                    setattr(car, key, value)
                    fields_to_update.add(key)
            cars.append(car)

        if cars:
            Car.objects.bulk_update(cars, list(fields_to_update))

        return Response({"message": f"{len(cars)} cars updated"}, status=200)


# to get data in bulk use .in_bulk() in post method
# by posting ids the corresponding data is fetched
class CarInBulkView(APIView):
    def post(self, request):
        cars = Car.objects.in_bulk(request.data['ids'])
        return Response({
            key: CarSerializer(value).data
            for key, value in cars.items()
        })


# simply returns the number of instances
class CarCountView(APIView):
    def get(self, request):
        count = Car.objects.count()
        return Response({"count": count})


# to load large data in small chunks we use .iterator(chumk_size=)
class CarIteratorView(APIView):
    def get(self, request):
        data = []
        for car in Car.objects.iterator(chunk_size=2):
            data.append(CarSerializer(car).data)
        return Response(data)


# to get the instance of the latest field (year) e.g 2026
class CarLatestView(APIView):
    def get(self, request):
        car = Car.objects.latest('year')
        return Response(CarSerializer(car).data)


# to get the instance of the earliest field (year) e.g 1990 or any year lesser
class CarEarliestView(APIView):
    def get(self, request):
        car = Car.objects.earliest('year')
        return Response(CarSerializer(car).data)


# to get the first entry of the table in db use .first()
# to get the last entry of the table in db use .last()
class CarFirstLastView(APIView):
    def get(self, request):
        return Response({
            'first': CarSerializer(Car.objects.first()).data,
            'last': CarSerializer(Car.objects.last()).data
        })


# to get avg, minimum or maximum value we use .aggregate()
class CarAggregateView(APIView):
    def get(self, request):
        result = Car.objects.aggregate(
            avg_year=Avg('year'),
            max_year=Max('year'),
            min_year=Min('year')
        )
        return Response(result)


# it returns a bool value after checking if the instance containing the specified value exists
class CarExistsView(APIView):
    def get(self, request):
        exists = Car.objects.filter(make="Toyota").exists()
        return Response({"exists": exists})


# .explains the flow at which the instance is fetched from the db
class CarExplainView(APIView):
    def get(self, request):
        plan = Car.objects.filter(year__gte=2025).explain()
        return Response({"query_plan": plan})

