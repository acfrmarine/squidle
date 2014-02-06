from django.db import models

class Feedback(models.Model):

    PRIORITIES = (
        (-2, 'Lowest'),
        (-1, 'Low'),
        (0, 'Average'),
        (1, 'High'),
        (2, 'Highest'),
    )

    brief_description = models.CharField(max_length=200)
    full_description = models.TextField()
    request_date = models.DateTimeField(editable=False)
    priority = models.IntegerField(choices=PRIORITIES)
    complete = models.BooleanField(default=False)

