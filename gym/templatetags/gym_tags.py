from django import template
register = template.Library()

@register.filter
def money(value):
    return f'Q{value:,.2f}'

@register.filter
def badge(status):
    return {'Vigente': 'green', 'Por vencer': 'amber', 'Pago pendiente': 'amber', 'Programada': 'blue',
            'Vencida': 'red', 'Cancelada': 'muted'}.get(status, 'muted')


@register.simple_tag
def icon(name, css=''):
    """Inline reference to the local SVG sprite (static/gym/icons.svg); decorative by default."""
    from django.templatetags.static import static
    from django.utils.html import format_html
    return format_html('<svg class="i {}" aria-hidden="true" focusable="false"><use href="{}#i-{}"></use></svg>',
                       css, static('gym/icons.svg'), name)
