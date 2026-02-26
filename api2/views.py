from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .serialisers import CarSerializer, OwnerSerializer
from .models import Car, Owner
from django.db.models import Count, Q
from django.db import transaction, connection


class OwnerCreateView(generics.CreateAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

class CarCreateView(generics.CreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

class CarListView(APIView):
    def get(self, request):
        cars = Car.objects.all()  # no select_related
        return Response(CarSerializer(cars, many=True).data)


class OwnerListView(APIView):
    def get(self, request):
        owners = Owner.objects.all()  # ❌ no prefetch
        return Response(OwnerSerializer(owners, many=True).data)

class CarFilterView(APIView):
    def get(self, request):
        cars = Car.objects.filter(year__lte=2020)
        return Response(CarSerializer(cars, many=True).data)


class CarExcludeView(APIView):
    def get(self, request):
        cars = Car.objects.exclude(make="Toyota")
        return Response(CarSerializer(cars, many=True).data)


class CarAnnotateView(APIView):
    def get(self, request):
        cars = Car.objects.values('make').annotate(total=Count('id'))
        return Response(cars)


class CarOrderByView(APIView):
    def get(self, request):
        cars = Car.objects.order_by('-year')
        return Response(CarSerializer(cars, many=True).data)


class CarReverseView(APIView):
    def get(self, request):
        cars = Car.objects.order_by('make').reverse()
        return Response(CarSerializer(cars, many=True).data)


class CarDistinctView(APIView):
    def get(self, request):
        cars = Car.objects.values('make').distinct()
        return Response(cars)


class CarValuesView(APIView):
    def get(self, request):
        cars = Car.objects.values('make', 'year')
        return Response(cars)


class CarValuesListView(APIView):
    def get(self, request):
        cars = Car.objects.values_list('make', flat=True)
        return Response(cars)


class CarNoneView(APIView):
    def get(self, request):
        cars = Car.objects.none()
        return Response(CarSerializer(cars, many=True).data)


class CarUnionView(APIView):
    def get(self, request):
        q1 = Car.objects.filter(year__gte=2020)
        q2 = Car.objects.filter(make="Honda")
        cars = q1.union(q2)
        return Response(CarSerializer(cars, many=True).data)


class CarIntersectionView(APIView):
    def get(self, request):
        q1 = Car.objects.filter(year__gte=2020)
        q2 = Car.objects.filter(make="Honda")
        cars = q1.intersection(q2)
        return Response(CarSerializer(cars, many=True).data)


class CarDifferenceView(APIView):
    def get(self, request):
        q1 = Car.objects.all()
        q2 = Car.objects.filter(make="Honda")
        cars = q1.difference(q2)
        return Response(CarSerializer(cars, many=True).data)


# used to optimize forward relation of entities
# the model containing the foriegn key
class CarSelectRelatedView(APIView):
    def get(self, request):
        cars = Car.objects.select_related('owner')
        return Response(CarSerializer(cars, many=True).data)


# used to optimize backward relation of entities
# the model that does not contain the foriegn key but django creates a reverse manager
class CarPrefetchView(APIView):
    def get(self, request):
        owners = Owner.objects.prefetch_related('car')
        return Response(OwnerSerializer(owners, many=True).data)


# do not load the fields specified  and if the serializer has more fields in it,
# it will run query for each field separately running more queries than normal
# best is to use a separate serializer
class CarDeferView(APIView):
    def get(self, request):
        cars = Car.objects.defer('make', 'year')
        return Response(CarSerializer(cars, many=True).data)


# loads only the fields specified  and if the serializer has more fields in it,
# it willrun query for each field separately running more queries than normal
# best is to use a separate serializer
class CarOnlyView(APIView):
    def get(self, request):
        cars = Car.objects.only('make', 'year')
        return Response(CarSerializer(cars, many=True).data)


#  when multiple databases are used
# right now only one db exist so .using() shows default behaviour as car.objects.all()
class CarUsingView(APIView):
    def get(self, request):
        cars = Car.objects.using('default').all()
        return Response(CarSerializer(cars, many=True).data)

# ---------
class CarLockView(APIView):
    def get(self, request):
        with transaction.atomic():
            car = Car.objects.select_for_update().first()
            return Response(CarSerializer(car).data)


class CarRawView(APIView):
    def get(self, request):
        cars = Car.objects.raw("SELECT * FROM api_car")
        return Response(CarSerializer(cars, many=True).data)


class CarAndView(APIView):
    def get(self, request):
        cars = Car.objects.filter(
            (Q(make="Honda") & Q(year__gte=2020))
        )
        return Response(CarSerializer(cars, many=True).data)


class CarOrView(APIView):
    def get(self, request):
        cars = Car.objects.filter(
            (Q(make="Honda") | Q(make="Toyota"))
        )
        return Response(CarSerializer(cars, many=True).data)

# -----------------------------------------



class OwnerCreateView(generics.CreateAPIView):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer

class CarCreateView(generics.CreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

class CarListSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT id, make, model, year, owner_id FROM api2_car')
            rows = cursor.fetchall()
        data = [
            {
                'id': r[0],
                'make': r[1],
                'model': r[2],
                'year': r[3],
                'owner_id': r[4],
                # 'owner_city': r[5]
            }for r in rows
        ]
        return Response(data)

class OwnerListSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT id, name, city FROM api2_owner')
            rows = cursor.fetchall()
        data = [
            {
                'id': r[0],
                'name': r[1],
                'city': r[2],
            } for r in rows
        ]
        return Response(data)


class CarFilterSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT make, model, year, owner_id FROM api2_car WHERE year = %s',[2020])
            row = cursor.fetchall()

            data=[
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': [4]
                }for r in row
            ]
            return Response(data)


class CarExcludeSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT id, make, model, year, owner_id FROM api2_car WHERE year != %s', [2020])
            row = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': [4]
                } for r in row
            ]
            return Response(data)


class CarAnnotateSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT make, COUNT(id) AS total
                FROM api_car
                GROUP BY make
            """)
            rows = cursor.fetchall()

        data = [
            {
                "make": r[0],
                "total": r[1],
            }
            for r in rows
        ]

        return Response(data)


class CarOrderBySQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT id, make, model, year, owner_id FROM api2_car ORDER  BY year ASC')
            row = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': [4]
                } for r in row
            ]
            return Response(data)


class CarReverseBySQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT id, make, model, year, owner_id FROM api2_car ORDER  BY year DESC)
            row = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': [4]
                } for r in row
            ]
            return Response(data)


class CarDistinctSQLView(APIView):
    def get(self, request):
       with connection.cursor() as cursor:
           cursor.execute('SELECT DISTINCT make FROM api2_car')
           rows = cursor.fetchall()

       return Response(r[0] for r in rows)


class CarValuesSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT make, year FROM api2_car'
            )
            rows = cursor.fetchall()

            data = [
                {
                    'make': r[0],
                    'year': r[1]
                } for r in rows
            ]
            return Response(data)



class CarValuesListSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT make, year FROM api2_car'
            )
            rows = cursor.fetchall()

        return Response(rows)



class CarUnionSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id, make, model, year, owner_id FROM api2_car WHERE year >= 2022
                UNION
                SELECT id, make, model, year, owner_id FROM api2_car WHERE make = 'Honda'
                '''
            )
            rows = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': r[4]
                } for r in rows
            ]
            return Response(data)



class CarIntersectionSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id, make, model, year, owner_id FROM api2_car WHERE year >= 2022
                INTERSECT
                SELECT id, make, model, year, owner_id FROM api2_car WHERE make = 'Honda'
                '''
            )
            rows = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': r[4]
                } for r in rows
            ]
            return Response(data)



class CarDifferenceSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id, make, model, year, owner_id FROM api2_car WHERE year >= 2022
                EXCEPT
                SELECT id, make, model, year, owner_id FROM api2_car WHERE make = 'Honda'
                '''
            )
            rows = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': r[4]
                } for r in rows
            ]
            return Response(data)


class CarSelectRelatedSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT c.id, c.make, c.model, c.year,
                       o.name, o.city
                FROM api2_car c
                INNER JOIN api2_owner o ON c.owner_id = o.id
                '''
            )
            rows = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_name': r[4],
                    'owner_city': r[5]
                } for r in rows
            ]
            return Response(data)


class OwnerPrefetchRelatedSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id, name, city FROM api2_owner'
            )
            owners = cursor.fetchall()

            cursor.execute(
                'SELECT id, make, model, year, owner_id FROM api2_car'
            )
            cars = cursor.fetchall()

        owner_map = {}
        for o in owners:
            owner_map[o[0]] = {
                'id': o[0],
                'name': o[1],
                'city': o[2],
                'cars': []
            }

        for c in cars:
            owner_map[c[4]]['cars'].append({
                'id': c[0],
                'make': c[1],
                'model': c[2],
                'year': c[3]
            })

        return Response(list(owner_map.values()))


class CarDeferSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id, make, model, year, owner_id FROM api2_car'
            )
            rows = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': r[4]
                } for r in rows
            ]
            return Response(data)

class CarOnlySQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id, make, year FROM api2_car'
            )
            rows = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'year': r[2]
                } for r in rows
            ]
            return Response(data)


class CarSelectForUpdateSQLView(APIView):
    def get(self, request):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT id, make, model, year, owner_id FROM api2_car FOR UPDATE'
                )
                row = cursor.fetchone()

                data = {
                    'id': row[0],
                    'make': row[1],
                    'model': row[2],
                    'year': row[3],
                    'owner_id': row[4]
                }
            return Response(data)



class CarAndSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id, make, model, year, owner_id
                FROM api2_car
                WHERE make = 'Honda' AND year >= 2022
                '''
            )
            rows = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': r[4]
                } for r in rows
            ]
            return Response(data)


class CarOrSQLView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT id, make, model, year, owner_id
                FROM api2_car
                WHERE make = 'Honda' OR year >= 2023
                '''
            )
            rows = cursor.fetchall()

            data = [
                {
                    'id': r[0],
                    'make': r[1],
                    'model': r[2],
                    'year': r[3],
                    'owner_id': r[4]
                } for r in rows
            ]
            return Response(data)

