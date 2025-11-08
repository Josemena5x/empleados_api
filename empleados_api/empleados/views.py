# empleados/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Empleado
from .serializers import EmpleadoSerializer
import boto3
import csv
from io import StringIO
from django.conf import settings
from django.db import transaction

# 🟢 Crear (POST) y Listar (GET todos)
class EmpleadoListCreateView(APIView):
    def get(self, request):
        empleados = Empleado.objects.all()
        serializer = EmpleadoSerializer(empleados, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Soporte para crear uno o varios empleados en un mismo request.
        # Acepta estas formas:
        #  - JSON object para un solo empleado
        #  - JSON array para varios empleados
        #  - { "empleado": { ... } } para un solo empleado
        #  - { "empleados": [ {...}, {...} ] } para varios
        data = request.data
        if isinstance(data, dict) and 'empleados' in data:
            payload = data['empleados']
        elif isinstance(data, dict) and 'empleado' in data:
            payload = data['empleado']
        else:
            payload = data

        many = isinstance(payload, list)
        serializer = EmpleadoSerializer(data=payload, many=many)
        if serializer.is_valid():
            # Hacer la creación atómica: o se crean todos o ninguno
            with transaction.atomic():
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔵 Obtener, Actualizar y Eliminar por ID
class EmpleadoDetailView(APIView):
    def get_object(self, pk):
        try:
            return Empleado.objects.get(pk=pk)
        except Empleado.DoesNotExist:
            return None

    def get(self, request, pk):
        empleado = self.get_object(pk)
        if not empleado:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpleadoSerializer(empleado)
        return Response(serializer.data)

    def put(self, request, pk):
        empleado = self.get_object(pk)
        if not empleado:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        empleado_data = request.data.get('empleado', request.data)
        serializer = EmpleadoSerializer(empleado, data=empleado_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        empleado = self.get_object(pk)
        if not empleado:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        empleado.delete()
        return Response({'mensaje': 'Empleado eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)

class ExportarEmpleadosS3View(APIView):
    """
    Exporta todos los empleados a un archivo CSV en un bucket S3.
    Requiere que la instancia EC2 tenga un rol IAM con permisos de S3.
    """

    def post(self, request):
        try:
            empleados = Empleado.objects.all().values()

            if not empleados:
                return Response({'mensaje': 'No hay empleados para exportar'}, status=status.HTTP_200_OK)

            # Crear CSV en memoria
            csv_buffer = StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=empleados[0].keys())
            writer.writeheader()
            writer.writerows(empleados)

            # Cliente S3 (usa IAM Role si está configurado)
            s3 = boto3.client('s3')
            bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'proyectocpn')

            s3.put_object(
                Bucket=bucket_name,
                Key='empleados/empleados.csv',
                Body=csv_buffer.getvalue()
            )

            return Response({'mensaje': f'Archivo exportado correctamente a S3 ({bucket_name})'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)