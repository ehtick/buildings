from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.urls import reverse
from django.core.validators import FileExtensionValidator

from filebrowser.fields import FileBrowseField
from filebrowser.base import FileObject
from treebeard.mp_tree import MP_Node

from .map_utils import workflow

from django.utils.text import slugify

def generate_unique_slug(klass, field, id):
    """
    return unique slug if origin slug exists.
    eg: `foo-bar` => `foo-bar-1`

    :param `klass` is Class model.
    :param `field` is specific field for title.
    Thanks to djangosnippets.org!
    """
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    if klass == Building:
        while klass.objects.filter(slug=unique_slug).exists():
            unique_slug = '%s-%d' % (origin_slug, numb)
            numb += 1
    else:
        while klass.objects.filter(slug=unique_slug, build_id=id).exists():
            unique_slug = '%s-%d' % (origin_slug, numb)
            numb += 1
    return unique_slug

def building_default_intro():
    return _('Another Building by %(website)s!') % {'website': settings.WEBSITE_NAME}

class Building(models.Model):
    slug = models.SlugField(max_length=100, editable=False, null=True)
    image = models.ImageField(_("Image"), max_length=200,
        null=True, blank=True, upload_to='uploads/buildings/images/')
    fb_image = FileBrowseField(_("Image"), max_length=200,
        extensions=[".jpg", ".png", ".jpeg", ".gif", ".tif", ".tiff"],
        null=True, directory='buildings/images/')
    title = models.CharField(_('Title'),
        help_text=_("Building name"),
        max_length = 50, null=True, blank=True)
    intro = models.CharField(_('Introduction'),
        default = building_default_intro,
        help_text = _('Few words to describe this building'),
        max_length = 100)
    date = models.DateField(_('Date'), default = now, )
    last_updated = models.DateTimeField(editable=False, null=True)
    address = models.CharField(_('Address'), null=True, blank=True,
        help_text = _('Something like "Rome - Monteverde" is ok'),
        max_length = 100)
    lat = models.FloatField(_("Latitude"), default = settings.CITY_LAT)
    long = models.FloatField(_("Longitude"), default = settings.CITY_LONG,
        help_text=_("Coordinates from Google Maps or https://openstreetmap.org"))
    zoom = models.FloatField(_("Zoom factor"), default = settings.CITY_ZOOM,
        help_text=_("Maximum should be 23"))

    def __str__(self):
        return self.title

    def get_full_path(self):
        return reverse('buildings:building_detail',
            kwargs={'build_slug': self.slug, 'set_slug': 'base_'+str(self.id)})

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = _('Building-%(date)s') % {'date': self.date.strftime("%d-%m-%y")}
        if not self.slug:
            self.slug = generate_unique_slug(Building, self.title, 0)
        self.last_updated = now()
        super(Building, self).save(*args, **kwargs)
        if self.image:
            #this is a sloppy workaround to make working test
            #image is saved on the front end, passed to fb_image and deleted
            Building.objects.filter(id=self.id).update(image=None,
                fb_image=FileObject(str(self.image)))
        try:
            PlanSet.objects.get(slug='base_'+str(self.id), build_id=self.id)
        except:
            PlanSet.add_root(title=self.title, slug='base_'+str(self.id),
                build=self)

    class Meta:
        verbose_name = _('Building')
        verbose_name_plural = _('Buildings')
        ordering = ('-date', )

class Plan(models.Model):

    build = models.ForeignKey(Building, on_delete = models.CASCADE,
        related_name='building_plan', verbose_name = _('Building'))
    title = models.CharField(_('Name'),
        help_text=_("Name of the building plan"), max_length = 50, )
    slug = models.SlugField(max_length=100, editable=False, null=True)
    elev = models.FloatField(_("Elevation in meters"), default = 0)
    file = models.FileField(_("DXF file"), max_length=200,
        upload_to="uploads/buildings/plans/dxf/",
        validators=[FileExtensionValidator(allowed_extensions=['dxf', ])],
        null=True, blank=True )
    refresh = models.BooleanField(_("Refresh geometry"), default=True)
    geometry = models.JSONField( null=True, blank=True )
    visible = models.BooleanField(_("Visible"), default=False,
        help_text=_("Check if plan is immediately visible"))

    def __str__(self):
        return self.title + ' | ' + str(self.elev)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Plan,
                self.title + ' ' + str(self.elev), self.build.id)
        #upload file
        super(Plan, self).save(*args, **kwargs)
        if self.refresh and self.file:
            geometry = workflow(self.file, self.build.lat, self.build.long)
            #this is a sloppy workaround to make working test
            #geometry refreshed
            Plan.objects.filter(id=self.id).update(geometry=geometry,
                refresh=False)

    class Meta:
        verbose_name = _('Building plan')
        verbose_name_plural = _('Building plans')
        ordering = ('-elev', )

class PlanSet(MP_Node):
    build = models.ForeignKey(Building, on_delete = models.CASCADE,
        related_name='building_planset', verbose_name = _('Building'))
    parent = models.ForeignKey('self', verbose_name = _('Parent set'),
        null=True, blank=True,
        help_text = _('Choose carefully, can be changed only by staff in admin'),
        on_delete = models.SET_NULL)
    title = models.CharField(_('Title'),
        help_text=_("Set name"),
        max_length = 50, )
    intro = models.CharField(_('Description'),
        null=True, blank=True,
        help_text = _('Few words to describe the set'),
        max_length = 100)
    slug = models.SlugField(max_length=100, editable=False, null=True)
    plans = models.ManyToManyField(Plan,
        blank = True, verbose_name = _('Plans'),
        help_text=_("Choose plans to show in this set") )

    def __str__(self):
        prefix = ''
        for i in range( self.depth -1 ):
            prefix = prefix + '-'
        return prefix + self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(PlanSet, self.title, self.build.id)
        self.last_updated = now()
        super(PlanSet, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Plan set')
        verbose_name_plural = _('Plan sets')
        ordering = ('build', 'path')

def photo_station_default_intro():
    return (_('Another photo station by %(sitename)s!') %
        {'sitename': settings.WEBSITE_NAME})

class PhotoStation(models.Model):

    build = models.ForeignKey(Building, on_delete = models.CASCADE,
        related_name='building_station', verbose_name = _('Building'))
    plan = models.ForeignKey(Plan, on_delete = models.SET_NULL,
        related_name='plan_station', verbose_name = _('Building plan'),
        null=True, blank=True)
    title = models.CharField(_('Title'),
        help_text=_("Title of the photo station"), max_length = 50, )
    slug = models.SlugField(max_length=100, editable=False, null=True)
    intro = models.CharField(_('Description'),
        default = photo_station_default_intro,
        max_length = 100)
    lat = models.FloatField(_("Latitude"), null=True, blank=True)
    long = models.FloatField(_("Longitude"), null=True, blank=True)

    def __str__(self):
        return self.title + ' / ' + self.build.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(PhotoStation, self.title,
                self.build.id)
        if not self.lat:
            self.lat = self.build.lat
        if not self.long:
            self.long = self.build.long
        super(PhotoStation, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Photo station')
        verbose_name_plural = _('Photo stations')
        ordering = ('build', 'title')

class StationImage(models.Model):
    stat = models.ForeignKey(PhotoStation, null=True,
        on_delete = models.CASCADE, related_name='station_image',
        verbose_name = _('Station'))
    date = models.DateTimeField(_('Date:'), default = now, )
    image = models.ImageField(_("Image"), max_length=200,
        null=True, blank=True, upload_to='uploads/buildings/images/')
    fb_image = FileBrowseField(_("Image"), max_length=200,
        extensions=[".jpg", ".png", ".jpeg", ".gif", ".tif", ".tiff"],
        null=True, directory='buildings/images/')
    caption = models.CharField(_("Caption"), max_length = 200, blank=True,
        null=True)

    def save(self, *args, **kwargs):
        #save and upload image
        super(StationImage, self).save(*args, **kwargs)
        if self.image:
            #this is a sloppy workaround to make working test
            #image is saved on the front end, passed to fb_image and deleted
            StationImage.objects.filter(id=self.id).update(image=None,
                fb_image=FileObject(str(self.image)))

    class Meta:
        verbose_name=_("Image")
        verbose_name_plural=_("Images")
        ordering = ('-date', )
