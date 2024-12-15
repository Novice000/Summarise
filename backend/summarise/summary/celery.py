from celery import shared_task
from django.db import transaction
from exceptiongroup import catch
from .models import Chat, User, Summary

@shared_task
def update_chat_db(output, query, user_id, chat_id = None):
    
    try:
        transaction.atomic()
        
        if chat_id != None:
            try:
                chat_obj = Chat.objects.get(pk= chat_id)
                query = {"query":query}
                response = {"response": output}
                chat_obj.chat.append(query, response)
                chat_obj.save()
                print("succesfully added message")
            except Chat.DoesNotExist:
                user = User.objects.get(pk=user_id)
                query = {"query":query}
                response = {"response": output}
                chat = [query, response]
                chat_obj = Chat.objects.create(user = user, chat = chat)
                chat_obj.save()
                print("succesfully created a new chat")
            
        else:
            user = User.objects.get(pk=user_id)
            query = {"query":query}
            response = {"response": output}
            chat = [query, response]
            chat_obj = Chat.objects.create(user = user, chat = chat)
            chat_obj.save()
            print("succesfully created a new chat")
            
    except Exception as e:
        print(f"failed to update task {e}")
        raise e


@shared_task
def update_summary_db(user_id, to_summarise, summary):
    
    try:
        transaction.atomic()
        
        try:
            
            user = User.objects.get(pk = user_id)
            
        except User.DoesNotExist:
            print("print user does not exist")
            
        if Summary.objects.filter(user= user, to_summarise = to_summarise, summary = summary).exists():
            pass
        else:
            Summary.objects.create(user=user, ot_summarise = to_summarise, summary=summary)
    except Exception as e:
                print(f"Error updating summary table: {e}")
    