from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from api.serializers import AnalyzeTextSerializer
from api.llm_panel import run_panel

class AnalyzeTextView(APIView):
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get(self, request):
        return Response({
            "message": "Submit text via POST (JSON or form).",
            "example_json": {"text": "Teamwork matters because..."}
        })

    def post(self, request):
        serializer = AnalyzeTextSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        text = serializer.validated_data["text"]

        try:
            result = run_panel(text)
            return Response(result.model_dump(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Analysis failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
