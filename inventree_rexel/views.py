from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView

from .serializers import RexelRequestSerializer
from .helpers import RexelHelper


class RexelView(APIView):
    """
    API-endpoint om onderdelen van Rexel te importeren.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = RexelRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rexelhelper = RexelHelper()
        processed_data = rexelhelper.process_rexel_data(serializer.validated_data)

        return Response(processed_data, status=status.HTTP_200_OK)
