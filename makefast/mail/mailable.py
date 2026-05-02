from typing import Dict, Any

class Mailable:
    def __init__(self):
        self._view = None
        self._data: Dict[str, Any] = {}
        self._subject = ""

    def view(self, template_name: str):
        """
        Set the template view name.
        Uses dot notation e.g., 'emails.welcome' maps to 'resources/views/emails/welcome.html'.
        """
        self._view = template_name
        return self

    def with_data(self, **data):
        """
        Pass data to the view.
        """
        self._data.update(data)
        return self

    def subject(self, subject_text: str):
        """
        Set the email subject.
        """
        self._subject = subject_text
        return self

    def build(self):
        """
        Configure the mailable. 
        Override this method in your subclass.
        """
        pass
