# shrunk - Rutgers University URL Shortener

"""Application forms for shrunk."""

import re

from wtforms import Form, TextField, PasswordField, RadioField, validators
from flask_auth import LoginForm

import shrunk.filters


class LinkForm(Form):
    """A WTForm for creating and editing links.

    :Fields:
      - `long_url`: Text field for the original unshrunk URL
      - `title`: Text field for a descriptive link title
    """
    long_url = TextField("URL", validators=[
        validators.DataRequired("You need a link to shrink!"),
        validators.URL(require_tld=True, message="Please enter a valid URL.")
    ])
    title = TextField("Title", validators=[
        validators.DataRequired("Please enter a title.")
    ])
    rejected_regexes = []

    def __init__(self, form, banlist=None):
        """Initializes the form.

        :Parameters:
          - `form`: The form from an incoming request
          - `banlist` (optional): A list of strings to restrict, in addition to
            the default ones
        """
        super().__init__(form)
        if banlist:
            for r in banlist:
                LinkForm.rejected_regexes.append(re.compile(r))

    def validate_long_url(form, field):
        """Performs validation on the long_url field."""
        for regex in LinkForm.rejected_regexes:
            if regex.search(field.data):
                raise ValidationError("That URL is not allowed.")

    def to_json(self):
        """Exports the form"s fields into a JSON-compatible dictionary."""
        return {
            "long_url": self.long_url.data,
            "title": self.title.data
        }


class RULoginForm(LoginForm):
    """A WTForm representing the login form.

    :Fields:
      - `username`: Text field for the user's NetID
      - `password`: Password field for a NetID password
    """
    username = TextField("Netid", validators=[validators.DataRequired()])
    password = PasswordField("Password",
            validators=[validators.DataRequired()])


class BlacklistUserForm(Form):
    """A WTForm for banning users.

    This form is accessible by administrators only.

    :Fields:
      - `netid`: Text field corresponding to the banned user's NetID
    """
    netid = TextField("NetID", validators=[validators.DataRequired()])

    def to_json(self):
        """Exports the form's fields into a JSON-compatible dictionary."""
        return {
            "netid": self.netid.data,
            "action": self.action.data
        }


class AddAdminForm(Form):
    """A WTForm for adding new administrators.
    
    This form is accessible by administrators only.

    :Fields:
      - `netid`: Text field corresponding to a NetID
    """
    netid = TextField("NetID", validators=[validators.DataRequired()])


class BlockLinksForm(Form):
    """A WTForm for blocking unwanted URLs.

    This form is accessible by administrators only.

    :Fields:
      - `link`: Text field corresponding to a long URL to block
    """
    link = TextField("Link", validators=[validators.DataRequired()])
