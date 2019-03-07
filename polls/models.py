from django.db import models
from django.utils.html import mark_safe

from users.models import User

from markdown import markdown

# Create your models here.


class Poll(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_user')
    text = models.CharField(max_length=255)
    pub_date = models.DateField()

    def __str__(self):
        return self.text

    def user_can_vote(self, user):
        """
        Returns False is user has already voted, else True
        """
        user_votes = user.vote_user.all()
        qs = user_votes.filter(poll=self)
        if qs.exists():
            return False
        return True

    @property
    def num_votes(self):
        return self.vote_set.count()

    def get_results_dict(self):
        """
        Returns a list of objects in the form:
        [
            # for each related choice
            {
                'text': choice_text,
                'num_votes': number of votes on that choice
                'percentage': num_votes / poll.num_votes * 100
            }
        ]
        """
        res = []
        for choice in self.choice_set.all():
            d = {}
            d['text'] = choice.choice_text
            d['num_votes'] = choice.num_votes
            if not self.num_votes:
                d['percentage'] = 0
            else:
                d['percentage'] = choice.num_votes / self.num_votes * 100
            res.append(d)
        return res

    def get_polls_as_markdown(self):
        return mark_safe(markdown(self.text, safe_mode='escape'))


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)

    def __str__(self):
        return "{} - {}".format(self.poll.text[:25], self.choice_text[:25])

    @property
    def num_votes(self):
        return self.vote_set.count()


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vote_user')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
