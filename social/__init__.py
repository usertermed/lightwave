"""
Compatibility shims for runtime issues (loaded early by Django).

This module contains a small monkeypatch for Django's template
context `BaseContext.__copy__` implementation to work around an
incompatibility with Python 3.14's handling of `super()` objects
when using `copy()`.

Keep this file small and focused; remove once the dependency
versions that included the fix are in use.
"""
try:
	# Defer imports until Django is available; importing this file while
	# Django isn't installed should be a no-op.
	from copy import copy as _copy
	from django.template.context import BaseContext

	def _basecontext_copy_compat(self):
		"""Create a shallow duplicate of a BaseContext without calling
		``copy(super())`` which can fail under Python 3.14.
		"""
		cls = self.__class__
		# Create an empty instance without invoking __init__
		duplicate = cls.__new__(cls)

		# Shallow-copy instance dict where possible
		try:
			duplicate.__dict__ = getattr(self, "__dict__", {}).copy()
		except Exception:
			duplicate.__dict__ = dict(getattr(self, "__dict__", {}))

		# Ensure `dicts` is a shallow copy so modifications don't share state
		if hasattr(self, "dicts"):
			duplicate.dicts = list(self.dicts)

		return duplicate

	# Apply the monkeypatch only if the implementation looks like the
	# problematic variant (defensive: avoid double-patching).
	if getattr(BaseContext, "__copy__", None) is not _basecontext_copy_compat:
		BaseContext.__copy__ = _basecontext_copy_compat
except Exception:
	# If anything goes wrong here (e.g., Django not installed yet),
	# don't block the process — the import will be retried when Django
	# loads and this module is imported again.
	pass
