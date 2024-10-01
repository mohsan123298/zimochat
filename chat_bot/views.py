from django.shortcuts import render
from .bot_logic import process_message, train_bot
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import chat_history

X, vectorizer, queries, responses = train_bot()
@login_required
def dashboard(request):
    user_id=request.user.id
    
    chat_histories= chat_history.objects.filter(user_id=user_id).order_by('-created_at')
    
    context={
        'chat_histories': chat_histories
    }
    
    return render(request, 'home/dashboard.html', context)

@login_required
def get_response(request):
    if request.method == 'POST':
        user_input = request.POST.get('message')
        bot_reply= process_message(user_input, X, vectorizer, queries, responses)
         
        return JsonResponse({'response':bot_reply})

@login_required
@csrf_exempt  # Remove this if you're handling CSRF in your AJAX calls
def save_history(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        title = request.POST.get('title')
        chathistory = request.POST.get('chathistory')
        history_id = request.POST.get('id', None)  # Get history ID if provided

        # Parse the incoming chat history
        try:
            chathistory = json.loads(chathistory)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)

        # Check if the incoming chat history is a list
        if not isinstance(chathistory, list):
            return JsonResponse({'status': 'error', 'message': 'Chat history should be a list of dictionaries'}, status=400)

        # If a history ID is provided, append the new chat data to the existing history
        if history_id:
            try:
                chat_history_obj = chat_history.objects.get(id=history_id)
                # Load existing history
                existing_history = json.loads(chat_history_obj.history)

                # Append new chat data to the existing history (which should be a list)
                existing_history.extend(chathistory)

                # Save the updated history
                chat_history_obj.history = json.dumps(existing_history)
                chat_history_obj.save()

                return JsonResponse({'status': 'success', 'message': 'History updated successfully'})
            except chat_history.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'History not found'}, status=404)

        # If no history ID, create a new chat history entry
        else:
            chat_history_obj = chat_history.objects.create(
                user_id=user_id,
                title=title,
                history=json.dumps(chathistory)  # Save the new chat history as a JSON array
            )
            return JsonResponse({'status': 'success', 'id': chat_history_obj.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    
def find_one(request, id):
    try:
        chathistory = chat_history.objects.get(id=id)
        return JsonResponse({
            'id': chathistory.id,
            'title': chathistory.title,
            'chathistory': chathistory.history  # Assuming this field stores the chat history as JSON
        })
    except chat_history.DoesNotExist:
        return JsonResponse({'error': 'Chat history not found'}, status=404)