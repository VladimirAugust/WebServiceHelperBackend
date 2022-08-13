from django.conf import settings
from django.http import Http404
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.utils.trees import serialize_tree
from .models import *
from .serializers import *


class CategoriesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        all_nodes = GoodCategory.objects.all()
        level1 = list(filter(lambda x: not x.parent, all_nodes))
        trees = []
        for root in level1:
            trees.append(serialize_tree(root, all_nodes, GoodCategorySerializer))

        return Response(trees)


class GoodsViewSet(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 GenericViewSet):

    serializer_class = GoodSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Good.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            good = Good.objects.filter(user=self.request.user).get(pk=kwargs['pk'])
        except Good.DoesNotExist:
            try:
                good = Good.objects.filter(state=Good.PublishState.PUBLISHED).get(pk=kwargs['pk'])
            except Good.DoesNotExist:
                raise Http404

        serializer = self.serializer_class(good)
        return Response(serializer.data)

    def perform_update(self, serializer):
        if settings.MODERATION_AFTER_CHANGES and self._find_diffs(serializer):
            serializer.save(state=Good.PublishState.MODERATION)
        else:
            serializer.save()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, state=Good.PublishState.MODERATION)

    def _find_diffs(self, serializer):
        for key, value in serializer.validated_data.items():
            if getattr(self.get_object(), key) != value:
                return True
        return False