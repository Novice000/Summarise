from celery import shared_task
from django.db import transaction
from exceptiongroup import catch
from .models import Chat, User, Summary

@shared_task
def update_chat_db(message, sender, user_id, chat_id):
    try:
        transaction.atomic()
        try:
            chat_obj = Chat.objects.get(pk= chat_id)
            chat = {sender:message}
            chat_obj.chat.append(chat)
            chat_obj.save()
            print("succesfully added message")
            
        except Chat.DoesNotExist:
            user = User.objects.get(pk=user_id)
            chat = [{sender: message}]
            chat_obj = Chat.objects.create(user = user, chat = chat)
            chat_obj.save()
            print("succesfully created a new chat")
    except Exception as e:
        print(f"failed to update task {e}")
        raise e


@shared_task
def update_summary_db(summary, user_id):
    try:
        transaction.atomic()
        try:
            user = User.objects.get(pk = user_id)
        except User.DoesNotExist:
            print("print user does not exist")
            
        if Summary.objects.filter(user= user, summary = summary).exists():
            pass
        else:
            Summary.objects.create(user=user, summary=summary)
    except Exception as e:
                print(f"Error updating summary table: {e}")
    