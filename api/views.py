from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Max, Min

from .serializers import CarSerializer
from .models import Car


class CarListView(generics.ListAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

class CarGetView(APIView):
    def get(self, request):
        cars = Car.objects.all()
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)



class CarGetOneView(APIView):
    def get(self, request, id):
        car = Car.objects.get(id=id)
        serializer = CarSerializer(car)
        return Response(serializer.data)

class CarRetrieveView(generics.RetrieveAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer



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




class CarCreateView(generics.CreateAPIView):
   queryset = Car.objects.all()
   serializer_class = CarSerializer

class CarCreateAPIView(APIView):
    def post(self,request):
        car = Car.objects.create(
            make=request.data['make'],
            model=request.data['model'],
            year=request.data['year']
        )
        return Response(CarSerializer(car).data, status=status.HTTP_201_CREATED)

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

class CarUpdateView(APIView):
    def get(self,request):
        car = Car.objects.filter(make="Toyota")
        serializer = CarSerializer(car, many=True)
        return Response(serializer.data)

    def put(self, request):
        updated = Car.objects.filter(make="Toyota").update(year=2025)
        return Response({"updated_rows": updated})




class CarBulkCreateView(APIView):
    def post(self, request):
        cars = [
            Car(**item) for item in request.data
        ]
        Car.objects.bulk_create(cars)
        return Response({"message": "Cars created"}, status=201)

class CarBulkUpdateView(APIView):
    def put(self, request):
        cars = []
        for item in request.data:
            car = Car.objects.get(id=item['id'])
            car.year = item['year']
            cars.append(car)

        Car.objects.bulk_update(cars, ['year'])
        return Response({"message": "Cars updated"})

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

class CarInBulkView(APIView):
    def post(self, request):
        cars = Car.objects.in_bulk(request.data['ids'])
        return Response({
            key: CarSerializer(value).data
            for key, value in cars.items()
        })





class CarCountView(APIView):
    def get(self, request):
        count = Car.objects.count()
        return Response({"count": count})


class CarIteratorView(APIView):
    def get(self, request):
        data = []
        for car in Car.objects.iterator(chunk_size=2):
            data.append(CarSerializer(car).data)
        return Response(data)

class CarLatestView(APIView):
    def get(self, request):
        car = Car.objects.latest('year')
        return Response(CarSerializer(car).data)


class CarEarliestView(APIView):
    def get(self, request):
        car = Car.objects.earliest('year')
        return Response(CarSerializer(car).data)

class CarFirstLastView(APIView):
    def get(self, request):
        return Response({
            'first': CarSerializer(Car.objects.first()).data,
            'last': CarSerializer(Car.objects.last()).data
        })


class CarAggregateView(APIView):
    def get(self, request):
        result = Car.objects.aggregate(
            avg_year=Avg('year'),
            max_year=Max('year'),
            min_year=Min('year')
        )
        return Response(result)

class CarExistsView(APIView):
    def get(self, request):
        exists = Car.objects.filter(make="Toyota").exists()
        return Response({"exists": exists})




class CarExplainView(APIView):
    def get(self, request):
        plan = Car.objects.filter(year__gte=2025).explain()
        return Response({"query_plan": plan})
