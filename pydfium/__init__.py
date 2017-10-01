# -*- coding: utf-8 -*-
"""
    pydfium
    ~~~~~~~

    Pydfium is a wrapper for the PDFIUM library. This 

    Nutshell
    --------

    TODO EXAMPLE CODE HERE::

        {% extends 'base.html' %}
        {% block title %}Memberlist{% endblock %}
        {% block content %}
          <ul>
          {% for user in users %}
            <li><a href="{{ user.url }}">{{ user.username }}</a></li>
          {% endfor %}
          </ul>
        {% endblock %}


    :copyright: (c) 2017 by Gerson Kurz
    :license: MIT, see LICENSE for more details.
"""
__docformat__ = 'restructuredtext en'
__version__ = '0.0.1'

from pydfium.document import Document

__all__ = [
    'Document'
]
