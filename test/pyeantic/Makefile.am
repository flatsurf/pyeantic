if HAVE_SAGE
  MAYBE_SAGE = eantic_sage.py
endif
TESTS = renf.py renf_elem.py doctest.sh ${MAYBE_SAGE}
EXTRA_DIST = $(TESTS)

AM_TESTS_ENVIRONMENT = . $(builddir)/test-env.sh;

renf.py: test-env.sh
renf_elem.py: test-env.sh
eantic_sage.py: test-env.sh
doctest.sh: test-env.sh

@VALGRIND_CHECK_RULES@

BUILT_SOURCES = test-env.sh
EXTRA_DIST += test-env.sh.in
CLEANFILES = test-env.sh
$(builddir)/test-env.sh: $(srcdir)/test-env.sh.in Makefile
	sed -e 's,[@]srcdir[@],$(srcdir),g' -e 's,[@]builddir[@],$(builddir),g' -e 's,[@]pythondir[@],$(pythondir),g' < $< > $@
