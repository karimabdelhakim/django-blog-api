from django.db.models import Q
from rest_framework.filters import ( SearchFilter, OrderingFilter)
from rest_framework.generics import (ListAPIView, RetrieveAPIView,
	UpdateAPIView,DestroyAPIView,CreateAPIView,RetrieveUpdateAPIView)

from rest_framework.permissions import (AllowAny,IsAuthenticated,
	IsAdminUser,IsAuthenticatedOrReadOnly)
from .permissions import IsOwnerOrReadOnly,IsOwner
from posts.models import Post
from .serializers import (PostListSerializer, PostDetailSerializer, 
	PostCreateUpdateSerializer)
from .pagination import PostLimitOffsetPagination,PostPageNumberPagination

class PostCreateAPIView(CreateAPIView):
	queryset = Post.objects.all()
	serializer_class = PostCreateUpdateSerializer
	permission_classes = [IsAuthenticated]
#IsAuthenticated
#authuser can create and not read
#user can do nothing
	def perform_create(self, serializer):
		serializer.save(user=self.request.user)
		

class PostDetailAPIView(RetrieveAPIView):
	queryset = Post.objects.all()
	#permission_classes = [AllowAny]#default=AllowAny
	serializer_class = PostDetailSerializer
	lookup_field = 'slug'
	#lookup_url_kwarg = "abc" #just a name can be used in urls.py as <abc> instead of <slug>

class PostUpdateAPIView(RetrieveUpdateAPIView):
	queryset = Post.objects.all()
	serializer_class = PostCreateUpdateSerializer
	lookup_field = 'slug'
	permission_classes = [IsAuthenticated,IsOwner]
#IsAuthenticated (authuser can do any ,not auth-user can do nothing)       
	                 		
	def perform_update(self, serializer):#i don't think this maters in the update because user is already saved and we don't need to change him
		serializer.save(user=self.request.user)
	
class PostDeleteAPIView(DestroyAPIView):
	queryset = Post.objects.all()
	serializer_class = PostDetailSerializer
	lookup_field = 'slug'
	permission_classes = [IsAuthenticated,IsOwner]

class PostListAPIView(ListAPIView):
	serializer_class = PostListSerializer
	#permission_classes = [AllowAny]#default
	filter_backends = [SearchFilter,OrderingFilter]
	search_fields = ['title','content','user__first_name']
	pagination_class = PostPageNumberPagination#PostLimitOffsetPagination

	def get_queryset(self,*args,**kwargs):
		queryset_list = Post.objects.all()
		query = self.request.GET.get('q')
		if query:
			queryset_list= queryset_list.filter(
				Q(title__icontains=query) |
				Q(content__icontains=query) |
				Q(user__first_name__icontains=query) |
				Q(user__last_name__icontains=query)
				).distinct()
		return queryset_list
