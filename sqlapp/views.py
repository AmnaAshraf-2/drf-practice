from django.shortcuts import render
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response


class CarGetView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, make, model, year FROM api_car")
            rows = cursor.fetchall()

        data = [
            {
                "id": r[0],
                "make": r[1],
                "model": r[2],
                "year": r[3]
            }
            for r in rows
        ]
        return Response(data)



class CarOneView(APIView):
    def get(self, request, id):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id, make, model, year FROM api_car WHERE id = %s',
                [id]
            )

            row = cursor.fetchone()

        if not row:
            return Response({"detail": "Not found"}, status=404)

        return Response({
            "id": row[0],
            "make": row[1],
            "model": row[2],
            "year": row[3],
        })

class CarDeleteView(APIView):

    def get_car(self, id):
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id, make, model, year FROM api_car WHERE id = %s',
                [id]
            )
            return cursor.fetchone()

    def get(self, request, id):
        row = self.get_car(id)

        if not row:
            return Response({"detail": "Not found"}, status=404)

        return Response({
            "id": row[0],
            "make": row[1],
            "model": row[2],
            "year": row[3],
        })

    def delete(self, request, id):
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM api_car WHERE id = %s', [id])
            if cursor.rowcount == 0:
                return Response({"detail": "Not found"}, status=404)

        return Response(status=204)


class CarCreateAPIView(APIView):
    def post(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO api_car (make, model, year)
                VALUES (%s, %s, %s)
                RETURNING id, make, model, year
                """,
                [
                    request.data['make'],
                    request.data['model'],
                    request.data['year']
                ]
            )
            row = cursor.fetchone()

        return Response({
            "id": row[0],
            "make": row[1],
            "model": row[2],
            "year": row[3]
        }, status=201)


class CarUpdateAPIView(APIView):
    def put(self, request, id):
        with connection.cursor() as cursor:
            cursor.execute('UPDATE api_car SET make = %s, model = %s, year = %s WHERE id = %s',
                [
                 request.data['make'],
                 request.data['model'],
                 request.data['year']
                 ]
                           )

            if cursor.rowcount == 0:
                return Response({"detail": "Not found"}, status=404)

            return Response({
                "id": cursor.rowcount,
                "make": cursor.rowcount,
                "model": cursor.rowcount,
                "year": cursor.rowcount
            })

class CarGetOrCreateView(APIView):
    def post(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, make, model, year FROM api_car WHERE make=%s AND model=%s",
                [
                    request.data['make'],
                    request.data['model']
                ]
            )
            row = cursor.fetchone()

            if row:
                created = False
            else:
                cursor.execute(
                    """
                    INSERT INTO api_car (make, model, year)
                    VALUES (%s, %s, %s)
                    RETURNING id, make, model, year
                    """,
                    [
                        request.data['make'],
                        request.data['model'],
                        request.data['year']
                    ]
                )
                row = cursor.fetchone()
                created = True

        return Response({"created": created, "car": {
            "id": row[0],
            "make": row[1],
            "model": row[2],
            "year": row[3]
        }})

class CarUpdateOrCreateView(APIView):
    def post(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM api_car WHERE make=%s AND model=%s",
                [
                    request.data['make'],
                    request.data['model']
                ]
            )
            row = cursor.fetchone()

            if row:
                cursor.execute(
                    "UPDATE api_car SET year=%s WHERE id=%s",
                    [
                        request.data['year'],
                        row[0]
                    ]
                )
                created = False
            else:
                cursor.execute(
                    """
                    INSERT INTO api_car (make, model, year)
                    VALUES (%s, %s, %s)
                    """,
                    [
                        request.data['make'],
                        request.data['model'],
                        request.data['year']
                    ]
                )
                created = True

        return Response({"created": created})


class CarBulkCreateView(APIView):
    def post(self, request):
        with connection.cursor() as cursor:
            for item in request.data:
                cursor.execute(
                    "INSERT INTO api_car (make, model, year) VALUES (%s, %s, %s)",
                    [item['make'], item['model'], item['year']]
                )
        return Response({"message": "Cars created"}, status=201)


class CarCountView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM api_car")
            count = cursor.fetchone()[0]

        return Response({"count": count})

class CarExistsView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM api_car WHERE make=%s)",
                ["Toyota"]
            )
            exists = cursor.fetchone()[0]

        return Response({"exists": exists})


class CarAggregateView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT AVG(year), MAX(year), MIN(year) FROM api_car"
            )
            avg_, max_, min_ = cursor.fetchone()

        return Response({
            "avg_year": avg_,
            "max_year": max_,
            "min_year": min_
        })


class CarExplainView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute(
                "EXPLAIN ANALYZE SELECT * FROM api_car WHERE year >= %s",
                [2020]
            )
            plan = cursor.fetchall()

        return Response({"query_plan": plan})


class CarLatestView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, make, model, year
                FROM api_car
                ORDER BY year DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

        if not row:
            return Response({"detail": "No car found"}, status=404)

        return Response({
            "id": row[0],
            "name": row[1],
            "year": row[2],
            "price": row[3],
        })


class CarEarliestView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, make, model, year
                FROM api_car
                ORDER BY year ASC
                LIMIT 1
            """)
            row = cursor.fetchone()

        if not row:
            return Response({"detail": "No car found"}, status=404)

        return Response({
            "id": row[0],
            "name": row[1],
            "year": row[2],
            "price": row[3],
        })


class CarFirstLastView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM api_car ORDER BY id ASC LIMIT 1")
            first = cursor.fetchone()

            cursor.execute("SELECT * FROM api_car ORDER BY id DESC LIMIT 1")
            last = cursor.fetchone()

        return Response({
            "first": first,
            "last": last
        })
