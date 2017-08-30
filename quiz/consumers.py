import json

from channels import Group

from .models import Player, Question, Choice, QuestionChoicePlayer


def ws_connect(message):
    message.reply_channel.send({'accept': True})
    Group('wsquiz').add(message.reply_channel)

    result = Question.get_question()
    message.reply_channel.send(result)


def ws_message(message):
    message_body = json.loads(message['text'])

    question = message_body.get('question_id')
    choice = message_body.get('choice_id')
    player = message_body.get('player')

    if not choice or not Choice.objects.filter(id=choice).first():
        raise Exception('INVALID_CHOICE')

    if not question and not Question.objects.filter(id=question).first():
        raise Exception('INVALID_QUESTION')

    if not player:
        raise Exception('INVALID_USER')

    player_obj, _ = Player.objects.get_or_create(name=player)

    if question and choice:
        QuestionChoicePlayer.objects.get_or_create(
            player_id=player_obj.id,
            question_id=question,
            choice_id=choice,
        )

    result = Question.get_question(player)
    message.reply_channel.send(result)


def ws_disconnect(message):
    Group('wsquiz').discard(message.reply_channel)


def top_players_connect(message):
    message.reply_channel.send({'accept': True})
    Group('top_players').add(message.reply_channel)
    QuestionChoicePlayer.send_top_players()


def top_players_disconnect(message):
    Group('top_players').discard(message.reply_channel)
