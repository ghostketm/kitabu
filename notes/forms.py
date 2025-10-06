from django import forms
from .models import Note

class NoteForm(forms.ModelForm):
    """Form for creating/editing notes"""
    class Meta:
        model = Note
        fields = ['title', 'content', 'media_file', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Note title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your note here...'}),
            'media_file': forms.FileInput(attrs={'class': 'form-control'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Disable media upload for non-premium users
        if self.user and not self.user.is_premium:
            self.fields['media_file'].disabled = True
            self.fields['media_file'].help_text = "Upgrade to Premium (Ksh 87) to upload media"

class ShareNoteForm(forms.Form):
    """Form for sharing notes with other users (premium feature)"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username to share with'})
    )