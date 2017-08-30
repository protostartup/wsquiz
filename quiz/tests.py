import json

from channels import Channel, Group
from channels.test import ChannelTestCase, WSClient

from quiz import models


class ChannelTests(ChannelTestCase):

    def _setup_player(self, name='Player'):
        return models.Player.objects.create(name=name)

    def _setup_question(self, text='My Question'):
        return models.Question.objects.create(text=text)

    def _setup_choice(self, question, text='My Choice', right_answer=True):
        return models.Choice.objects.create(
            question=question,
            text=text,
            right_answer=right_answer,
        )

    def _setup_answer(self, question, choice, player):
        return models.QuestionChoicePlayer.objects.create(
            question=question,
            choice=choice,
            player=player
        )

    def test_top_players(self):
        player = self._setup_player()
        question = self._setup_question()
        choice = self._setup_choice(question=question)

        Group('top_players').add('test_channel')

        self._setup_answer(
            player=player,
            question=question,
            choice=choice
        )

        top_players = models.Player.top_players()

        result = self.get_next_message('test_channel', require=True)
        result = json.loads(result['text'])

        self.assertEqual(result[0]['name'], top_players[0].name)
        self.assertEqual(result[0]['right_answers'], top_players[0].right_answers)
        self.assertEqual(result[0]['wrong_answers'], top_players[0].wrong_answers)
        self.assertEqual(result[0]['time_playing'], top_players[0].time_playing)

    def test_send_answer_no_more_question(self):
        player = self._setup_player()
        question = self._setup_question()
        choice = self._setup_choice(question=question)

        text = {
            'player': player.name,
            'question_id': question.id,
            'choice_id': choice.id,
        }

        client = WSClient()
        client.send_and_consume('websocket.receive', text=text)
        result = client.receive()

        self.assertFalse(result['next_question'])
        self.assertTrue(result['game_finished'])
        self.assertTrue(result['last_right_answer'], choice.text)
        self.assertEqual(result['time_playing'], player.time_playing)

    def test_send_answer_with_more_question(self):
        player = self._setup_player()
        question_one = self._setup_question()
        question_two = self._setup_question()
        choice_one = self._setup_choice(question=question_one)
        choice_two = self._setup_choice(question=question_two)

        text = {
            'player': player.name,
            'question_id': question_one.id,
            'choice_id': choice_one.id,
        }

        client = WSClient()
        client.send_and_consume('websocket.receive', text=text)
        result = client.receive()

        self.assertTrue('question' in result['next_question'])
        self.assertEqual(result['next_question']['question'], question_two.text)
        self.assertEqual(result['next_question']['choices'][0]['text'], choice_two.text)
        self.assertTrue(result['last_right_answer'], choice_one.text)
        self.assertFalse(result['game_finished'])
