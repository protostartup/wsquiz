var WebsocketBridge = (function() {
  var WS_PATH_ROOT = "/ws/";
  var WS_PATH_TOP_PLAYERS = "/ws/top_players/";
  var topPlayersWebSocket;
  var questionsWebSocket;
  var currentQuestionID;

  var init = function() {
    openTopPlayersBridge();
  };

  var openTopPlayersBridge = function() {
    console.log("Opening questions bridge " + WS_PATH_TOP_PLAYERS);
    topPlayersWebSocket = new channels.WebSocketBridge();
    topPlayersWebSocket.connect(WS_PATH_TOP_PLAYERS);
    topPlayersWebSocket.listen(onTopPlayersReceived);
    console.log("Connected to " + WS_PATH_TOP_PLAYERS);
  };

  var onTopPlayersReceived = function(data) {
    console.log("Got top_players message ", data);
    var topPlayersList = $(".js-top-players");
    topPlayersList.empty();
    data.forEach(function(player) {
      var total = player.right_answers + player.wrong_answers;
      var wrongPercent = player.wrong_answers * 100 / total;
      var rightPercent = player.right_answers * 100 / total;
      var player =
        '<li class="player">' +
        '<span class="player__percent player__percent--correct" style="width:' +
        rightPercent +
        '%">&nbsp;</span>' +
        '<span class="player__percent player__percent--wrong" style="width:' +
        wrongPercent +
        "%; left: " +
        (100 - wrongPercent) +
        '%;">&nbsp;</span>' +
        '<span class="player__name">' +
        player.name +
        "</span>" +
        '<span class="player__time">' +
        player.time_playing +
        "s - " +
        player.right_answers +
        "/" +
        player.total_questions +
        " </span>" +
        "</li>";
      topPlayersList.append(player);
    });
  };

  var openQuestionsBridge = function() {
    console.log("Opening questions bridge " + WS_PATH_ROOT);
    questionsWebSocket = new channels.WebSocketBridge();
    questionsWebSocket.connect(WS_PATH_ROOT);
    questionsWebSocket.listen(onQuestionReceived);
  };

  var onQuestionReceived = function(data) {
    if (data.last_right_answer) {
      if (!data.last_question_status) {
        $(".js-choice").addClass("choice--wrong");
        $('.js-choice[id="' + data.last_right_answer + '"]')
          .removeClass("choice--wrong")
          .addClass("choice--right");
      } else {
        $('.js-choice[id="' + data.last_right_answer + '"]').addClass("choice--right");
      }
      var timer = setTimeout(function() {
        printAnswers(data);
      }, 1000);
      return;
    }
    printAnswers(data);
  };

  var printAnswers = function(data) {
    if (!data.game_finished) {
      currentQuestionID = data.next_question.question_id;
      $(".question").text(data.next_question.question);
      $(".js-choices").empty();

      data.next_question.choices.forEach(function(choice) {
        $(".js-choices").append(
          '<input type="button" class="choice js-choice" id="' +
            choice.id +
            '" value="' +
            choice.text +
            '">\n'
        );
      });
      bindChoices();
      return;
    }

    // FinishGame
    $(".js-choices, .js-submit").hide();
    $(".question").html(Player.get() + "<br>[Thanks for playing!]");
  };

  var bindChoices = function() {
    $(".js-choice")
      .off("mousedown")
      .on("mousedown", onChoiceChoose);
    $(".js-submit")
      .off("mousedown")
      .on("mousedown", submitChoice);
  };

  var submitChoice = function(event) {
    event.preventDefault();
    var player = Player.get();
    var choiceId = $(".js-choice.choice--selected").attr("id");
    if (choiceId) {
      questionsWebSocket.send({
        player: player,
        question_id: currentQuestionID,
        choice_id: choiceId,
      });
    }
  };

  var onChoiceChoose = function(event) {
    event.preventDefault();
    console.log("clicked");
    $(".js-choice").removeClass("choice--selected");
    $(this).addClass("choice--selected");
  };

  return {
    init: init,
    openQuestionsBridge: openQuestionsBridge,
  };
})();

var Interface = (function() {
  var join = function(event) {
    var playerName = $(".js-player-name").val();
    if (!playerName) {
      $(".js-player-name").addClass("player-name__field--error");
      return;
    }
    $(".js-player-name").removeClass("player-name__field--error");
    Player.setPlayer(playerName);
    WebsocketBridge.openQuestionsBridge();
    $(".js-game").addClass("game--show");
    $(".js-player-name-container").addClass("player-name--hide");
  };

  return {
    join: join,
  };
})();

var Player = (function() {
  var player;

  var setPlayer = function(playerName) {
    player = playerName;
  };

  var get = function() {
    return player;
  };

  return {
    setPlayer: setPlayer,
    get: get,
  };
})();

WebsocketBridge.init();
