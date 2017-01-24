from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
	#owner can do any thing
    #not auth and auth(not owner) users can only read
	message = 'You must be the owner of this object'
		
	def has_object_permission(self, request, view, obj):
		if request.method in SAFE_METHODS:
			return True
		return obj.user == request.user

class IsOwner(BasePermission):
	#only owner can do any thing
    #not auth and auth(not owner) users can do nothing
	message = 'You must be the owner of this object'
		
	def has_object_permission(self, request, view, obj):
		return obj.user == request.user


		