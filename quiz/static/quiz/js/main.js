var WebsocketBridge = (function() {
  var WS_PATH_ROOT = '/ws/'
  var WS_PATH_TOP_PLAYERS = '/ws/top_players/'
  var topPlayersWebSocket
  var questionsWebSocket
  var currentQuestionID

  var init = function() {
    openTopPlayersBridge()
  }

  var openTopPlayersBridge = function() {
    console.log('Opening questions bridge ' + WS_PATH_TOP_PLAYERS)
    topPlayersWebSocket = new channels.WebSocketBridge()
    topPlayersWebSocket.connect(WS_PATH_TOP_PLAYERS)
    topPlayersWebSocket.listen(onTopPlayersReceived)
    console.log('Connected to ' + WS_PATH_TOP_PLAYERS)
  }

  var onTopPlayersReceived = function(data) {
    console.log('Got top_players message ', data)
    var topPlayersList = $('.js-top-players')
    topPlayersList.empty()
    data.forEach(function(player) {
      var total = player.right_answers + player.wrong_answers
      var wrongPercent = (player.wrong_answers * 100) / total
      var rightPercent = (player.right_answers * 100) / total
      var player = '<li class="player">' + 
                      '<span class="player__percent player__percent--correct" style="width:' + rightPercent + '%">&nbsp;</span>' +
                      '<span class="player__percent player__percent--wrong" style="width:' + wrongPercent + '%; left: ' + (100 - wrongPercent) + '%;">&nbsp;</span>' +
                      '<span class="player__name">' + player.name + '</span>' +
                      '<span class="player__time">' + player.time_playing + 's - '+ player.right_answers + '/' + player.total_questions + ' </span>' +
                    '</li>';
      topPlayersList.append(player)
    })
  }

  var openQuestionsBridge = function() {
    console.log('Opening questions bridge ' + WS_PATH_ROOT)
    questionsWebSocket = new channels.WebSocketBridge()
    questionsWebSocket.connect(WS_PATH_ROOT)
    questionsWebSocket.listen(onQuestionReceived);
  }

  var onQuestionReceived = function(data) {
    console.log(data)
    if (!data.game_finished) {
      currentQuestionID = data.next_question.question_id
      $('.question').text(data.next_question.question)
      $('.js-choices').empty();

      data.next_question.choices.forEach(function(choice) {
        $('.js-choices').append('<input type="button" class="choice js-choice" id="' + choice.id + '" value="' + choice.text + '">\n');
      })
      bindChoices()
      return
    }
    
    // FinishGame
    $('.js-choices, .js-submit').hide();
    $('.question').html(Player.get() + '<br>[Thanks for playing!]')
  }

  var bindChoices = function() {
    $('.js-choice').off('click').on('click', onChoiceChoose);
    $('.js-submit').off('click').on('click', submitChoice);
  }

  var submitChoice = function(event) {
    event.preventDefault();
    var player = Player.get()
    var choiceId = $('.js-choice.choice--selected').attr('id')
    if (choiceId) {
      questionsWebSocket.send({
        'player': player,
        'question_id': currentQuestionID,
        'choice_id': choiceId,
      })
    }
  }

  var onChoiceChoose = function(event) {
    event.preventDefault();
    $('.js-choice').removeClass('choice--selected');
    $(this).addClass('choice--selected')
  }

  return {
    init: init,
    openQuestionsBridge: openQuestionsBridge,
  }
}())

var Interface = (function() {

  var init = function() {
    $('.js-join').bind('click', onClickJoinButton)
  }

  var onClickJoinButton = function(event) {
    event.preventDefault()
    var playerName = $('.js-player-name').val()
    if (!playerName) {
      $('.js-player-name').addClass('player-name__field--error')
      return
    }
    $('.js-player-name').removeClass('player-name__field--error')
    Player.setPlayer(playerName)
    WebsocketBridge.openQuestionsBridge()
    $('.js-game').addClass('game--show')
    $('.js-player-name-container').addClass('player-name--hide')
  }

  return {
    init: init,
  }
}())

var Player = (function() {
  var player

  var setPlayer = function(playerName) {
    player = playerName
  }

  var get = function() {
    return player
  }

  return {
    setPlayer: setPlayer,
    get: get,
  }
}())

WebsocketBridge.init()
Interface.init()
