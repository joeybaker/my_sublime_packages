import sublime_plugin
import hashlib
import urllib
import time
import base64
import re
import html.parser

# test http://dmoz.org/World/Español <b>Català, Español, Français, 日本語, Русский</b>

class Md5Command(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			m = hashlib.md5()
			m.update(txt.encode('utf-8'))
			txt = m.hexdigest()

			self.view.replace(edit, s, txt)

class Sha1Command(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			m = hashlib.sha1()
			m.update(txt.encode('utf-8'))
			txt = m.hexdigest()

			self.view.replace(edit, s, txt)

class Base64EncodeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			txt = base64.b64encode(txt.encode('utf-8')).decode('utf-8')

			self.view.replace(edit, s, txt)

class Base64DecodeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			# pad to 4 characters
			if len(txt) % 4 != 0:
				txt += "=" * (4 - len(txt) % 4)

			txt = base64.b64decode(txt).decode('utf-8')

			self.view.replace(edit, s, txt)

class UriComponentEncodeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			txt = urllib.parse.quote(txt, safe='~()*!.\'')

			self.view.replace(edit, s, txt)

class UriEncodeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			txt = urllib.parse.quote(txt, safe='~@#$&()*!+=:;,.?/\'')

			self.view.replace(edit, s, txt)

class UriComponentDecodeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			txt = urllib.parse.unquote(txt)

			self.view.replace(edit, s, txt);

class HtmlEntityEncodeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			txt = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;").replace('"', "&quot;")

			self.view.replace(edit, s, txt);

class HtmlEntityEncodeAllCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			txt = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;").replace('"', "&quot;").encode('ascii', errors='xmlcharrefreplace').decode('utf-8');

			self.view.replace(edit, s, txt);

class HtmlEntityDecodeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			if s.empty():
				s = self.view.word(s)
			txt = self.view.substr(s)

			txt = html.parser.HTMLParser().unescape(txt)

			self.view.replace(edit, s, txt);

class CurrentUnixTimestamp(sublime_plugin.TextCommand):
	def run(self, edit):
		for s in self.view.sel():
			txt = time.asctime(time.gmtime())
			txt = time.ctime()
			txt = "%.0f" % round(time.time(), 3)
			self.view.replace(edit, s, txt)

# disable default command
from HTML.encode_html_entities import *
class EncodeHtmlEntities(sublime_plugin.TextCommand):
	def is_visible(self):
		return False
	def is_enabled(self):
		return False