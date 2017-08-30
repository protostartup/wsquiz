import json
from random import randint

from django.db import models
from django.db.models import Count
from channels import Group


class Player(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    @property
    def time_playing(self):
        """
        Returns the total number of seconds of playing, calculating
        from the first question answered to the last.
        """

        first_question = self.questionchoiceplayer_set.earliest()
        last_question = self.questionchoiceplayer_set.latest()
        total_time = last_question.created_at - first_question.created_at
        return total_time.seconds

    @property
    def wrong_answers(self):
        """
        Returns the count of questions answered wrongly.
        """

        return self.questionchoiceplayer_set.filter(
            choice__right_answer=False
        ).count()

    @property
    def right_answers(self):
        """
        Returns the count of questions answered correctly.
        """

        return self.questionchoiceplayer_set.filter(
            choice__right_answer=True
        ).count()

    @classmethod
    def top_players(cls):
        """
        Returns a list of the five best players, calculated by the
        total number of answered questions and time playing.
        """

        qs = cls.objects.all()

        return sorted(
            qs,
            key=lambda player: (player.right_answers, -player.time_playing)
        )[::-1]


class Question(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

    @classmethod
    def next_random_question(cls, player=None):
        """
        Giving a player, returns the next random question.
        If there is no questions left to be answered, return False.
        """

        qs = cls.objects.all()

        if player:
            qs = qs.exclude(questionchoiceplayer__player__name=player)
        if qs.count():
            return qs[randint(0, qs.count() -1)]

    @classmethod
    def next_random_question_serialized(cls, player=None):
        """
        Giving a player, returns the next random question serialized
        to be sent over the WebSocket.
        """

        question = cls.next_random_question(player=player)
        if question:
            question_body = {
                'question': question.text,
                'question_id': question.id,
                'choices': [
                    {
                        'text': choice.text,
                        'id': choice.id,
                    } for choice in question.choice_set.all()
                ]
            }

            return question_body

    @classmethod
    def get_question(cls, player=None):
        """
        Returns the final response to be sent over the WebSocket,
        including the next question and if the game is finished or
        not.
        """

        next_question = cls.next_random_question_serialized(player)
        game_finished = not bool(next_question)

        last_right_answer = None
        time_playing = None
        last_question_status = None
        if player:
            last_right_answer = QuestionChoicePlayer.last_right_answer(player)
            time_playing = Player.objects.get(name=player).time_playing
            last_question_status = QuestionChoicePlayer.last_question_status(player)

        result = {
            'text': json.dumps({
                'next_question': next_question or False,
                'game_finished': game_finished,
                'time_playing': time_playing,
                'last_right_answer': last_right_answer,
                'last_question_status': last_question_status,
            })
        }

        return result


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    right_answer = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.question, self.text)


class QuestionChoicePlayer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=False, blank=True, auto_now_add=True)

    class Meta:
        unique_together = ('player', 'question')
        get_latest_by = 'created_at'

    def __str__(self):
        return '{} - {}'.format(self.player, self.choice)

    @classmethod
    def last_right_answer(cls, player):
        """
        Returns the last right answer for the question answred by a player.
        """

        question = cls.objects.filter(player__name=player).latest().question
        choice = question.choice_set.filter(right_answer=True).last().id
        return choice

    @classmethod
    def last_question_status(cls, player):
        """
        Returns if the Player answered correctly the last question.
        """

        question = cls.objects.filter(player__name=player).latest()
        question_status = question.choice.right_answer
        return question_status

    @classmethod
    def send_top_players(cls):
        """
        Send the top players to the WebSocket, already serialized.
        """

        top_players = [
            {
                'name': player.name,
                'right_answers': player.right_answers,
                'wrong_answers': player.wrong_answers,
                'time_playing': player.time_playing,
                'total_questions': Question.objects.count(),
            } for player in Player.top_players()
        ]

        vuash = Group('top_players').send({
            'text': json.dumps(top_players)
        })

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        QuestionChoicePlayer.send_top_players()
        return result
