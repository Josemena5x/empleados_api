# empleados/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Empleado
from .serializers import EmpleadoSerializer

# 🟢 Crear (POST) y Listar (GET todos)
class EmpleadoListCreateView(APIView):
    def get(self, request):
        empleados = Empleado.objects.all()
        serializer = EmpleadoSerializer(empleados, many=True)
        return Response(serializer.data)

    def post(self, request):
        empleado_data = request.data.get('empleado', request.data)
        serializer = EmpleadoSerializer(data=empleado_data)
        if serializer.is_valid():
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
