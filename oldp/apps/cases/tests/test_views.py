from django.test import LiveServerTestCase, tag
from django.urls import reverse


@tag('views')
class CasesViewsTestCase(LiveServerTestCase):
    fixtures = ['cases/courts.json']

    def test_index(self):
        res = self.client.get(reverse('cases:index'))

        self.assertEqual(res.status_code, 200)

