from django import template
from django.template.defaultfilters import urlencode
from front.utils import states


register = template.Library()


def get_staticmap_latlng(parser, token):
    try:
        func, address, lat, lng, width, height, zoom = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r' % token.split_contents()[0])

    return StaticMapNode(address=address, lat=lat, lng=lng, width=width, height=height, zoom=zoom)

get_staticmap_latlng = register.tag(get_staticmap_latlng)


def get_staticmap(parser, token):
    try:
        func, address, state, width, height, zoom = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r' % token.split_contents()[0])
    
    return StaticMapNode(address=address, state=state, width=width, height=height, zoom=zoom)

get_staticmap = register.tag(get_staticmap)


class StaticMapNode(template.Node):
    def __init__(self, address, state=None, lat=None, lng=None, width=None, height=None, zoom=None):
        self.address = address
        self.state = state
        self.lat = lat
        self.lng = lng
        self.width = width
        self.height = height
        self.zoom = zoom
    
    def render(self, context):
        address = template.Variable(self.address).resolve(context)
        state = None if self.state is None else template.Variable(self.state).resolve(context)
        lat = None if self.lat is None else template.Variable(self.lat).resolve(context)
        lng = None if self.lng is None else template.Variable(self.lng).resolve(context)

        # try to find the name of the state
        name = [s[1] for s in states if s[0] == state]
        if len(name) > 0:
            state = name[0]

        # build the urls
        if lat and lng:
            staticmap_url = "http://maps.googleapis.com/maps/api/staticmap?center=%s,%s&markers=%s,%s&zoom=%s&size=%sx%s&sensor=false" % (
                lat, lng, lat, lng, self.zoom, self.width, self.height)
            googlemaps_url = "http://maps.google.com/?q=%s" % urlencode(address)
        else:
            staticmap_url = "http://maps.googleapis.com/maps/api/staticmap?center=%s,%s&markers=%s,%s&zoom=%s&size=%sx%s&sensor=false" % (
                address, state, address, state, self.zoom, self.width, self.height)
            googlemaps_url = "http://maps.google.com/?q=%s" % urlencode("%s,%s" % (address, state))

        html = "<a href='%s' target='_blank' class='map-link'><img class='map-image' src='%s' /></a>" % (googlemaps_url, staticmap_url)
        return html
