import hashlib
import logging
import re

from django.db import models

from oldp.apps.cases.models import Case
from oldp.apps.laws.models import Law

logger = logging.getLogger(__name__)


class Reference(models.Model):
    """

    A reference connecting two content objects (1:1 relation). The object that is referenced is either "law", "case"
    or ... (reference target). The referencing object (the object which text contains the reference) can be derived
    via marker.

    Depending on the referencing object (its marker) the corresponding implementation is used.

    If the referenced object is not defined, the reference is "not assigned" (is_assigned method)

    """
    law = models.ForeignKey(Law, null=True, on_delete=models.SET_NULL)
    case = models.ForeignKey(Case, null=True, on_delete=models.SET_NULL)
    to = models.CharField(max_length=250)  # to as string, if case or law cannot be assigned (ref id)
    to_hash = models.CharField(max_length=100, null=True)
    count = None

    class Meta:
        pass

    def get_marker(self):
        """Reverse m2m-field look up"""
        marker = self.casereferencemarker_set.first()

        if marker is None:
            marker = self.lawreferencemarker_set.first()

        return marker

    def get_absolute_url(self):
        """
        Returns Url to law or case item (if exist) otherwise return search Url.

        :return:
        """
        if self.law is not None:
            return self.law.get_absolute_url()
        elif self.case is not None:
            return self.case.get_absolute_url()
        else:
            return '/search/?q=%s' % self.get_marker().text

    def get_target(self):
        if self.law is not None:
            return self.law
        elif self.case is not None:
            return self.case
        else:
            return None

    def get_title(self):
        # TODO handle unassigned refs
        if self.law is not None:
            return self.law.get_title()
        elif self.case is not None:
            return self.case.get_title()
        else:
            return self.to  # TODO
            # to = json.loads(self.to)
            # to['sect'] = str(to['sect'])
            #
            # if to['type'] == 'law' and 'book' in to and 'sect' in to:
            #     print(to)
            #     if to['book'] == 'gg':
            #         sect_prefix = 'Art.'
            #     elif 'anlage' in to['sect']:
            #         sect_prefix = ''
            #     else:
            #         sect_prefix = '§'
            #     to['sect'] = to['sect'].replace('anlage-', 'Anlage ')
            #     return sect_prefix + ' ' + to['sect'] + ' ' + to['book'].upper()
            # else:
            #     return self.get_marker().text

    def is_assigned(self):
        return self.law is not None or self.case is not None

    def set_to_hash(self):
        m = hashlib.md5()
        m.update(self.to.encode('utf-8'))

        self.to_hash = m.hexdigest()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.count:
            return '<Reference(count=%i, to=%s, hash=%s)>' % (self.count, self.to, self.to_hash)
        else:
        #     return self.__dict__
            return '<Reference(%s, target=%s)>' % (self.to, self.get_target())


class ReferenceMarker(models.Model):
    """
    Abstract class for reference markers, i.e. the actual reference within a text "§§ 12-14 BGB".

    Marker has a position (start, end, line), unique identifier (uuid, randomly generated), text of the marker as in
    the text, list of references (can be law, case, ...). Implementations of abstract class (LawReferenceMarker, ...)
    have the corresponding source object (LawReferenceMarker: referenced_by = a law object).

    """
    text = models.CharField(max_length=250)  # Text of marker
    uuid = models.CharField(max_length=36)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    line = models.CharField(blank=True, max_length=200)
    referenced_by = None
    referenced_by_type = None
    references = models.ManyToManyField(Reference)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO Handle ids with signals?

    def get_referenced_by(self):
        raise NotImplementedError()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'RefMarker(ids=%s, line=%s, pos=%i-%i, by=%s)' % ('self.ids', self.line, self.start, self.end, self.referenced_by)

    @staticmethod
    def remove_markers(value):
        return re.sub(r'\[ref=([-a-z0-9]+)\](.*?)\[\/ref\]', r'\2', value)

    @staticmethod
    def make_markers_clickable(value):
        """
        TODO Replace ref marker number with db id
        """
        return re.sub(r'\[ref=([-a-z0-9]+)\](.*?)\[\/ref\]', r'<a href="#refs" onclick="clickRefMarker(this);" data-ref-uuid="\1" class="ref">\2</a>', value)


class LawReferenceMarker(ReferenceMarker):
    """

    A reference marker in a law content object.

    """
    referenced_by_type = Law
    referenced_by = models.ForeignKey(Law, on_delete=models.CASCADE)

    def get_referenced_by(self) -> Law:
        return self.referenced_by


class CaseReferenceMarker(ReferenceMarker):
    """

    A reference marker in a case content object.

    """
    referenced_by_type = Case
    referenced_by = models.ForeignKey(Case, on_delete=models.CASCADE)

    def get_referenced_by(self) -> Case:
        return self.referenced_by
