import requests

from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin,PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404,redirect,reverse
from django.http import HttpResponse
from .forms import (
	UserRegisterForm,
	UserUpdateForm,
	ProfileUpdateForm,
	CommentForm,
	SuggestionForm,
)
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404
from django.contrib import messages
from itertools import chain
from django.conf import settings
from .models import (
	Tutorial,
	TutorialSeries,
	BlogPost,
	BlogCategory,
	Comment,
	AboutPage,
	Suggetions,
	Topic,
	Notification_Manual,
	Account,
	User_Agreements,
	NewsLetter,
	Connect,
)
from django.views.generic import (
	ListView,
	DetailView,
	CreateView,
	UpdateView,
	DeleteView,
	TemplateView,
)
from django.core.mail import mail_admins 



def error404(request,*args,**kwargs):
	data = {} 
	return render(request,'mysite/error404.html',data,status=404)

def error500(request,*args,**kwargs):
	data = {} 
	return render(request,'mysite/error500.html',data,status=500) 



class Notify_View(UserPassesTestMixin,ListView):
	model = Notification_Manual
	template_name = 'mysite/notify.html'
	context_object_name = 'notifications'
	ordering = ['-id']

	def test_func(self):
		try:
			is_admin = self.request.user.is_admin
		except:
			is_admin = None

		if not is_admin:
			return False
		return True
 




class SuggestionFormView(CreateView):
	model = Suggetions
	form_class = SuggestionForm
	template_name = 'mysite/snippets/suggestions.html'

	
	def post(self,request,*args,**kwargs):
		form = SuggestionForm(request.POST or None)
		if form.is_valid():
			recaptcha_response = request.POST.get('g-recaptcha-response')
			data = {
				'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
				'response': recaptcha_response
			}
			r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
			result = r.json()
			''' End reCAPTCHA validation '''
			if result['success']:
				instance = form.save()
				mail_admins(f'New suggestion({instance.title})',f'{instance.content}')
				messages.success(request, 'Your Suggestions will be taken seriously..Thank you for suggesting..')
			else:
				messages.warning(request, 'Invalid reCAPTCHA. Please try again.')
		else:
			messages.warning(request, 'Enter All fields..')
		return redirect('.')


class ConnectPage(TemplateView):
	model = Connect
	template_name = 'mysite/connect.html'


	def get_context_data(self,**kwargs):
		context = super().get_context_data(**kwargs)
		try:
			context['connections'] = Connect.objects.all().first()
		except:
			context['connections'] = Connect.objects.all()

		return context
			
	

class About_page(TemplateView):
	model = AboutPage
	template_name = 'mysite/about.html'
	context_object_name = 'about_age'


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		try:
			context['about_page'] = AboutPage.objects.all().first()
		except:
			context['about_page'] = AboutPage.objects.all()

		return context




class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Comment

	def get_object(self):
		try:
			return Comment.objects.get(pk=self.kwargs['pk'])
		except Exception as e:
			raise Http404
 
	
	def get_success_url(self):
		return self.request.POST.get('path', '/')

	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['previous'] = self.request.META.get('HTTP_REFERER')
		return context


	def test_func(self):
		comment = self.get_object()
		if str(self.request.user) == str(comment.user.username):
			return True
		return False



@login_required(login_url='login')
def profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST, instance=request.user)
		p_form = ProfileUpdateForm(request.POST,
								   request.FILES,
								   instance=request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			messages.success(request, f'Your account has been updated!')
			return redirect('account')

	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)

	context = {
		'u_form': u_form,
		'p_form': p_form
	}

	return render(request, 'mysite/account.html', context)



class HomePage(ListView):
	model = TutorialSeries
	template_name = 'mysite/home.html'
	context_object_name = 'tutorial_series'


	def get_context_data(self, **kwargs):

		context = super().get_context_data(**kwargs)
		tutorial_series = TutorialSeries.objects.all().order_by('-id')
		try:
			context['blog_posts'] = BlogPost.objects.all().order_by('-id')[5]
		except:
			context['blog_posts'] = BlogPost.objects.all().order_by('-id')

		# li = [series.tutorial_set.first() for series in tutorial_series ]
		# tutorials = zip(tutorial_series, li)

		context['tutorials'] = tutorial_series
		return context


class TutorialList(ListView):
	model = TutorialSeries
	template_name = 'mysite/Tutorial_lists.html'
	context_object_name = 'tutorial_series'
	ordering = ['-id']
	paginate_by = 15


class BlogPostList(ListView):
	model = BlogPost
	template_name = 'mysite/blogs.html'
	context_object_name = 'blogs'
	ordering = ['-id']
	paginate_by = 15


class TutorialDetailView(DetailView):
	model = Tutorial
	template_name = 'mysite/generic_tutorial_views.html'
	context_object_name = 'tutorials'

	def post(self,request,*args,**kwargs):
		 
		if not request.user.is_authenticated:
			messages.info(request, f'Kindly log in, in order to comment')
			return redirect('login')

		# tutorial = Tutorial.objects.get(slug=self.kwargs['tutorial'])
		tutorial = get_object_or_404(Tutorial, slug=self.kwargs['tutorial'])

		contenttype = ContentType.objects.get_for_model(Tutorial)
		obj_id = tutorial.id
		
		initial_data = {
			"content_type": contenttype,
			"object_id": obj_id,
		}

		form = CommentForm(self.request.POST ,initial=initial_data)

		if form.is_valid() and request.user.is_authenticated:
			c_type = form.cleaned_data.get("content_type")
			content_type = ContentType.objects.get_for_model(model=Tutorial)
			obj_id = form.cleaned_data.get('object_id')
			content_data = form.cleaned_data.get("content")
			parent_obj = None			

			try:
				parent_id = int(request.POST.get("parent_id"))
			except:
				parent_id = None


			if parent_id:
				parent_qs = Comment.objects.filter(id=parent_id).distinct()
				if parent_qs.exists() and parent_qs.count() == 1:
					parent_obj = parent_qs.first()
			new_comment,created= Comment.objects.get_or_create(
							user = self.request.user,
							content_type= content_type,
							object_id = obj_id,
							content = content_data,
							parent = parent_obj,
						)
			return redirect(tutorial.get_absolute_url())
		return redirect(tutorial.get_absolute_url())



	def get_object(self):
		self.series = get_object_or_404(TutorialSeries, slug=self.kwargs['series_name'])
		return self.series

	def get_context_data(self, **kwargs):

		context = super().get_context_data(**kwargs)
		tutorial = get_object_or_404(Tutorial, slug=self.kwargs['tutorial'])
		contenttype = ContentType.objects.get_for_model(tutorial.__class__)
		obj_id = tutorial.id
		comments= Comment.objects.filter(content_type=contenttype,object_id=obj_id)
		initial_data = {
			"content_type": contenttype,
			"object_id": obj_id,
		}
		form = CommentForm(self.request.POST or None, initial=initial_data)

		context['comments'] = tutorial.comments
		try:
			context['featured'] = TutorialSeries.objects.filter(is_featured=True).order_by('-date_published').exclude(slug=self.series.slug)[3]
		except:
			context['featured'] = TutorialSeries.objects.filter(is_featured=True).order_by('-date_published').exclude(slug=self.series.slug)
		
		context['form'] = form
		context['current_tutorial'] = self.series.tutorial_set.get(slug=self.kwargs['tutorial'])
		context['full_tutorials'] = self.series.tutorial_set.all().order_by('part_num')
		context['series_name'] = self.series
		return context



class BlogPostView(DetailView):
	model = BlogPost
	template_name = 'mysite/generic_post.html'
	context_object_name = 'blogpost'


	def get_object(self):
		self.posts = get_object_or_404(BlogPost, slug=self.kwargs['blogpost'])
		self.posts.view_count += 1
		self.posts.save()
		return self.posts

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		post_category = self.posts.category.slug 
		contenttype = ContentType.objects.get_for_model(self.posts.__class__)

		obj_id = self.posts.id
		comments= Comment.objects.filter(content_type=contenttype,object_id=obj_id)
		context['comments'] = self.posts.comments
		
		initial_data = {
		"content_type": contenttype,
		"object_id": obj_id,
		}
		form = CommentForm(self.request.POST or None, initial=initial_data)
		

		context['form'] = form
		context['post_slug'] = self.posts.slug 
		try:
			context['categories'] = Topic.objects.all().order_by('-id')[6]
		except:
			context['categories'] = Topic.objects.all().order_by('-id')	
		try:
			# add .exclude() for exluding self.post data i.e the post which the user is viewing
			context['similar_posts'] = BlogPost.objects.filter(category__slug=post_category).exclude(slug=self.posts.slug)[7]
		except:
			context['similar_posts'] = BlogPost.objects.filter(category__slug=post_category).exclude(slug=self.posts.slug)

		try:
			context['featured_posts'] = BlogPost.objects.filter(is_featured =True).exclude(slug=self.posts.slug).order_by('id')[7]
		except:
			context['featured_posts'] = BlogPost.objects.filter(is_featured =True).exclude(slug=self.posts.slug).order_by('id')

		try:
			context['trending_posts'] = BlogPost.objects.all().order_by('-view_count').exclude(slug=self.posts.slug)[7]

		except:
			context['trending_posts'] = BlogPost.objects.all().order_by('-view_count').exclude(slug=self.posts.slug)			

		return context 


	def post(self,request,*args,**kwargs):

		if not request.user.is_authenticated:
			messages.info(request, f'Kindly log in, in order to comment')
			return redirect('login')

		# posts_ = BlogPost.objects.get(slug=self.kwargs['blogpost'])
		posts_ = get_object_or_404(BlogPost, slug=self.kwargs['blogpost'])
		contenttype = ContentType.objects.get_for_model(BlogPost)
		obj_id = posts_.id
		
		initial_data = {
			"content_type": contenttype,
			"object_id": obj_id,
		}

		form = CommentForm(self.request.POST ,initial=initial_data)

		if form.is_valid() and request.user.is_authenticated:
			c_type = form.cleaned_data.get("content_type")
			content_type = ContentType.objects.get_for_model(model=BlogPost)
			obj_id = form.cleaned_data.get('object_id')
			content_data = form.cleaned_data.get("content")
			parent_obj = None
			try:
				parent_id = int(request.POST.get("parent_id"))
			except:
				parent_id = None

			if parent_id:
				parent_qs = Comment.objects.filter(id=parent_id).distinct()
				if parent_qs.exists() and parent_qs.count() == 1:
					parent_obj = parent_qs.first()
			new_comment,created= Comment.objects.get_or_create(
							user = self.request.user,
							content_type= content_type,
							object_id = obj_id,
							content = content_data,
							parent = parent_obj,
						)
			return redirect('.')
		return redirect('.')


	def get_queryset(self):
		return self.posts




class SearchResultsView(ListView):
	model = TutorialSeries
	template_name = 'mysite/search_results.html'
	context_object_name = 'results'
	paginate_by = 15

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		try:
			context['featured_posts'] = BlogPost.objects.filter(is_featured =True).order_by('id')[7]
		except:
			context['featured_posts'] = BlogPost.objects.filter(is_featured =True).order_by('id')

		try:
			context['trending_posts'] = BlogPost.objects.all().order_by('-view_count')[7].order_by('-id')

		except:
			context['trending_posts'] = BlogPost.objects.all().order_by('-view_count').order_by('-id')


		context['query'] = self.request.GET.get('q')
		return context

	def get_queryset(self): # new
		query = self.request.GET.get('q')

		tutorials = TutorialSeries.objects.filter(
			Q(title__icontains=query) |
			Q(summary__icontains=query) 
		)

		posts = BlogPost.objects.filter(
			Q(title__icontains=query) |
			Q(summary__icontains=query) 
		)

		category = Topic.objects.filter(
			Q(title__icontains=query) 
		)

		object_list = list(chain(category,tutorials,posts))

		return object_list




class CategoriesView(ListView):
	model = Topic
	template_name = 'mysite/topics.html'
	context_object_name = 'topics'


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		try:
			context['featured_posts'] = BlogPost.objects.filter(is_featured =True).order_by('id')[7]
		except:
			context['featured_posts'] = BlogPost.objects.filter(is_featured =True).order_by('id')

		try:
			context['trending_posts'] = BlogPost.objects.all().order_by('-view_count')[7].order_by('-id')

		except:
			context['trending_posts'] = BlogPost.objects.all().order_by('-view_count').order_by('-id')

		return context


class CategoryView(ListView):
	model = Topic
	template_name = 'mysite/categoryview.html'
	context_object_name = 'topics'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		category = get_object_or_404(Topic,slug=self.kwargs['category'] ) 


		results = category.related_results

		context['results'] = results
		context['category'] = category
		
		try:
			context['featured_posts'] = BlogPost.objects.filter(is_featured =True).order_by('id')[7]
		except:
			context['featured_posts'] = BlogPost.objects.filter(is_featured =True).order_by('id')

		try:
			context['trending_posts'] = BlogPost.objects.all().order_by('-view_count')[7].order_by('id')

		except:
			context['trending_posts'] = BlogPost.objects.all().order_by('-view_count').order_by('id')

		return context


def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			recaptcha_response = request.POST.get('g-recaptcha-response')
			data = {
				'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
				'response': recaptcha_response
			}
			r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
			result = r.json()
			''' End reCAPTCHA validation '''
			if result['success']:
				user = form.save()
				want_newsletter = form.cleaned_data.get('newsletter')

				username = form.cleaned_data.get('username')
				
				email = form.cleaned_data.get('email')

				if want_newsletter:
					NewsLetter.objects.create(user=username,email=email)

				User_Agreements.objects.create(user=user,want_newsletter=want_newsletter)

				messages.success(request, f'Your account has been created! You are now able to log in')
				return redirect('login')
			else:
				messages.warning(request, 'Invalid reCAPTCHA. Please try again.')
			
		else:
			messages.info(request, f'Something went wrong!!')

	else:
		
		form = UserRegisterForm()
	return render(request, 'mysite/register.html',{'form':form})
