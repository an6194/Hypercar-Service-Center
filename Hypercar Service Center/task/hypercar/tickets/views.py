from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from collections import deque

menu = {
        'change_oil': 'Change oil',
        'inflate_tires': 'Inflate tires',
        'diagnostic': 'Get diagnostic test',
    }
queue = dict()
for key in menu.keys():
    queue[key] = deque()
ticket_id = 0
next_ticket = 0


class WelcomeView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        with open('index.html') as ans:
            welcome_text = ans.readlines()
        return HttpResponse(welcome_text)


class MenuPage(View):
    template_name = 'menu_template.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'menu': menu})


class ResultPage(View):
    template_name = 'queue_template.html'

    @staticmethod
    def count_minutes(ticket_action):
        total_minutes = 0
        for action in queue:
            if action == 'change_oil':
                total_minutes += len(queue[action]) * 2
            elif action == 'inflate_tires' \
                    and ticket_action != 'change_oil':
                total_minutes += len(queue[action]) * 5
            elif action == 'diagnostic' \
                    and ticket_action != 'change_oil' \
                    and ticket_action != 'inflate_tires':
                total_minutes += len(queue[action]) * 30
        return total_minutes

    def get(self, request, action, *args, **kwargs):
        global ticket_id
        minutes_to_wait = self.count_minutes(action)
        ticket_id += 1
        queue[action].append(ticket_id)
        return render(request, self.template_name,
                      context={
                          'ticket_number': ticket_id,
                          'minutes_to_wait': minutes_to_wait
                      })


class ProcessPage(View):
    template_name = 'operator_template.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,
                      context={'queue': queue})

    def post(self, request, *args, **kwargs):
        global next_ticket
        next_ticket = 0
        if len(queue['change_oil']) != 0:
            next_ticket = queue['change_oil'].popleft()
        elif len(queue['inflate_tires']) != 0:
            next_ticket = queue['inflate_tires'].popleft()
        elif len(queue['diagnostic']) != 0:
            next_ticket = queue['diagnostic'].popleft()
        return redirect('/next')


class NextPage(View):
    template_name = 'next_ticket_template.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,
                      context={'ticket_number': next_ticket})
