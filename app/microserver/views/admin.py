from dataclasses import dataclass
from urllib.parse import urljoin
from flask import Blueprint, current_app, url_for, request, render_template, session, redirect

from ..utils import get_level_names, DEFAULT_ALLOWED_LEVELS, signed_serializer

admin = Blueprint('admin', __name__)


@dataclass
class LevelLink:
    name: str

    # TODO: cache all these methods
    def _get_full_url(self, url) -> str:
        return urljoin(request.url_root, url)

    def _get_signed_name(self):
        return signed_serializer.dumps(self.name)

    def get_map_url(self) -> str:
        return self._get_full_url(url_for('allow_level_view', level=self._get_signed_name()))

    def get_direct_url(self) -> str:
        return self._get_full_url(url_for('cpu.debugger_specific_level', level=self.name, t=self._get_signed_name()))

    def get_description(self) -> str:
        return '&nbsp;&nbsp;\u2713' if self.name in DEFAULT_ALLOWED_LEVELS else ''


@admin.route('/secret_admin_link')
def home():
    session['ADMIN'] = True
    return render_template('admin.html.jinja2', level_links=map(LevelLink, get_level_names()))


@admin.route('/logout')
def logout():
    session['ADMIN'] = False
    return redirect(url_for('home'))
