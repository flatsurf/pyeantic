all-local:
	$(PYTHON) setup.py build --verbose

install-exec-local:
	$(PYTHON) setup.py install --prefix $(DESTDIR)$(prefix) --single-version-externally-managed --record $(DESTDIR)$(pythondir)/pyeantic/install_files.txt --verbose

uninstall-local:
	cat $(DESTDIR)$(pythondir)/pyeantic/install_files.txt | xargs rm -rf
	rm -rf $(DESTDIR)$(pythondir)/pyeantic

clean-local:
	-rm -rf pyeantic/__pycache__ pyeantic.egg-info build

BUILT_SOURCES = setup.py
EXTRA_DIST = setup.py.in
CLEANFILES = setup.py
$(builddir)/setup.py: $(srcdir)/setup.py.in Makefile
	sed -e 's,[@]top_srcdir[@],$(top_srcdir),g' -e 's,[@]PACKAGE_VERSION[@],$(PACKAGE_VERSION),g' < $< > $@
