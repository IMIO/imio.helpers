from os import path
from Products.Five.browser import BrowserView
from plone.dexterity.interfaces import IDexterityContent


class AppyPodSampleHTML(BrowserView):
    """Load sample HTML to test appy.pod in a given XHTML field."""

    def __call__(self, field_name):
        """Load appy_pod.html into context's p_field_name XHTML field."""
        file_path = path.join(path.dirname(__file__), 'appy_pod.html')
        data = open(file_path, 'r')
        # dexterity
        if IDexterityContent.providedBy(self.context):
            pass
        else:
            # Archetypes
            field = self.context.getField(field_name)
            field.getMutator(self.context)(data.read(), content_type='text/html')
        data.close()
