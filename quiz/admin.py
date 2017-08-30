from django.contrib import admin

from quiz import models


class ChoiceInline(admin.TabularInline):
    model = models.Choice
    extra = 0


@admin.register(models.Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        ChoiceInline,
    ]


@admin.register(models.Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_filter = ('question',)
    list_display = ('question', 'text', 'right_answer')


@admin.register(models.QuestionChoicePlayer)
class QuestionChoicePlayerAdmin(admin.ModelAdmin):
    list_filter = ('question', 'player')
    list_display = ('question', 'player', 'right_answer')

    def right_answer(self, obj):
        return obj.choice.right_answer
    right_answer.boolean = True
