# -*- coding: utf-8 -*-
from django.test import TestCase, tag

from oldp.apps.laws.models import Law
from oldp.apps.laws.processing.processing_steps.extract_refs import ExtractLawRefs


@tag('processing')
class LawProcessingTest(TestCase):
    fixtures = ['laws/laws.json']

    def __init__(self, *args, **kwargs):
        super(LawProcessingTest, self).__init__(*args, **kwargs)

    def setUp(self):
        pass

    def tearDown(self):
        # os.remove(self.temp_path)
        pass

    def test_extract_refs(self):
        content = Law.objects.get(book__slug='ublg-1', slug='12')
        # print(content)
        # print(content.get_reference_markers())

        step = ExtractLawRefs()
        processed = step.process(content)

        # print(processed)
        # print(processed.reference_markers)

        self.assertEqual(len(processed.get_reference_markers()), 1, 'Invalid number of reference markers')
        # self.assertEqual(processed.get_reference_markers()[0].referenced_by, content, 'Invalid reference markers by')
        # self.assertEqual(processed.get_reference_markers()[0].start, 764, 'Invalid reference markers start')
        # self.assertEqual(processed.get_reference_markers()[0].end, 767, 'Invalid reference markers end')

    def test_extract_refs_detail(self):
        text = '<P>Anforderungsbeh&#246;rden gem&#228;&#223; § 5 Abs. 1 und § 79 Satz 1 des Bundesleistungs' \
               'gesetzes sind, soweit in §§ 2 bis 4 nichts anderes bestimmt ist, die Beh&#246;rden der allgemeinen ' \
               'Verwaltung auf der Kreisstufe.</P>'

        law = Law.objects.get(book__slug='ublg-1', slug='12')
        law_processed = ExtractLawRefs().process(law)

        # print('Original: %s' % text)
        # print('\nMarker: %s' % ref_text)

        # self.assertEqual(len(law_processed.get_references()), 3, 'Invalid number of reference markers')

        # TODO Reference count?

        # print(refs)


