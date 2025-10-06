from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
import os

def note_media_path(instance, filename):
    """Generate file path for note media uploads"""
    return f'notes/{instance.author.username}/{filename}'

class Note(models.Model):
    """
    Core note model. Free users can create text notes.
    Premium users can add media files.
    """
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Note content supports markdown")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    
    # Media upload (premium feature)
    media_file = models.FileField(
        upload_to=note_media_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx']
            )
        ],
        help_text="Premium feature: Upload images or documents"
    )
    
    # Sharing (premium feature)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_notes',
        blank=True,
        help_text="Premium feature: Share notes with other users"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    def can_user_edit(self, user):
        """Check if user can edit this note"""
        return self.author == user or user in self.shared_with.all()
    
    @property
    def media_filename(self):
        """Get just the filename without path"""
        if self.media_file:
            return os.path.basename(self.media_file.name)
        return None