from django.shortcuts import render,redirect
from .models import *
from .forms import *
from django.contrib import messages
from youtubesearchpython import VideosSearch
from django.core.paginator import Paginator
import requests
import wikipedia
from django.contrib.auth.decorators import login_required






from youtubesearchpython import VideosSearch

# Create your views here.

def home(request):
    # user=User.objects.filter(user=request.user)
    context={
        'user':request.user.username
    }
    return render(request,"dashboard/home.html",context)

@login_required
def notes(request):
    if request.method=="POST":
        form=NotesForm(request.POST)
        if form.is_valid():
            notes=Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
            messages.success(request,f"Notes Added  from {request.user.username} Sucefssfully")
            return redirect('notes')
            
            
    form=NotesForm()

    notes=Notes.objects.filter(user=request.user)
    context={'notes':notes, 'form':form}
    return render(request,"dashboard/notes.html",context)
@login_required
def delete_notes(request,pk=None):
    notes=Notes.objects.get(id=pk)
    notes.delete()
    messages.success(request,f"Notes Deleted Sucefssfully")
    return redirect("notes")
@login_required
def notes_detail(request,pk=None):
    notes=Notes.objects.get(id=pk)
    return render(request,"dashboard/notes_detail.html", {'notes':notes})
@login_required
def homework(request):
    if request.method=="POST":
        form=homeworkForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['is_finished']
                if finished=='on':
                    finished=True
                else:
                    finished=False
            except:
                finished=False
            homework=Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished
            )
            homework.save()
            messages.success(request,f"Homework Added  from {request.user.username} Sucefssfully")
            return redirect('homewrok')
            
            
    form=homeworkForm()
    homework=Homework.objects.filter(user=request.user)
    if len(homework)==0:
        homework_done=True
    else:
        homework_done=False
    context={'homeworks':homework,'homework_done':homework_done,'form':form}
    return render(request,"dashboard/homework.html",context)
@login_required
def update_homework(request,pk=None):    
    homework=Homework.objects.get(id=pk)
    if homework.is_finished==True:
        homework.is_finished=False
    else:
        homework.is_finished=True
    homework.save()
    return redirect('homework')
@login_required
def delete_homework(request,pk=None):
    homework=Homework.objects.get(id=pk)
    homework.delete()
    return redirect('homework')


def youtube(request):
    form = dashboardForm(request.POST or None)
    result_list = []
    query = ""

    if request.method == "POST" and form.is_valid():
        query = form.cleaned_data['text']
        request.session['query'] = query
    else:
        query = request.session.get('query', 'trending')  # default trending if nothing searched

    page_number = int(request.GET.get('page', 1))
    video_search = VideosSearch(query, limit=10 * page_number)

    try:
        all_results = video_search.result().get('result', [])
    except Exception as e:
        all_results = []
        print("Error fetching YouTube results:", e)

    # Slice only current page items
    page_results = all_results[(page_number - 1) * 10 : page_number * 10]

    for i in page_results:
        desc = ''
        if i.get('descriptionSnippet'):
            desc = ''.join(j.get('text', '') for j in i.get('descriptionSnippet'))

        result_dict = {
            "input": query,
            "title": i.get('title'),
            "duration": i.get('duration'),
            "thumbnails": i.get('thumbnails', [{}])[0].get("url"),
            "channel": i.get('channel', {}).get('name'),
            "link": i.get('link'),
            "views": i.get('viewCount', {}).get('short'),
            "published": i.get('publishedTime'),
            "description": desc
        }
        result_list.append(result_dict)

    context = {
        'form': form,
        'result': result_list,
        'page': page_number,
        'next_page': page_number + 1,
        'prev_page': page_number - 1 if page_number > 1 else None
    }

    return render(request, "dashboard/youtube.html", context)
@login_required
def todo(request):
    if request.method=="POST":
        form=todoForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['is_finished']
                if finished=='on':
                    finished=True
                else:
                    finished=False
            except:
                finished=False
            todo=Todo(
                user=request.user,
                title=request.POST['title'],
                is_finished=finished
            )
            todo.save()
            messages.success(request,f"Todo added from {request.user.username}!!")
            return redirect('todo')
    form=todoForm()
    todo=Todo.objects.filter(user=request.user)
    if len(todo)==0:
        todo_done=True
    else:
        todo_done=False
    context={'todos':todo,
              'form':form,
              'todo_done':todo_done
             }
    return render(request,"dashboard/todo.html",context)
@login_required
def update_todo(request,pk=None):
    todo=Todo.objects.get(id=pk)
    if todo.is_finished==True:
        todo.is_finished=False
    else:
        todo.is_finished=True
    todo.save()
    return redirect('todo')
@login_required
def delete_todo(request,pk=None):
    todo=Todo.objects.get(id=pk)
    todo.delete()
    messages.success(request,f"Todo Deleted Sucefssfully")
    return redirect("todo")

def books(request):
    form = dashboardForm(request.POST or None)
    result_list = []
    query = None

    # Check for search
    if request.method == "POST" and form.is_valid():
        query = request.POST['text']
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40"
    else:
        # Trending default (e.g., top tech books or bestsellers)
        url = "https://www.googleapis.com/books/v1/volumes?q=best+books&maxResults=40"

    r = requests.get(url)
    answer = r.json()
    items = answer.get('items', [])

    for item in items:
        volume = item.get('volumeInfo', {})
        result_dict = {
            'title': volume.get('title'),
            'subtitle': volume.get('subtitle'),
            'description': volume.get('description'),
            'count': volume.get('pageCount'),
            'categories': volume.get('categories'),
            'rating': volume.get('averageRating'),
            'thumbnail': volume.get('imageLinks', {}).get('thumbnail'),
            'preview': volume.get('previewLink'),
        }
        result_list.append(result_dict)

    # Paginate results
    paginator = Paginator(result_list, 10)  # Show 10 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'results': page_obj,
        'query': query,
    }
    return render(request, "dashboard/books.html", context)


def dictionary(request):
    if request.method == "POST":
        form = dashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{text}"

            try:
                r = requests.get(url)
                answer = r.json()

                phonetics = answer[0]['phonetics'][0].get('text', '')

                # Try to find the first non-empty audio URL
                audio = ''
                for phon in answer[0].get('phonetics', []):
                    if phon.get('audio'):
                        audio = phon['audio']
                        break

                definition = answer[0]['meanings'][0]['definitions'][0].get('definition', '')
                example = answer[0]['meanings'][0]['definitions'][0].get('example', '')
                # synonyms = answer[0]['meanings'][0]['definitions'][0].get('synonyms', [])
                synonyms = []
                for meaning in answer[0].get('meanings', []):
                    for definition_item in meaning.get('definitions', []):
                        if 'synonyms' in definition_item:
                            synonyms.extend(definition_item['synonyms'])

                synonyms = list(set(synonyms)) 

                context = {
                    'form': form,
                    'input': text,
                    'phonetics': phonetics,
                    'audio': audio,
                    'definition': definition,
                    'example': example,
                    'synonyms': synonyms
                }
            except Exception as e:
                print("Error:", e)
                context = {
                    'form': form,
                    'input': text,
                    'error': "Word not found or data missing."
                }

            return render(request, "dashboard/dictionary.html", context)

    else:
        form = dashboardForm()

    return render(request, "dashboard/dictionary.html", {'form': form})
@login_required
def wiki(request):
    if request.method=="POST":
        text=request.POST['text']
        form=dashboardForm(request.POST)
        search=wikipedia.page(text)
        context={
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
            
        }
        return render(request,"dashboard/wiki.html",context)
    form=dashboardForm()
    context={
        'form':form
    }
    return render(request,"dashboard/wiki.html",context)

def conversion(request):
    if request.method == "POST":
        form = conversionForm(request.POST)

        if form.is_valid():
            measurement_type = form.cleaned_data['measurement']

            if measurement_type == "length":
                measurement_form = conversionLengthForm(request.POST)

                if 'input' in request.POST:
                    first = request.POST.get('measure1')
                    second = request.POST.get('measure2')
                    input_val = request.POST.get('input')
                    answer = ''

                    if input_val and int(input_val) >= 0:
                        if first == 'yard' and second == 'foot':
                            answer = f'{input_val} yard = {int(input_val)*3} foot'
                        elif first == 'foot' and second == 'yard':
                            answer = f'{input_val} foot = {int(input_val)/3} yard'

                    context = {
                        'form': form,
                        'm_form': measurement_form,
                        'input': True,
                        'answer': answer
                    }
                    return render(request, "dashboard/conversion.html", context)

                # If only "Select" was clicked
                context = {
                    'form': form,
                    'm_form': conversionLengthForm(),
                    'input': True
                }
                return render(request, "dashboard/conversion.html", context)

            elif measurement_type == "mass":
                measurement_form = conversionMassForm(request.POST)

                if 'input' in request.POST:
                    first = request.POST.get('measure1')
                    second = request.POST.get('measure2')
                    input_val = request.POST.get('input')
                    answer = ''

                    if input_val and int(input_val) >= 0:
                        if first == 'pound' and second == 'kilogram':
                            answer = f'{input_val} pound = {int(input_val)*0.453592} kilogram'
                        elif first == 'kilogram' and second == 'pound':
                            answer = f'{input_val} kilogram = {int(input_val)*2.20462} pound'

                    context = {
                        'form': form,
                        'm_form': measurement_form,
                        'input': True,
                        'answer': answer
                    }
                    return render(request, "dashboard/conversion.html", context)

                # If only "Select" was clicked
                context = {
                    'form': form,
                    'm_form': conversionMassForm(),
                    'input': True
                }
                return render(request, "dashboard/conversion.html", context)

    # Default GET request fallback
    form = conversionForm()
    context = {
        'form': form,
        'input': False
    }
    return render(request, "dashboard/conversion.html", context)

def register(request):
    if request.method=="POST":
        form=registerForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get("username")
            messages.success(request,f"Account created for {username}!!")
            return redirect('login')
            
    form=registerForm()
    context={
        'form':form
    }
    return render(request,"dashboard/register.html",context)
@login_required
def profile(request):
    homework=Homework.objects.filter(is_finished=False,user=request.user)
    todo=Todo.objects.filter(is_finished=False,user=request.user)
    if len(homework)==0:
        homework_done=True
    else:
        homework_done=False
    if len(todo)==0:
        todo_done=True
    else:
        todo_done=False
    context={
        'homework':homework,
        'todo':todo,
        'homework_done':homework_done,
        'todo_done':todo_done
    }
    
    return render(request,"dashboard/profile.html",context)

