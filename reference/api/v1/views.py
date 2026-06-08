import json

from django.http import JsonResponse
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from reference.api.v1.serializers import ReferenceSerializer
from reference.data_utils import get_reference
from reference.models import Reference, ReferenceStatus


class ReferenceViewSet(
    GenericViewSet,
    CreateModelMixin
):
    serializer_class = ReferenceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "post",
    ]

    def create(self, request, *args, **kwargs):
        return self.api_reference(request)

    def api_reference(self, request):
        try:
            data = json.loads(request.body)
            post_reference = data.get("reference")
            post_type = data.get("type")

            try:
                reference = Reference.objects.get(mixed_citation=post_reference)

            except Reference.DoesNotExist:
                new_reference = Reference.objects.create(
                    mixed_citation=post_reference,
                    status=ReferenceStatus.CREATING,
                    creator=self.request.user,
                )

                get_reference(new_reference.id)
                reference = Reference.objects.get(mixed_citation=post_reference)

            if post_type == "xml":
                reference_data = reference.element_citation.first().marked_xml
            else:
                reference_data = reference.element_citation.first().marked

            response_data = {
                "message": f"reference: {reference_data}",
            }
        except json.JSONDecodeError:
            response_data = {"error": "Error processing"}

        return JsonResponse(response_data)
