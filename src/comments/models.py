from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.urlresolvers import reverse

#from posts.models import Post

# Create your models here.

class CommentManager(models.Manager):
	def all(self):
		qs = super(CommentManager,self).filter(parent=None)
		return qs

	def filter_by_instance(self,instance):
		#instance.__class__ = class of the instance so if instance is Post it returns the Post class
		content_type = ContentType.objects.get_for_model(instance.__class__)
		obj_id = instance.id
		qs = super(CommentManager, self).filter(content_type=content_type, object_id=obj_id).filter(parent=None)	
		return qs

	# you wont need create_by_model_type if you used my other_solution 
	def create_by_model_type(self,model_type,slug,content,user,parent_obj=None):
		model_qs = ContentType.objects.filter(model=model_type)
		if model_qs.exists():
			SomeModel = model_qs.first().model_class()#Post model
			obj_qs = SomeModel.objects.filter(slug=slug)#one post object in array
			if obj_qs.exists() and obj_qs.count() ==1:
				instance = self.model()#Comment model
				instance.content =content
				instance.user= user
				instance.content_type = model_qs.first()#content type=post
				instance.object_id = obj_qs.first().id
				if parent_obj:
					instance.parent = parent_obj
				instance.save()
				return instance
		return None			 
			


class Comment(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,default=1)
	#post = models.ForeignKey(Post)
	
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)#post model
	object_id = models.PositiveIntegerField() #post id or any other object id
	content_object = GenericForeignKey('content_type', 'object_id')#post instance
	parent = models.ForeignKey("self", null=True, blank=True)

	content = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)

	objects = CommentManager()

	class Meta:
		ordering = ['-timestamp']

	def __unicode__(self):
		return str(self.user.username)

	def get_absolute_url(self):
		return reverse("comments:thread",kwargs={"id":self.id})	

	def get_delete_url(self):
		return reverse("comments:delete",kwargs={"id":self.id})		

	def children(self):#replies
		return Comment.objects.filter(parent=self)#parent=parent comment instance

	@property
	def is_parent(self):
		if self.parent is not None:#if comment has parent
			return False # it is a child(not parent)
		return True	#it is parent