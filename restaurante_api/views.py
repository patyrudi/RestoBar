class ConsumoViewSet(viewsets.ModelViewSet):
    queryset = Consumo.objects.all()
    serializer_class = ConsumoSerializer

    def create(self, request, *args, **kwargs):
        idmesa = request.data.get("idmesa")

        if Consumo.objects.filter(idmesa=idmesa, estado=1).exists():
            raise ValidationError({"error": "La mesa ya tiene un consumo abierto."})

        # Si no existe, proceder con la creación del consumo
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'], url_path=r'mesa/(?P<idmesa>\d+)/crear')
    def abrir_consumo(self, request, idmesa=None):
        """
        Abre un consumo en la mesa especificada.
        Valida que no haya un consumo abierto y recibe los datos del cliente.
        """
        # Validar que la mesa no tiene un consumo abierto (estado 1)
        if Consumo.objects.filter(idmesa=idmesa, estado=1).exists():
            raise ValidationError({"error": "La mesa ya tiene un consumo abierto."})

        # Obtener o crear el cliente
        ciCliente = request.data.get("ciCliente")
        nombre = request.data.get("nombre")

        if ciCliente:
            cliente, created = Cliente.objects.get_or_create(ciCliente=ciCliente, defaults={"nombre": nombre})
        else:
            return Response({"error": "El campo ciCliente es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el consumo para la mesa con el cliente
        try:
            mesa = Mesa.objects.get(idmesa=idmesa)  # Verificar si la mesa existe
        except Mesa.DoesNotExist:
            return Response({"error": "Mesa no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        consumo = Consumo.objects.create(
            idmesa=mesa,
            idcliente=cliente,
        )

        serializer = ConsumoSerializer(consumo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)