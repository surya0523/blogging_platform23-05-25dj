# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Post, Comment, Category
from .forms import PostForm, CommentForm, SearchForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_on')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        return context

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.filter(is_moderated=True)
        context['comment_form'] = CommentForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        # Send email alerts for new blog posts
        subject = f"New Blog Post: '{form.instance.title}'"
        message = render_to_string('emails/new_post_alert.html', {'post': form.instance})
        send_mail(
            subject,
            message,
            'your-email@gmail.com',
            ['all-subscribers@example.com'], # You'd have a list of user emails here
            fail_silently=False
        )
        return response
    
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    slug_url_kwarg = 'slug'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')
    slug_url_kwarg = 'slug'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    

@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post-detail', slug=slug)
    return redirect('post-detail', slug=slug)


@login_required
def moderate_comment(request, comment_id):
    # சூப்பர் யூசர் (superuser) அல்லது ஸ்டாஃப் (staff) பயனர் மட்டுமே அனுமதிக்கப்படுவார்.
    if not request.user.is_superuser and not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to moderate this comment.")
        
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_moderated = True
    comment.save()
    return redirect('post-detail', slug=comment.post.slug)