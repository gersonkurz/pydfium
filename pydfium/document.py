# -*- coding: utf-8 -*-
"""
    jinja2.filters
    ~~~~~~~~~~~~~~

    Bundled jinja filters.

    :copyright: (c) 2017 by the Jinja Team.
    :license: BSD, see LICENSE for more details.
"""
import platform
from ctypes import c_int, c_void_p, Structure, WinDLL, byref, c_char_p
from ctypes import WINFUNCTYPE
import os
import logging

log = logging.getLogger("pydfium.document")

class FPDF_LIBRARY_CONFIG(Structure):
    _fields_ = [("version", c_int),
                ("user_font_paths", c_void_p), # not supported yet
                ("isolate", c_void_p),
                ("v8embedder_slot", c_int)]

def determine_pdfium_binary():
    log.debug(f"document.py was loaded from {__file__}")
    directory, filename = os.path.split(__file__)
    log.debug(f"- directory is {directory}")

    # determine folder name based on 32/64 bit Windows
    foldername = "pdfium-windows-x64\\x64" if platform.architecture()[0] == "64bit" else "pdfium-windows-x86\\x86"
    log.debug(f"- folder is {foldername}")

    result = os.path.join(directory, foldername, "bin\\pdfium.dll")
    log.debug(f"- result is {result}")

    if not os.path.exists(result):
        assert False, f"pdfium.dll not found at '{result}'"
    return result


class Document(object):
    def __init__(self, ws, doc):
        self.ws = ws
        self.doc = doc
        assert self.doc != 0

    def __enter__(self):
        log.info(f"Document.enter({id(self)}, self.doc={self.doc}) code called")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print(self.ws)
        print(self.ws.fpdf_close_document)
        self.ws.fpdf_close_document(self.doc)
        del self.doc

    @property
    def page_count(self):
        return self.ws.fpdf_get_page_count(self.doc)

def FPDF_string(x):
    if x is not None:
        if isinstance(x, str):
            return x.encode("latin-1")
    return x

class Workspace(object):
    def __init__(self):
        self.pdfium = None

    def verify_is_supported_environment(self):
        if platform.system() == 'Windows':
            return True

        assert False, f"Operating System '{platform.system()} not supported by pyfdium module"

    def load_library(self, filename=None):
        self.verify_is_supported_environment()

        if not filename:
            filename = determine_pdfium_binary()

        assert self.pdfium is None, "Do not call this function more than once"

        self.pdfium = WinDLL(filename)
        log.info(f"loaded {self.pdfium}")

        self.init_config = FPDF_LIBRARY_CONFIG(2, c_void_p(), c_void_p(), 0)
        self.pdfium.FPDF_InitLibraryWithConfig(byref(self.init_config))
        rc = self.pdfium.FPDF_GetLastError()
        log.info(f"ok, InitLibraryWithConfig({rc}) done")

        prototype = WINFUNCTYPE(c_void_p, c_char_p, c_char_p)
        self.fpdf_load_document = prototype(("FPDF_LoadDocument", self.pdfium))

        prototype = WINFUNCTYPE(None, c_void_p)
        self.fpdf_close_document = prototype(("FPDF_CloseDocument", self.pdfium))

        prototype = WINFUNCTYPE(c_int, c_void_p)
        self.fpdf_get_page_count = prototype(("FPDF_GetPageCount", self.pdfium))

    def free_library(self):
        if self.pdfium is not None:
            self.pdfium.FPDF_DestroyLibrary()
            del self.pdfium
            self.pdfium = None

    def __enter__(self):
        log.info(f"Workspace.enter({id(self)}) code called")
        self.load_library()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.free_library()

    def load_document(self, filename, password=None):
        result = self.fpdf_load_document(FPDF_string(filename), FPDF_string(password))
        print("result: %r" % (result, ))
        if not result:
            rc = self.pdfium.FPDF_GetLastError()
            assert False, f"ERROR {rc}: unable to load '{filename}'"

        return Document(self, result)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with Workspace() as ws:
        log.info(f"Workspace: {ws}")

        with ws.load_document(r"C:\Scripts\2017\pydfium\pydfium\test.pdf") as doc:
            log.info(f"Document: {doc} has {doc.page_count} pages")


