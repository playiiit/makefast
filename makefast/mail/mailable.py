from typing import Dict, Any

class Mailable:
    # Class attributes to handle cases where super().__init__() is not called
    _view = None
    _data = None
    _subject = ""
    _to = None

    def __init__(self):
        self._view = None
        self._data = {}
        self._subject = ""
        self._to = None

    def _ensure_data_initialized(self):
        if self._data is None:
            self._data = {}

    def to(self, email_address: str):
        """
        Set the recipient email address.
        """
        self._to = email_address
        return self

    def view(self, template_name: str):
        """
        Set the template view name.
        Uses dot notation e.g., 'emails.welcome' maps to 'resources/views/emails/welcome.html'.
        """
        self._view = template_name
        return self

    def with_data(self, data: dict = None, **kwargs):
        """
        Pass data to the view.
        """
        self._ensure_data_initialized()
        if data:
            self._data.update(data)
        if kwargs:
            self._data.update(kwargs)
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

    def send(self, to_email: str = None):
        """
        Send the mailable.
        """
        from .mailer import Mail
        
        recipient = to_email or self._to
        if not recipient:
            raise ValueError("No recipient specified. Use .to() or pass an email to .send()")
            
        return Mail.to(recipient).send(self)
