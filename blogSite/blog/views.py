from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.core.paginator import Paginator
from .forms import CommentForm, PostForm
from .models import Post, Comment


# Create your views here.

class AboutView(TemplateView):
    template_name = 'about.html'


class PostListView(ListView):
    model = Post
    paginate_by = 2

    def get_queryset(self):
        zapytanie = self.model.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        return zapytanie

class PostDetailView( DetailView):
    model = Post
    paginate_by = 2

    def get_context_data(self, **kwargs):
        object_list = Comment.objects.filter(post=self.get_object()).order_by('id')
        context = super(PostDetailView, self).get_context_data(object_list=object_list, **kwargs)
        activities = self.get_related_activities(object_list)
        context['page_obj'] = activities
        context['object_list'] = activities.object_list
        return context

    def get_related_activities(self, query_object_list):
        queryset = query_object_list
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page')
        activities = paginator.get_page(page)
        return activities

class CreatePostView(LoginRequiredMixin, CreateView):
    model = PostForm
    form_class = PostForm
    template_name = 'blog/post_form.html'
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'


class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    login_url = '/login/'
    template_name = 'post_draft_list.html'
    redirect_field_name = 'blog/post_list.html'

    def get_queryset(self):
        return self.model.objects.filter(published_date__isnull=True).order_by('-published_date')

################################################



@login_required()
def post_publish(request, pk):
    request.method = 'GET'
    post = get_object_or_404(Post, pk=pk)
    post_pk = post.pk
    post.publish()
    return redirect('post_detail', pk=post_pk)



def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form': form})


@login_required()
def comment_approve(request, pk):
    request.method = 'GET'
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required()
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect(request, 'post_detail', pk=post_pk)

def get_post_comments(request):
    comment = get_object_or_404(Comment.post.primary_key)
    request.method = 'GET'
    clist = comment.object.all()
    print(clist)
    return redirect(request, 'comments_list', clist)

