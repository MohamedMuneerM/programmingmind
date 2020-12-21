from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.urls import reverse
# from django.contrib.auth import get_user_model
from django.db import models
from PIL import Image,ExifTags
from itertools import chain
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.files.storage import default_storage as storage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
# from image_cropping import ImageRatioField
# Create your models here.




class Connect(models.Model):
	youtube = models.URLField(max_length=2083)
	instagram = models.URLField(max_length=2083)
	github = models.URLField(max_length=2083)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return 'Social Media Links'
	



class Suggetions(models.Model):
	title = models.CharField(max_length=500)
	content = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)



class AboutPage(models.Model):
	content = models.TextField()
	updated = models.DateTimeField(auto_now=True) 

class Test(models.Model):
	title = models.CharField(max_length=300) 


class CommentManager(models.Manager):
	def all(self):
		qs = super(CommentManager, self).filter(parent=None)
		return qs

	def filter_by_instance(self, instance):
		content_type = ContentType.objects.get_for_model(instance.__class__)
		obj_id = instance.id
		qs = super(CommentManager, self).filter(content_type=content_type, object_id= obj_id).filter(parent=None)
		return qs


class BlogCategory(models.Model):
	title = models.CharField(max_length=300)
	slug = models.SlugField(max_length=300)

	def __str__(self):
		return self.title

class Topic(models.Model):
	title = models.CharField(max_length=300)
	slug = models.SlugField(max_length=300)
	image = models.ImageField(upload_to='images',null=True,blank=True)


	@property
	def get_absolute_url(self):
		return reverse('category',kwargs={
			'category':self.slug
			})


	@property
	def related_results(self):
		instance = self
		tutorials = instance.tutorialseries_set.all()
		posts = instance.blogpost_set.all()

		results  = list(chain(tutorials,posts))
		return results

	@property
	def get_photo_url(self):
		if self.image and hasattr(self.image, 'url'):
			return self.image.url
		else:
			return "https://res.cloudinary.com/munokitchen/image/upload/v1608445363/default-image_rk0yni.jpg"



	def __str__(self):
		return self.title




class TutorialSeries(models.Model):
	title = models.CharField(max_length=300)
	topic = models.ManyToManyField(Topic)
	date_published = models.DateTimeField(auto_now_add=True)
	image = models.ImageField(upload_to='images',null=True,blank=True)
	summary = models.TextField(blank=True,null=True)
	slug = models.SlugField(max_length=300)
	is_featured = models.BooleanField(default=False)
	view_count = models.IntegerField(default=0)


	def __str__(self):
		return self.title


	def get_absolute_url(self):
		return reverse('tutorial_detail',kwargs={
			'series_name':self.slug,
			'tutorial':self.tutorial_set.filter(category__slug=self.slug).first().slug,
			})


	@property
	def get_photo_url(self):
		if self.image and hasattr(self.image, 'url'):
			return self.image.url
		else:
			return "https://res.cloudinary.com/munokitchen/image/upload/v1608445363/default-image_rk0yni.jpg"




class Tutorial(models.Model):
	title = models.CharField(max_length=300)
	summary = models.TextField(blank=True,null=True) 
	part_num = models.PositiveIntegerField(null=True,blank=True)
	category = models.ForeignKey(TutorialSeries,null=True,blank=True,on_delete=models.SET_NULL)
	youtube_link = models.URLField(max_length=2083,blank=True,null=True)
	date_published = models.DateTimeField(auto_now_add=True)
	slug = models.SlugField(max_length=300)
	content = models.TextField()
	view_count = models.IntegerField(default=0)


	def __str__(self):
		return self.title
	

	def get_absolute_url(self):
		return reverse('tutorial_detail',kwargs={
			'series_name':self.category.slug,
			'tutorial':self.slug
			})

	@property
	def has_yt_link(self):
		if self.youtube_link:
			return True
		return False

	@property
	def next(self):
		instance = self
		category = instance.category
		# next_tutorial = Tutorial.objects.filter(id__gt=instance.id).order_by('id').first() 
		# next_tutorial  = Tutorial.objects.get(category__slug=instance.category).get_next_by_date_published()
		next_tutorial = category.tutorial_set.filter(part_num__gt=instance.part_num).order_by('part_num').first()
		# next_tutorial = category.tutorial_set.get(id=instance.id).get_next_by_date_published()
		return next_tutorial

	@property
	def last(self):
		instance = self
		category = instance.category
		last = category.tutorial_set.all().order_by('part_num').last()
		return last
	@property
	def is_end(self):
		if self.part_num == self.last.part_num:
			return True
		return False 
	


	@property
	def comments(self):
		instance = self
		qs = Comment.objects.filter_by_instance(instance)
		return qs



	def __str__(self):
		return self.title



class BlogPost(models.Model):
	title = models.CharField(max_length=300)
	summary = models.TextField(blank=True,null=True)
	category = models.ForeignKey(BlogCategory,null=True,on_delete=models.SET_NULL)
	topic = models.ManyToManyField(Topic)
	content = models.TextField()
	youtube_link = models.URLField(max_length=2083,blank=True,null=True)
	image = models.ImageField(upload_to='images',null=True,blank=True)
	date_published = models.DateTimeField(auto_now_add=True)
	slug = models.SlugField(max_length=300)
	view_count = models.IntegerField(default=0)
	is_featured = models.BooleanField(default=False)


	def __str__(self):
		return self.title

		

	def get_absolute_url(self):
		return reverse('blogpost',kwargs={
			'blogpost':self.slug,
			})

	@property
	def has_yt_link(self):
		if self.youtube_link:
			return True
		return False

	@property
	def get_photo_url(self):
		if self.image and hasattr(self.image, 'url'):
			return self.image.url
		else:
			return "https://res.cloudinary.com/munokitchen/image/upload/v1608445363/default-image_rk0yni.jpg"


	@property
	def comments(self):
		instance = self
		qs = Comment.objects.filter_by_instance(instance)
		return qs








class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		user = self.model(
			email=self.normalize_email(email),
			username=username,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			username=username,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


# def get_profile_image_filepath(self, filename):
# 	return 'profile_images/' + str(self.pk) + '/profile_image.png'

# def get_default_profile_image():
# 	return "codingwithmitch/default_profile_image.png"


class Account(AbstractBaseUser):
	email 					= models.EmailField(verbose_name="email", max_length=60, unique=True)
	username 				= models.CharField(max_length=30, unique=True)
	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin				= models.BooleanField(default=False)
	is_active				= models.BooleanField(default=True)
	is_staff				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)
	# profile_image			= models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True, blank=True, default=get_default_profile_image)
	# hide_email				= models.BooleanField(default=True)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	objects = MyAccountManager()

	def __str__(self):
		return self.username

	# def get_profile_image_filename(self):
		# return str(self.profile_image)[str(self.profile_image).index('profile_images/' + str(self.pk) + "/"):]

	# For checking permissions. to keep it simple all admin have ALL permissons
	def has_perm(self, perm, obj=None):
		return self.is_admin

	# Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
	def has_module_perms(self, app_label):
		return True


# User = get_user_model() 


class User_Agreements(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	want_newsletter = models.BooleanField(default=False)
	is_agreed_terms_and_conditions = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.user.username} agreements'


class NewsLetter(models.Model):
	user = models.CharField(max_length=599)
	email = models.EmailField()

	def __str__(self):
		return self.user



class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	image = models.ImageField(default='https://res.cloudinary.com/munokitchen/image/upload/v1606644051/default_image_txvds7.png',upload_to='profile_pics')
	# cropping = ImageRatioField('image', '430x360')
	def __str__(self):
		return f'{self.user.username} Profile'


	@property
	def get_photo_url(self):
		if self.image and hasattr(self.image, 'url'):
			return self.image.url
		else:
			return "https://res.cloudinary.com/munokitchen/image/upload/v1606644051/default_image_txvds7.png"

	def get_rotation_code(self,img):

		if not hasattr(img, '_getexif') or img._getexif() is None:
			return None

		for code, name in ExifTags.TAGS.items():
			if name == 'Orientation':
				orientation_code = code
				break
		else:
			raise Exception('Cannot get orientation code from library.')

		return img._getexif().get(orientation_code, None)


	def rotate_image(self,img, rotation_code):
		"""
		Returns rotated image file.

		img: PIL.Image file.
		rotation_code: is rotation code retrieved from get_rotation_code.
		"""
		if rotation_code == 1:
			return img
		if rotation_code == 3:
			img = img.transpose(Image.ROTATE_180)
		elif rotation_code == 6:
			img = img.transpose(Image.ROTATE_270)
		elif rotation_code == 8:
			img = img.transpose(Image.ROTATE_90)
		else:
			pass
		return img


	def save(self, *args, **kwargs):
		imageTemproary = Image.open(self.image)
		rotation_code = self.get_rotation_code(imageTemproary)
		if rotation_code is not None:
			imageTemproary = self.rotate_image(imageTemproary, rotation_code)
		outputIoStream = BytesIO()
		imageTemproaryResized = imageTemproary.resize( (300,300) ) 
		imageTemproaryResized.save(outputIoStream , format='PNG', quality=100)
		outputIoStream.seek(0)
		self.image = InMemoryUploadedFile(outputIoStream,'ImageField', "%s.jpg" %self.image.name.split('.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
		try:
			super(Profile, self).save(*args, **kwargs)
		except Exception as e:
			pass
	# def save(self):
	#     super().save()

	#     img = Image.open(self.image.name)

	#     if img.height > 300 or img.width > 300:
	#         output_size = (300, 300)
	#         img.thumbnail(output_size)
	#         fh = storage.open(self.image.name, "w")
	#         format_ = 'png'
	#         img.save(fh,format_)
	#         # img.save(self.image.name)
	#         fh.close()




class Comment(models.Model):
	user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')
	parent      = models.ForeignKey("self", null=True, blank=True,on_delete=models.CASCADE)

	content     = models.TextField()
	timestamp   = models.DateTimeField(auto_now_add=True)

	objects = CommentManager()

	class Meta:
		ordering = ['-timestamp']


	def __str__(self):
		return str(self.user.username)

	def children(self): #replies
		return Comment.objects.filter(parent=self).order_by('timestamp')


	def get_delete_url(self):
		return reverse("post-delete", kwargs={"pk": self.id})

	@property
	def is_children(self):
		if self.parent is not None:
			return True
		return False

	@property
	def is_parent(self):
		if self.parent is not None:
			return False
		return True

class Notification_Manual(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	sender = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='send',null=True,blank=True,on_delete=models.CASCADE)
	post_url = models.CharField(max_length=1000,null=True,blank=True)
	content = models.TextField()

