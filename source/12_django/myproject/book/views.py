from django.shortcuts import render, redirect, reverse,  get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import BookForm, BookModelForm
from .models import Book
# 1. form없이 걍 2. form객체생성후(6장) 3. DjangoGenericView 이용 4. GenericView 상속(7장)

# def book_list(request):
#         return render(request, "book/book_list.html", {'book_list': Book.objects.all()})

book_list = ListView.as_view(model=Book)

book_new = CreateView.as_view(model=Book,
                                fields = ['title', 'author', 'publisher', 'sales'])

class BookCreateView(CreateView):
    model = Book
    fields = ['title', 'author', 'publisher', 'sales']
    def form_valid(self, form): # 유효성 검사 성공후 자동 호출
        book = form.save(commit=False)
        book.ip = self.request.META['REMOTE_ADDR'] # 요청한 client의 ip
        book.save()
        return redirect(book) # book.get_absoute_url()의 return값 적용

book_new = BookCreateView.as_view()

def book_new1(request): # GET방식 : template / POST방식 : 파라미터 변수 받아 DB에 save() => book:list
    if request.method == 'POST':
        form = BookModelForm(request.POST)
        if form.is_valid(): # 유효성 검사
            # book = Book(**form.cleaned_data)
            # book.ip = request.META['REMOTE_ADDR'] # 요청한 client의 ip
            
            book = form.save(commit = False) # 저장하지 않고 전달하는 방식
            book.ip = request.META['REMOTE_ADDR'] # 요청한 client의 ip
            book.save()
            
            return redirect(book) # book.get_absoute_url()의 return값 적용
        
        # else:
        #     return render(request, "book/book_form.html", {'form':form})
        
        # print('★ form.is_valid :', form.is_valid()) # 유효성 검증 결과
        # print('유효성 검사 결과', form.cleaned_data)

        # title = request.POST.get('title')
        # author = request.POST['author']
        # publisher = request.POST['publisher']
        # sales = int(request.POST['sales'])
        # ip = request.META['REMOTE_ADDR'] # 요청한 client의 ip
        # book = Book(title=title,
        #             author=author,
        #             publisher=publisher,
        #             sales=sales,
        #             ip=ip)
        # book.save()
        # return redirect(book) # book.get_absoute_url()의 return값 적용
    
    elif request.method == 'GET':
        form = BookModelForm()

    #     return render(request, "book/book_form.html", {'form':form})
    
    return render(request, "book/book_form.html", {'form':form})

book_edit = UpdateView.as_view(model=Book,
                                fields = ['title', 'author', 'publisher', 'sales'])

def book_edit1(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookModelForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save() # 수정시 ip수정x / 수정하려면 commit=False + 아래 2줄 적용
            return redirect(book)
            # book.ip = request.META['REMOTE_ADDR'] # 요청한 client의 ip
            # book.save()
    elif request.method == 'GET':
        form = BookModelForm(instance=book)
        return render(request, 'book/book_form.html', {'form': form})

book_delete = DeleteView.as_view(model=Book, 
                                # template_name = "~",
                                success_url=reverse_lazy('book:list'))

def book_delete1(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect(book)
    elif request.method == 'GET':
        return render(request, 'book/book_confirm_delete.html', {'object': book})