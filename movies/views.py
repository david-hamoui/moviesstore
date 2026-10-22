from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count, Value
from cart.models import Item
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, reported=False)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.reported = True
    review.save()
    return redirect('movies.show', id=id)


@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@staff_member_required
def admin_stats(request):

    most_purchased = Movie.objects.annotate(
        times_bought = Coalesce(Sum('item__quantity'), Value(0))
    ).order_by('-times_bought', 'name').first()

    most_reviewed = Movie.objects.annotate(
        times_reviewed = Coalesce(Count('review'), Value(0))
    ).order_by('-times_reviewed', 'name').first()

    template_data = {}
    template_data['title'] = 'Admin Stats for Purchases and Reviews'
    template_data['most_purchased'] = most_purchased
    template_data['most_reviewed'] = most_reviewed

    return render(request, 'movies/admin_stats.html', {'template_data': template_data})