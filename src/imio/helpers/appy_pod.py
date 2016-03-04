from os import path
from Products.Five.browser import BrowserView
from plone import api
from plone.dexterity.interfaces import IDexterityContent


class AppyPodSampleHTML(BrowserView):
    """Load sample HTML to test appy.pod in a given XHTML field."""

    def __call__(self, field_name):
        """Load appy_pod.html into context's p_field_name XHTML field."""
        plone_utils = api.portal.get_tool('plone_utils')
        file_path = path.join(path.dirname(__file__), 'appy_pod.html')
        data = open(file_path, 'r')
        filled = False
        if IDexterityContent.providedBy(self.context):
            # dexterity
            pass
        else:
            # Archetypes
            field = self.context.getField(field_name)
            if field and field.widget.getName() == 'RichWidget':
                field.getMutator(self.context)(data.read(), content_type='text/html')
                filled = True
        data.close()
        if filled:
            plone_utils.addPortalMessage("Field '{0}' has been filled.".format(field_name))
        else:
            plone_utils.addPortalMessage(
                "Field named '{0}' is not a field to store XHTML content!".format(field_name),
                type="error")
        self.request.RESPONSE.redirect(self.context.absolute_url())
