from django import template

register = template.Library()


@register.simple_tag
def is_missed(log):
    if log.missed:
        return 'block'
    else:
        return 'none'


@register.simple_tag
def is_incoming(log, user):
    if not log.missed:
        if log.callee.mobileno == user:
            return 'block'
        else:
            return 'none'
    else:
        return 'none'


@register.simple_tag
def is_outgoing(log, user):
    if not log.missed:
        if log.caller.mobileno == user:
            return 'block'
        else:
            return 'none'
    else:
        return 'none'

