from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User

from django.conf import settings

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, send_mass_mail

from django.db.models import Q

from django.template.loader import get_template
from django.shortcuts import render,redirect,get_object_or_404

from django.utils.decorators import method_decorator
from django.utils import timezone

from django.views.generic import UpdateView, ListView, CreateView, DeleteView


from main.models import Question, Answer, ContactUs, NewsLetter
from main.forms import QuestionForm, AnswerForm, NewsLetterForm

# This is the format of sending email
def email(request):
    subject = 'Thank you for posting question to our site'
    message = ' it  means a world to us '
    email_from = 'shekharnunia@gmail.com'
    recipient_list = [self.request.user.email,]
    if self.request.user.email == email_from:
        return redirect('main:home')
    else:
        send_mail( subject, message, email_from, recipient_list, fail_silently = False )
        return redirect('main:home')


def questionlistview(request):
    queryset_list = Question.objects.all().order_by('-pk')
    form = NewsLetterForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            form = form.save()
            messages.success(request, "Your Email has Successfully Submitted")
        else:
            messages.warning(request, "Wrong Email or Email Already Exist")


    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
                Q(topic__icontains=query)|
                Q(question__icontains=query)|
                Q(created_by__username__icontains=query) 
                ).distinct()

    paginator = Paginator(queryset_list, 10)
    page = request.GET.get('page', 1)

    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    context = {
        "questions": queryset, 
        'form': NewsLetterForm,
    }
    return render(request, 'main/home.html', context)



class QuestionListView(ListView):
    model = Question
    queryset = Question.objects.all().order_by('-pk')
    paginate_by = 10
    template_name = 'main/home.html'
    context_object_name = 'questions'

    def get_queryset(self):
        try:
            name = self.kwargs['q']
        except:
            name = ''
        if (name != ''):
            object_list = self.model.objects.filter(name__icontains = q)
        else:
            object_list = self.model.objects.all()
        return object_list


@method_decorator(login_required, name='dispatch')
class CreateQuestionView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'main/ask_question.html'
    
    def form_valid(self, form):
        new_question = form.save(commit=False)
        new_question.created_by = self.request.user
        new_question.save()
        messages.success(self.request, 'Question successfully created')

        subject = 'Thank you for posting question to Website'
        email_from = 'settings.EMAIL_HOST_USER'
        recipient_list = [self.request.user.email,]

        context = {
                'question_user': new_question.created_by,
                'link': new_question.get_absolute_url()
            }
        context_message = get_template('question_mail.txt').render(context)
        send_mail( subject, context_message, email_from, recipient_list, fail_silently = True )
        return redirect('main:home')
        # return redirect(new_question.get_absolute_url())


def question(request, pk):
    form = AnswerForm(request.POST)
    question = get_object_or_404(Question, pk=pk)
    # question.question_views += 1

    answer = Answer.objects.filter(question_a=question)
    if request.method == 'POST':
        if form.is_valid() and request.user.is_authenticated:
            answer = form.save(commit=False)
            answer.question_a = question
            answer.answer_by = request.user
            answer = form.save()
            messages.success(request, 'Answer successfully submitted')

            subject = 'There is a Answer uploaded for your Question'
            email_from = 'settings.EMAIL_HOST_USER'
            recipient_list = [question.created_by.email,]

            context = {
                'question_user': question.created_by,
                'answer_user': request.user,
            }
            context_message = get_template('answer_mail.txt').render(context)
            send_mail( subject, context_message, email_from, recipient_list, fail_silently = True )
            return redirect(answer.get_absolute_url())
        else:
            messages.warning(request, 'Login first')
            return redirect(question.get_absolute_url())
    form = AnswerForm()
    args = {
        'question':question,
        'form':form,
        'answers':answer
    }
    return render(request, 'main/question.html', args)


@method_decorator(login_required, name='dispatch')
class QuestionEditView(UserPassesTestMixin, UpdateView):
    model = Question
    fields = ('question',)
    template_name = 'main/edit_question.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'question'

    def form_valid(self, form):
        question = form.save(commit=False)
        question.created_by = self.request.user
        question.updated_at = timezone.now()
        question.save()
        messages.success(self.request, 'Question successfully updated')
        return redirect(question.get_absolute_url())
        # return redirect('main:question', pk=question.pk)

    def test_func(self):
        question = self.get_object()
        if self.request.user == question.created_by:
            return True
        return False


def delete_question(request, pk=None):
    instance = get_object_or_404(Question, pk=pk)
    if instance.created_by == request.user:
        instance.delete()
        messages.success(request, 'Question successfully deleted')
        return redirect('main:home')
    else:
        messages.warning(request, 'You not allowed to delete this question')
        return redirect(instance.get_absolute_url())


@method_decorator(login_required, name='dispatch')
class DeleteQuestionView(UserPassesTestMixin, DeleteView):
    model = Question
    success_url = '/'

    def test_func(self):
        question = self.get_object()
        if self.request.user == question.created_by:
            return True
        return False


@method_decorator(login_required, name='dispatch')
class AnswerEditView(UserPassesTestMixin, UpdateView):
    model = Answer
    fields = ('answer',)
    template_name = 'main/edit_answer.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'answer'

    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.answer_by = self.request.user
        answer.updated_at = timezone.now()
        messages.success(self.request, 'Answer successfully updated')
        answer.save()
        return redirect(answer.get_absolute_url())
        # return redirect('main:question', pk=answer.question_a.pk)

    def test_func(self):
        answer = self.get_object()
        if self.request.user == answer.answer_by:
            return True
        return False


def delete_answer(request, pk=None):
    instance = get_object_or_404(Answer, pk=pk)
    if instance.answer_by == request.user:
        instance.delete()
        messages.success(request, 'Answer successfully deleted')
        return redirect('main:home')
    else:
        messages.warning(request, 'You not allowed to delete this answer')
        return redirect(instance.get_absolute_url())


@method_decorator(login_required, name='dispatch')
class DeleteAnswerView(UserPassesTestMixin, DeleteView):
    model = Answer
    pk_url_kwarg = 'pk'
    success_url = '/'

    def test_func(self):
        answer = self.get_object()
        if self.request.user == answer.answer_by:
            return True
        return False


def privacy_policy(request):
    return render(request, 'main/privacy_policy.html', {})


def term_and_conditions(request):
    return render(request, 'main/term_and_conditions.html', {})


class ContactUs(CreateView):
    model = ContactUs
    template_name = 'main/contact_us.html'
    fields = ('name', 'email', 'message',)
    
    def form_valid(self, form):
        contact_us = form.save(commit=False)
        contact_us.save()


	# one mail for website admins
        subject_for_admin = 'Some is trying to contact to your website'
        email_from = 'settings.EMAIL_HOST_USER'
        recipient_list_for_admin = [settings.EMAIL_HOST_USER,]
        context_message_for_admin = contact_us.message
#        send_mail( subject_for_admin, context_message_for_admin, email_from, recipient_list_for_admin, fail_silently = True )


	# one mail for uploader
        subject = 'We got your email'
        recipient_list = [contact_us.email,]
        context_message = 'We will get your message and we will try to get back to you as fast as possible' 
 #       send_mail( subject, context_message, email_from, recipient_list, fail_silently = True )

        message1 = (subject_for_admin, context_message_for_admin, email_from, recipient_list_for_admin)
        message2 = (subject, context_message, email_from, recipient_list)
        send_mass_mail((message1, message2),  fail_silently = True)



        messages.success(self.request, 'Successfully Submitted.')
        return redirect('main:home')











#		Method to send mails in HTML


#from django.core.mail import EmailMultiAlternatives
#from django.template.loader import get_template
#from django.template import Context

#plaintext = get_template('email.txt')
#htmly     = get_template('email.html')

#d = Context({ 'username': username })

#subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
#text_content = plaintext.render(d)
#html_content = htmly.render(d)
#msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
#msg.attach_alternative(html_content, "text/html")
#msg.send()


#		OR



#from django.core.mail import send_mail
#from django.template.loader import render_to_string


#msg_plain = render_to_string('templates/email.txt', {'some_params': some_params})
#msg_html = render_to_string('templates/email.html', {'some_params': some_params})

#send_mail(
#    'email title',
#    msg_plain,
#    'some@sender.com',
#    ['some@receiver.com'],
#    html_message=msg_html,
#)
