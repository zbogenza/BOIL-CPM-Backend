from django.db import models

class Task(models.Model):
    name = models.CharField(max_length=255)
    duration = models.PositiveIntegerField()  # Czas trwania
    start_event = models.IntegerField(default=0)
    end_event = models.IntegerField(default=0)
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True)  # Relacje między zadaniami

    def __str__(self):
        return self.name

