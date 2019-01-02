from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User

from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render,redirect,get_object_or_404

from django.template.loader import get_template

from django.utils import timezone
from django.utils.decorators import method_decorator

from django.views.generic import UpdateView, ListView, CreateView, DeleteView

from .models import NewsLetterUser, NewsLetter
from .forms import NewsLetterUserSignupForm, NewsLetterCreationForm


def newsletter_signup(request):
    form = NewsLetterUserSignupForm(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        if NewsLetterUser.objects.filter(email=instance.email).exists():
            messages.warning(request, 'You have already subscibed to our mailing service')
        
        else:        
            instance.save()
            messages.success(request, 'You have successfully subscribed to our mailing service')
            subject = "Thanks for joining our Newsletter"
            from_email = settings.EMAIL_HOST_USER
            to_email = [instance.email]
            #with open(settings.BASE_DIR + "/templates/newsletter/sign_up_email.txt") as f:
            #    signup_message = f.read()
            signup_message='''Welcome to our website
            Thanks for Joining
            To unsubscribe click the this link http://127.0.0.1:8000/newsletter/unsubscribe/'''
            message = EmailMultiAlternatives(subject=subject, body=signup_message, from_email=from_email, to=to_email)
            html_template = get_template("newsletter/sign_up_email.html").render()
            message.attach_alternative(html_template, "text/html")
            message.send()
    context = {
            'form':form,
    }
    return render(request, 'newsletter/sign_up.html', context)


def newsletter_unsubscribe(request):
    form = NewsLetterUserSignupForm(request.POST or None)

    if form.is_valid():
        instance = form.save(commit=False)
        if NewsLetterUser.objects.filter(email=instance.email).exists():
            NewsLetterUser.objects.filter(email=instance.email).delete()
            messages.success(request, 'Your email has successfully removed from our mailing service')
            subject = "You have been unsubscribed"
            from_email = settings.EMAIL_HOST_USER
            to_email = [instance.email]
            #with open(settings.BASE_DIR + "/templates/newsletter/unsubscribe_email.txt") as f:
            #    signup_message = f.read()
            signup_message='''Welcome to our website
            Thanks for Joining
            To unsubscribe click the this link http://127.0.0.1:8000/newsletter/unsubscribe/'''

            message = EmailMultiAlternatives(subject=subject, body=signup_message, from_email=from_email, to=to_email)
            html_template = get_template("newsletter/unsubscribe_email.html").render()
            message.attach_alternative(html_template, "text/html")
            message.send()
        else:
            messages.warning(request, 'You email is not subscibed to our mailing service')            
    context = {
            'form':form,
    }
    return render(request, 'newsletter/unsubscribe.html', context)
    

@staff_member_required
def control_newsletter(request):
    form = NewsLetterCreationForm(request.POST or None)
    
    if form.is_valid():
        instance = form.save()
        newsletter = NewsLetter.objects.get(id=instance.id)
        if newsletter.status == "Published":
            subject = newsletter.subject
            body = newsletter.body
            from_email = settings.EMAIL_HOST_USER
            for email in newsletter.email.all():
                send_mail(subject=subject, from_email=from_email, recipient_list=[email.email], message=body, fail_silently=True)
            messages.success(request, 'Newsletter successfully send')
            return redirect('control_panel:control_newsletter_list')
        messages.success(request, 'Newsletter successfully Saved')
        return redirect('control_panel:control_newsletter_list')
    
    context={
        "form":form,
    }
    return render(request, "control_panel/control_newsletter.html", context)
    

#Not in use    
def control_newsletter_list(request):    
    newsletters = NewsLetter.objects.all()

    paginator = Paginator(newsletters, 1)
    page = request.GET.get('page', 1)

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        "questions": items, 
        "newsletters": newsletters, 
    }
    return render(request, 'control_panel/control_newsletter_list.html', context)    
    

@method_decorator(staff_member_required, name='dispatch')
class NewsletterListView(ListView):
    model = NewsLetter
    paginate_by = 10
    template_name = 'control_panel/control_newsletter_list.html'
    context_object_name = 'newsletters'


@staff_member_required
def newsletter_detail(request, pk):
    newsletter = get_object_or_404(NewsLetter, pk=pk)
    args = {
        'newsletter':newsletter,
    }
    return render(request, 'control_panel/control_newsletter_detail.html', args)


# Newsletter Edit view but not in use right now
class NewsletterEditView(UpdateView):
    model = NewsLetter
    fields = ['subject', 'body', 'email', 'status',]
    template_name = 'control_panel/control_newsletter_edit.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'newsletter'

    def form_valid(self, form):
        newsletter = form.save(commit=False)
        newsletter.updated = timezone.now()
        newsletter.save()
        messages.success(self.request, 'Question successfully updated')
        return redirect('control_panel:control_newsletter_detail', pk=newsletter.pk)
        # return redirect('main:question', pk=question.pk)


@staff_member_required
def control_newsletter_edit(request, pk):
    newsletter = get_object_or_404(NewsLetter, pk=pk)
    if request.method == 'POST':
        form = NewsLetterCreationForm(request.POST , instance = newsletter)
    
        if form.is_valid():
            newsletter = form.save()

            if newsletter.status == "Published":
                subject = newsletter.subject
                body = newsletter.body
                from_email = settings.EMAIL_HOST_USER
                for email in newsletter.email.all():
                    send_mail(subject=subject, from_email=from_email, recipient_list=[email.email], message=body, fail_silently=True)
                messages.success(request, 'Newsletter successfully send')
                return redirect('control_panel:control_newsletter_detail', pk=newsletter.pk)
            messages.success(request, 'Newsletter successfully Saved')
            return redirect('control_panel:control_newsletter_detail', pk=newsletter.pk)
    else:
        form = NewsLetterCreationForm(instance = newsletter)    
        context={
            "form":form,
        }
        return render(request, "control_panel/control_newsletter_edit.html", context)


@method_decorator(staff_member_required, name='dispatch')
class NewsletterDeleteView(DeleteView):
    model = NewsLetter
    success_url = '/'
    template_name = 'control_panel/control_newsletter_delete.html'



    
    
    
    
    
    
    
    
        
