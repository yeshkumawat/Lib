from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import IssueBookForm
from .models import Book, IssuedBook, Student
from django.contrib.auth.models import User

def index(request):
    return render(request, "index.html")

@login_required(login_url='/admin_login')
def add_book(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']

        book = Book.objects.create(name=name, author=author, isbn=isbn, category=category)
        alert = True
        return render(request, "add_book.html", {'alert': alert})
    
    return render(request, "add_book.html")

@login_required(login_url='/admin_login')
def view_books(request):
    books = Book.objects.all()
    return render(request, "view_books.html", {'books': books})

@login_required(login_url='/admin_login')
def view_students(request):
    students = Student.objects.all()
    return render(request, "view_students.html", {'students': students})

@login_required(login_url='/admin_login')
def issue_book(request):
    form = IssueBookForm()
    if request.method == "POST":
        form = IssueBookForm(request.POST)
        if form.is_valid():
            obj = IssuedBook.objects.create(
                student_id=request.POST['name2'],
                isbn=request.POST['isbn2']
            )
            alert = True
            return render(request, "issue_book.html", {'obj': obj, 'alert': alert})
    
    return render(request, "issue_book.html", {'form': form})

@login_required(login_url='/admin_login')
def view_issued_book(request):
    issued_books = IssuedBook.objects.all()
    details = []

    for i in issued_books:
        days = (date.today() - i.issued_date).days
        fine = max(0, days - 7) * 5

        books = Book.objects.filter(isbn=i.isbn)
        students = Student.objects.filter(user=i.student_id)

        for book, student in zip(books, students):
            t = (student.user, student.user_id, book.name, book.isbn, i.issued_date, i.expiry_date, fine)
            details.append(t)

    return render(request, "view_issued_book.html", {'issued_books': issued_books, 'details': details})

@login_required(login_url='/student_login')
def student_issued_books(request):
    student = Student.objects.get(user=request.user)
    issued_books = IssuedBook.objects.filter(student_id=student.user_id)
    li1 = []
    li2 = []

    for i in issued_books:
        books = Book.objects.filter(isbn=i.isbn)
        for book in books:
            t = (request.user.id, request.user.get_full_name, book.name, book.author)
            li1.append(t)

        days = (date.today() - i.issued_date).days
        fine = max(0, days - 15) * 5
        t = (i.issued_date, i.expiry_date, fine)
        li2.append(t)

    return render(request, 'student_issued_books.html', {'li1': li1, 'li2': li2})

@login_required(login_url='/student_login')
def profile(request):
    return render(request, "profile.html")

@login_required(login_url='/student_login')
def edit_profile(request):
    student = Student.objects.get(user=request.user)
    if request.method == "POST":
        email = request.POST['email']
        phone = request.POST['phone']
        branch = request.POST['branch']
        classroom = request.POST['classroom']
        roll_no = request.POST['roll_no']

        student.user.email = email
        student.phone = phone
        student.branch = branch
        student.classroom = classroom
        student.roll_no = roll_no
        student.user.save()
        student.save()
        alert = True
        return render(request, "edit_profile.html", {'alert': alert})
    
    return render(request, "edit_profile.html")

def delete_book(request, myid):
    book = Book.objects.get(id=myid)
    book.delete()
    return redirect("/view_books")

def delete_student(request, myid):
    student = Student.objects.get(id=myid)
    student.delete()
    return redirect("/view_students")

def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']

        try:
            user = request.user
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                alert = True
                return render(request, "change_password.html", {'alert': alert})
            else:
                currpasswrong = True
                return render(request, "change_password.html", {'currpasswrong': currpasswrong})
        except User.DoesNotExist:
            pass
    
    return render(request, "change_password.html")

def student_registration(request):
    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        branch = request.POST['branch']
        classroom = request.POST['classroom']
        roll_no = request.POST['roll_no']
        image = request.FILES['image']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            passnotmatch = True
            return render(request, "student_registration.html", {'passnotmatch': passnotmatch})

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        student = Student.objects.create(user=user, phone=phone, branch=branch, classroom=classroom, roll_no=roll_no, image=image)
        alert = True
        return render(request, "student_registration.html", {'alert': alert})
    
    return render(request, "student_registration.html")

def student_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None and not user.is_superuser:
            login(request, user)
            return redirect("/profile")
        else:
            alert = True
            return render(request, "student_login.html", {'alert': alert})
    
    return render(request, "student_login.html")

def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("/add_book")
        else:
            alert = True
            return render(request, "admin_login.html", {'alert': alert})
    
    return render(request, "admin_login.html")

def Logout(request):
    logout(request)
    return redirect("/")
