from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser  # Importer votre modèle utilisateur personnalisé
from .forms import CustomUserCreationForm, UpdateUserForm  # S'assurer que le bon formulaire est importé

# Fonction pour vérifier si l'utilisateur est administrateur
def is_admin(user):
    return user.is_superuser  # Vérifier si l'utilisateur est un superutilisateur

# Vue pour le login personnalisé
def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')  # Récupérer le rôle sélectionné dans le formulaire de connexion

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Vérifier le rôle sélectionné et le rôle réel de l'utilisateur, puis rediriger en conséquence
            if role == 'admin' and user.is_superuser:
                return redirect('admin_dashboard')  # Rediriger les administrateurs vers le tableau de bord admin
            elif role == 'user' and not user.is_superuser:
                return redirect('create_post')  # Rediriger les utilisateurs normaux vers la création de post
            else:
                # Mauvaise sélection de rôle
                return render(request, 'login.html', {'error': 'Rôle incorrect pour cet utilisateur.'})
        else:
            # Erreur de connexion : identifiants invalides
            return render(request, 'login.html', {'error': 'Identifiants incorrects'})
    
    return render(request, 'login.html')

# Vue pour le tableau de bord admin qui liste tous les utilisateurs
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Exclure l'utilisateur admin actuel
    users = CustomUser.objects.exclude(pk=request.user.pk)  # Utiliser CustomUser au lieu de User
    return render(request, 'accounts/admin_dashboard.html', {'users': users})

# Vue pour créer un nouveau compte utilisateur
@login_required
@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Définir le mot de passe
            user.save()
            return redirect('admin_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/create_user.html', {'form': form})

# Vue pour mettre à jour un compte utilisateur existant
@login_required
@user_passes_test(is_admin)
def update_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)  # Utiliser CustomUser au lieu de User
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)  # Utiliser UpdateUserForm pour la mise à jour
        if form.is_valid():
            user = form.save(commit=False)
            
            # Si un nouveau mot de passe est fourni, le définir
            if form.cleaned_data.get('password1'):
                user.set_password(form.cleaned_data['password1'])
            
            user.save()
            return redirect('admin_dashboard')
    else:
        form = UpdateUserForm(instance=user)
    return render(request, 'accounts/update_user.html', {'form': form})

# Vue pour supprimer un compte utilisateur existant
@login_required
@user_passes_test(is_admin)
def delete_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)  # Utiliser CustomUser au lieu de User
    if request.method == 'POST':
        user.delete()
        return redirect('admin_dashboard')
    return render(request, 'accounts/delete_user.html', {'user': user})
