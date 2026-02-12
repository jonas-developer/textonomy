from rest_framework import serializers

class AnalyzeTextSerializer(serializers.Serializer):
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        style={"base_template": "textarea.html", "rows": 12},
        help_text="Paste the text you want to analyze."
    )
