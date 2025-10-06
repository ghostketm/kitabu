from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Note
from .forms import NoteForm, ShareNoteForm
from accounts.models import CustomUser

@login_required
def note_list(request):
    """Display all notes for the current user"""
    my_notes = Note.objects.filter(author=request.user)
    shared_notes = request.user.shared_notes.all()
    
    return render(request, 'notes/note_list.html', {
        'my_notes': my_notes,
        'shared_notes': shared_notes,
    })

@login_required
def note_create(request):
    """Create a new note"""
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            
            # Check if user is trying to upload media without premium
            if note.media_file and not request.user.is_premium:
                messages.error(request, 'Media upload requires Premium. Upgrade for only Ksh 87!')
                return redirect('payments:upgrade')
            
            note.save()
            messages.success(request, 'Note created successfully!')
            return redirect('notes:note_detail', pk=note.pk)
    else:
        form = NoteForm(user=request.user)
    
    return render(request, 'notes/note_form.html', {'form': form, 'action': 'Create'})

@login_required
def note_detail(request, pk):
    """View a single note"""
    note = get_object_or_404(Note, pk=pk)
    
    # Check permissions
    if not note.can_user_edit(request.user):
        return HttpResponseForbidden("You don't have permission to view this note.")
    
    return render(request, 'notes/note_detail.html', {'note': note})

@login_required
def note_edit(request, pk):
    """Edit an existing note"""
    note = get_object_or_404(Note, pk=pk)
    
    if note.author != request.user:
        messages.error(request, "You can only edit your own notes.")
        return redirect('notes:note_list')
    
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES, instance=note, user=request.user)
        if form.is_valid():
            updated_note = form.save(commit=False)
            
            # Check media upload permission
            if updated_note.media_file and not request.user.is_premium:
                messages.error(request, 'Media upload requires Premium!')
                return redirect('payments:upgrade')
            
            updated_note.save()
            messages.success(request, 'Note updated successfully!')
            return redirect('notes:note_detail', pk=note.pk)
    else:
        form = NoteForm(instance=note, user=request.user)
    
    return render(request, 'notes/note_form.html', {'form': form, 'action': 'Edit', 'note': note})

@login_required
def note_delete(request, pk):
    """Delete a note"""
    note = get_object_or_404(Note, pk=pk, author=request.user)
    
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully!')
        return redirect('notes:note_list')
    
    return render(request, 'notes/note_confirm_delete.html', {'note': note})

@login_required
def note_share(request, pk):
    """Share a note with another user (premium feature)"""
    note = get_object_or_404(Note, pk=pk, author=request.user)
    
    if not request.user.is_premium:
        messages.error(request, 'Sharing notes requires Premium!')
        return redirect('payments:upgrade')
    
    if request.method == 'POST':
        form = ShareNoteForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user_to_share = CustomUser.objects.get(username=username)
                if user_to_share == request.user:
                    messages.error(request, "You can't share a note with yourself!")
                elif user_to_share in note.shared_with.all():
                    messages.info(request, f'Note already shared with {username}')
                else:
                    note.shared_with.add(user_to_share)
                    messages.success(request, f'Note shared with {username}!')
                return redirect('notes:note_detail', pk=note.pk)
            except CustomUser.DoesNotExist:
                messages.error(request, f'User "{username}" not found.')
    else:
        form = ShareNoteForm()
    
    return render(request, 'notes/note_share.html', {'form': form, 'note': note})