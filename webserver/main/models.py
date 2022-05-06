from django.db import models


class Manga(models.Model):
    cover_img = models.ImageField(upload_to="mangas/cover-images")
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    year = models.IntegerField()

    def __str__(self) -> str:
        return f'{self.title}'

    def __repr__(self) -> str:
        return f'<Manga: {self.title}>'

