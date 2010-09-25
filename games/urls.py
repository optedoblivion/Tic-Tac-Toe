from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'games.tictactoe.views.index'),
    (r'^tictactoe/$', 'games.tictactoe.views.index'),
    (r'^tictactoe/getAvailableMoves/$', 'games.tictactoe.views.getAvailableMoves'),
    (r'^tictactoe/makeHumanMove/$', 'games.tictactoe.views.makeHumanMove'),
    (r'^tictactoe/makeComputerMove/$', 'games.tictactoe.views.makeComputerMove'),

)
