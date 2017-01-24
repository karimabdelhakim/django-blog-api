from django.db.models import Q
from rest_framework.filters import ( SearchFilter, OrderingFilter)
from rest_framework.mixins import DestroyModelMixin,UpdateModelMixin
from rest_framework.generics import (ListAPIView, RetrieveAPIView,
	UpdateAPIView,DestroyAPIView,CreateAPIView,RetrieveUpdateAPIView)
from rest_framework.permissions import (AllowAny,IsAuthenticated,
	IsAdminUser,IsAuthenticatedOrReadOnly)

from posts.api.permissions import IsOwnerOrReadOnly,IsOwner
from posts.api.pagination import PostLimitOffsetPagination,PostPageNumberPagination
####for my other_solution ######
#from rest_framework.serializers  import ValidationError
#from django.contrib.contenttypes.models import ContentType
################################
from comments.models import Comment
from .serializers import (CommentListSerializer,CommentDetailSerializer,
	#CommentCreateSerializer,#for my other_solution
	create_comment_serializer
	)


class CommentCreateAPIView(CreateAPIView):
	queryset = Comment.objects.all()
	
	permission_classes = [IsAuthenticated]
	def get_serializer_class(self):#this function mimic =>> serializer_class=CommentCreateSerializer
		model_type = self.request.GET.get("type")
		slug = self.request.GET.get("slug")
		parent_id = self.request.GET.get("parent_id",None)
		return create_comment_serializer(model_type=model_type, slug=slug, 
			parent_id=parent_id,user=self.request.user)


"""
#################other_solution############
#this is my solution and is much better(less complicated) than the appove solution
#the appove solution is the CommentCreateAPIView class
#used with some commented code in comments/api/serializers.py 
#use this after course is finished
class CommentCreateAPIView(CreateAPIView):
	queryset = Comment.objects.all() 
	serializer_class = CommentCreateSerializer
	permission_classes = [IsAuthenticated]
	
	def perform_create(self, serializer):
		model_type = self.request.GET.get("type")
		obj_id = self.request.GET.get("id")
		parent_id = self.request.GET.get("parent_id",None)
		
		content_type_qs = ContentType.objects.filter(model=model_type)
		if not content_type_qs.exists() or content_type_qs.count() !=1:
			raise ValidationError("This is not a valid content type")
		content_type = content_type_qs.first()

		if parent_id:
			parent_comment_qs = Comment.objects.filter(id=parent_id)
			if not parent_comment_qs.exists() or parent_comment_qs.count() !=1:
				raise ValidationError("This is not a valid parent id")
			parent_comment = parent_comment_qs.first()	
		else:
			parent_comment = None

		serializer.save(user=self.request.user,content_type=content_type,
			object_id=obj_id,parent=parent_comment)

#################other_solution############
"""

	
class CommentDetailAPIView(DestroyModelMixin,UpdateModelMixin,RetrieveAPIView):
	queryset = Comment.objects.filter(id__gte=0)
 	serializer_class = CommentDetailSerializer
 	permission_classes = [IsOwnerOrReadOnly]

 	def put(self,request,*args,**kwargs):
 		return self.update(request,*args,**kwargs)
 	def delete(self,request,*args,**kwargs):
 		return self.destroy(request,*args,**kwargs)	




class CommentListAPIView(ListAPIView):
	serializer_class = CommentListSerializer
	#permission_classes = [AllowAny] #default
	filter_backends = [SearchFilter,OrderingFilter]
	search_fields = ['content','user__first_name']
	pagination_class = PostPageNumberPagination#PostLimitOffsetPagination

	def get_queryset(self,*args,**kwargs):
		queryset_list = Comment.objects.filter(id__gte=0)
		query = self.request.GET.get('q')
		if query:
			queryset_list= queryset_list.filter(
				Q(content__icontains=query) |
				Q(user__first_name__icontains=query) |
				Q(user__last_name__icontains=query)
				).distinct()
		
		##################for me not in course###############
		#get comments of a specific post(used in PostDetailSerializer)
		obj_id = self.request.GET.get('id')
		cont_type = self.request.GET.get('type')
		if obj_id and cont_type:
			queryset_list= queryset_list.filter(content_type=cont_type,object_id=obj_id)		
		##################for me not in course###############	
		
		return queryset_list
