import django.dispatch

person_altered = django.dispatch.Signal(providing_args=["person"])
