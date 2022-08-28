from django.forms import ModelForm
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, decorators
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
        action = self.request.query_params.get('action', '').lower()
        if action not in ('publish', 'draft', 'delete', 'sold'):
            raise serializers.ValidationError({"action": "should be publish/draft/delete/sold"})
        old_state = self.get_object().state

        img_changes = self._update_images(serializer)
        if action == 'draft':
            return serializer.save(state=Good.PublishState.DRAFT)

        if action == 'delete':
            return serializer.save(state=Good.PublishState.DELETED)

        if action == 'sold':
            return serializer.save(state=Good.PublishState.SOLD)

        # else: action=='publish'
        if settings.MODERATION_AFTER_CHANGES:
            if old_state == Good.PublishState.PUBLISHED and not self._find_diffs(serializer) and not img_changes:
                return serializer.save(state=Good.PublishState.PUBLISHED)
            # all the other cases: from Draft to Publish or from Publish with changes to Publish
            return serializer.save(state=Good.PublishState.MODERATION)
        else:
            serializer.save(state=Good.PublishState.PUBLISHED)

    def perform_create(self, serializer):
        action = self.request.query_params.get('action', '').lower()
        if action not in ('publish', 'draft'):
            raise serializers.ValidationError({"action": "should be publish/draft"})

        if action == 'draft':
            return self._save_with_updating_images(serializer, Good.PublishState.DRAFT)
        if settings.MODERATION_AFTER_CHANGES:
            return self._save_with_updating_images(serializer, Good.PublishState.MODERATION)
        else:
            return self._save_with_updating_images(serializer, Good.PublishState.PUBLISHED)

    def _save_with_updating_images(self, serializer, state):
        if 'images' in serializer.validated_data:
            images_ids = serializer.validated_data['images']
            del serializer.validated_data['images']
        else:
            images_ids = []
        new_obj = serializer.save(user=self.request.user, state=state)
        self._set_good_for_new_images(new_obj.id, images_ids)
        return new_obj

    def _update_images(self, serializer):
        if 'images' not in serializer.validated_data:
            return False
        old_images = list(self.get_object().images.all())
        new_images = serializer.validated_data['images']
        del serializer.validated_data['images']
        changes = set(new_images) != set(map(lambda x: x.id, old_images))
        if not changes:
            return False

        id = self.get_object().id
        for image in old_images:
            if image.id not in new_images:
                image.delete()
        self._set_good_for_new_images(id, new_images)
        return True


    def _set_good_for_new_images(self, good_id, images_ids):
        for i in images_ids:
            image = UploadedImage.objects.get(pk=i)
            image.good = Good.objects.get(pk=good_id)
            image.save()

    def _find_diffs(self, serializer):
        for key, value in serializer.validated_data.items():
            if getattr(self.get_object(), key) != value:
                return True
        return False


class GoodImages(APIView):
    permission_classes = []
    def get(self, request, good_id):
        queryset = UploadedImage.objects.filter(good__id=good_id)
        serializer = UploadedImageSerializer(queryset, many=True)
        return Response({
            "media": serializer.data
        })


@csrf_exempt
def upload_image_view(request):
    class ImageForm(ModelForm):
        class Meta:
            model = UploadedImage
            fields = ('image',)

    if request.FILES:
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            inst = form.save()
            return JsonResponse({'success': True, 'name': inst.id})

    return JsonResponse({'success': False})

class GoodForm(ModelForm):
    class Meta:
        model = Good
        fields = '__all__'