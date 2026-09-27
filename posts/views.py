import os
import requests
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from .models import Post
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Initialiser le planificateur
scheduler = BackgroundScheduler()
scheduler.start()

class CreatePostView(View):
    def get(self, request):
        # Obtenir la date et l'heure actuelles au format local
        now = timezone.localtime(timezone.now())
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        return render(request, 'create_post.html', {'current_date': current_date, 'current_time': current_time})

    def post(self, request):
        # Récupérer les données du formulaire
        image_url = request.POST['image_url']
        caption = request.POST['caption']
        post_date = request.POST['post_date']
        post_time = request.POST['post_time']

        # Récupérer les informations de l'utilisateur ou utiliser des valeurs par défaut depuis l'environnement
        access_token = getattr(request.user, 'access_token', os.getenv('ACCESS_TOKEN'))
        ig_user_id = getattr(request.user, 'instagram_account_id', os.getenv('INSTAGRAM_ACCOUNT_ID'))

        # Vérifier la validité du token d'accès
        if not validate_access_token(access_token):
            return HttpResponse("Le token d'accès est invalide ou a expiré.", status=403)

        # Convertir la date et l'heure en datetime
        post_datetime = datetime.datetime.strptime(f"{post_date} {post_time}", "%Y-%m-%d %H:%M")

        # Sauvegarder le post dans la base de données
        post = Post(
            user=request.user,
            image_url=image_url,
            caption=caption,
            post_date=post_date,
            post_time=post_time,
            is_published=False
        )
        post.save()

        # Planifier la tâche pour poster sur Instagram
        scheduler.add_job(post_to_instagram, 'date', run_date=post_datetime, args=[post, ig_user_id, image_url, caption, access_token])

        return redirect('posteta')

def post_to_instagram(post, ig_user_id, image_url, caption, access_token):
    """
    Fonction pour poster sur Instagram au moment programmé.
    """
    creation_id = create_media_object(ig_user_id, image_url, caption, access_token)
    if creation_id:
        success = publish_media_object(ig_user_id, creation_id, access_token)
        if success:
            post.is_published = True
            post.save()
        else:
            print(f"Échec de la publication de l'objet média : {creation_id}")
    else:
        print("Échec de la création de l'objet média")

# Créer l'objet média sur Instagram
def create_media_object(ig_user_id, image_url, caption, access_token):
    """
    Crée un objet média sur Instagram.
    """
    url = f'https://graph.facebook.com/v12.0/{ig_user_id}/media'
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': access_token
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json().get('id')
    else:
        print(f"Erreur lors de la création de l'objet média : {response.status_code} {response.text}")
        return None

# Publier l'objet média sur Instagram
def publish_media_object(ig_user_id, creation_id, access_token):
    """
    Publie un objet média précédemment créé sur Instagram.
    """
    url = f'https://graph.facebook.com/v12.0/{ig_user_id}/media_publish'
    payload = {
        'creation_id': creation_id,
        'access_token': access_token
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"Objet média publié : {response.json()}")
        return True
    else:
        print(f"Erreur lors de la publication de l'objet média : {response.status_code} {response.text}")
        return False

# Fonction pour valider le token d'accès
def validate_access_token(access_token):
    """
    Valide le token d'accès Instagram en utilisant l'API Facebook Graph.
    """
    url = f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={access_token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("data", {}).get("is_valid"):
            return True
    return False

# Vue pour afficher et gérer les posts programmés
class ScheduledPostsView(View):
    def get(self, request):
        posts = Post.objects.filter(user=request.user)  # Récupérer les posts de l'utilisateur connecté
        return render(request, 'posteta.html', {'posts': posts})

    def post(self, request):
        action = request.POST.get('action')
        post_id = request.POST.get('post_id')

        if action == 'delete':
            post = get_object_or_404(Post, id=post_id, user=request.user)
            post.delete()
        elif action == 'update':
            post = get_object_or_404(Post, id=post_id, user=request.user)
            
            image_url = request.POST.get(f'image_url_{post_id}', post.image_url)
            caption = request.POST.get(f'caption_{post_id}', post.caption)
            post_date_str = request.POST.get(f'post_date_{post_id}', post.post_date.strftime('%Y-%m-%d'))
            post_time_str = request.POST.get(f'post_time_{post_id}', post.post_time.strftime('%H:%M'))

            try:
                post_date = datetime.datetime.strptime(post_date_str, '%Y-%m-%d').date()
                post_time = datetime.datetime.strptime(post_time_str, '%H:%M').time()
                post_datetime = timezone.make_aware(datetime.datetime.combine(post_date, post_time))
            except ValueError:
                post_datetime = timezone.now()
            
            post.image_url = image_url
            post.caption = caption
            post.post_date = post_date
            post.post_time = post_time

            # Définir le post comme publié si la date et l'heure sont passées
            if post_datetime <= timezone.now():
                post.is_published = True
            else:
                post.is_published = False
            
            post.save()

        return redirect('posteta')
