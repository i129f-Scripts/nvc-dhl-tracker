import django.dispatch

pre_dhl_request_made = django.dispatch.Signal()
post_dhl_request_made = django.dispatch.Signal()
google_request_made = django.dispatch.Signal()
