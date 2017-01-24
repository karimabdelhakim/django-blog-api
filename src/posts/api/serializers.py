from rest_framework.serializers  import (ModelSerializer, 
HyperlinkedIdentityField, SerializerMethodField,HyperlinkedRelatedField)

from posts.models import Post

from comments.models import Comment
from comments.api.serializers import CommentSerializer
from accounts.api.serializers import UserDetailSerializer

####for me not in course
from django.contrib.contenttypes.models import ContentType 
from rest_framework.reverse import reverse
####for me not in course

class PostCreateUpdateSerializer(ModelSerializer):
	class Meta:
		model = Post
		fields = ['title','content','publish']

post_detail_url = HyperlinkedIdentityField(
		view_name='posts-api:detail',
		lookup_field='slug')

class PostDetailSerializer(ModelSerializer):
	url = post_detail_url
	user = UserDetailSerializer(read_only=True)
	image = SerializerMethodField()
	html = SerializerMethodField()
	comments = SerializerMethodField()
	####for me not in course
	comments_url = SerializerMethodField()
	####for me not in course
	
	class Meta:
		model = Post
		fields = ['url','id','user', 'title', 'slug',
		 'content','html','publish','image', 'comments','comments_url']

	def get_image(self,obj):
		try:
			image = obj.image.url
		except:
			image = None
		return image	
	def get_html(self,obj):
		return obj.get_markdown()			
	def get_comments(self,obj):
		c_qs = Comment.objects.filter_by_instance(obj)
		comments = CommentSerializer(c_qs, many=True).data
		return comments
	##########for me not in course############
	def get_comments_url(self,obj):
		content_type = ContentType.objects.get_for_model(obj).id
		url_q = "?id=%s&type=%s"%(obj.id,content_type)
		request = self.context.get('request')
		#return request.build_absolute_uri(reverse("comments-api:list")+url_q)
		return reverse("comments-api:list",request=request)+url_q
	##########for me not in course############


class PostListSerializer(ModelSerializer):
	url = post_detail_url
	user = UserDetailSerializer(read_only=True)
	class Meta:
		model = Post
		fields = ['url','user','title','content','publish']
	
	
