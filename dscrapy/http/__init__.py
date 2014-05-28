"""
Module containing all HTTP related classes

Use this module (instead of the more specific ones) when importing Headers,
Request and Response outside this module.
"""

from dscrapy.http.headers import Headers

from dscrapy.http.request import Request
from dscrapy.http.request.form import FormRequest
from dscrapy.http.request.rpc import XmlRpcRequest

from dscrapy.http.response import Response
from dscrapy.http.response.html import HtmlResponse
from dscrapy.http.response.xml import XmlResponse
from dscrapy.http.response.text import TextResponse
