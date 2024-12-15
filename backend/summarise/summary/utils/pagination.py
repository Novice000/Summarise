from rest_framework.pagination import PageNumberPagination

class SummaryPaginator(PageNumberPagination):
    page_size = 10
    
class ChatPaginator(PageNumberPagination):
    page_size = 20