from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
   path("",home, name="home"),
   path("notes",notes,name="notes"),
   path("delete_notes/<int:pk>",delete_notes,name="delete_notes"),
   path("notes_detail/<int:pk>",notes_detail,name="notes_detail"),
   path("homework",homework,name="homework"),
   path("homework_update/<int:pk>",update_homework,name='homework_update'),
   path('delete_homework/<int:pk>',delete_homework,name='delete_homework'),
   path('youtube',youtube,name="youtube"),
   path("todo",todo,name="todo"),
   path("update_todo/<int:pk>,",update_todo,name="update_todo"),
   path("delete_todo/<int:pk>",delete_todo,name="delete_todo"),
   path("books",books,name="books"),
   path("dictionary",dictionary,name="dictionary"),
   path("wiki",wiki,name="wiki"),
   path('conversion',conversion,name="conversion")

]
