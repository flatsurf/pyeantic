all-local:
	$(PYTHON) setup.py build --verbose

install-exec-local:
	$(PYTHON) setup.py install --prefix $(DESTDIR)$(prefix) --single-version-externally-managed --record $(DESTDIR)$(pythondir)/pyeantic/install_files.txt --verbose

uninstall-local:
	cat $(DESTDIR)$(pythondir)/pyeantic/install_files.txt | xargs rm -rf
	rm -rf $(DESTDIR)$(pythondir)/pyeantic

clean-local:
	-rm -rf pyeantic/__pycache__ pyeantic.egg-info build .pytest_cache

BUILT_SOURCES = setup.py pyeantic/config.py
EXTRA_DIST = setup.py.in pyeantic/config.py.in
CLEANFILES = setup.py pyeantic/config.py
$(builddir)/setup.py: $(srcdir)/setup.py.in Makefile
	sed -e 's,[@]top_srcdir[@],$(top_srcdir),g' -e 's,[@]PACKAGE_VERSION[@],$(PACKAGE_VERSION),g' < $< > $@
$(builddir)/pyeantic/config.py: $(srcdir)/pyeantic/config.py.in Makefile
	sed -e 's?[@]libdir[@]?-L$(libdir) $(LDFLAGS)?g' -e 's,[@]PACKAGE_VERSION[@],$(PACKAGE_VERSION),g' < $< > $@
