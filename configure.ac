dnl Process this file with autoconf to produce a configure script.

dnl We need at least autoconf 2.69 for this configure.ac to work.
AC_PREREQ([2.69])
AC_INIT([intervalxt], [1.0.0], [julian.rueth@fsfe.org])

AC_CONFIG_MACRO_DIR([m4])
AM_INIT_AUTOMAKE([1.14.1])

dnl Find C++ Compiler
AC_PROG_CXX

dnl Set INSTALL or use install-sh.
AC_PROG_INSTALL
dnl We build our library with libtool.
LT_INIT

AC_CANONICAL_HOST

dnl We run the valgrind test-suite in make check-valgrind (if valgrind is installed)
AX_VALGRIND_DFLT([sgcheck], [off])
AX_VALGRIND_DFLT([drd], [off])
AX_VALGRIND_DFLT([helgrind], [off])
AX_VALGRIND_CHECK()

dnl Check for required libraries
AC_LANG([C++])

dnl We want to build a Python module powered by cppyy
AM_PATH_PYTHON([3.6], , [AC_MSG_ERROR([Python not found])])

dnl We use some C++17 features, such as if constexpr
AX_CXX_COMPILE_STDCXX(17)

AC_CHECK_HEADERS([e-antic/renfxx.h], , AC_MSG_ERROR([E-ANTIC headers not found]))
AC_CHECK_LIB([eantic], [renf_elem_clear], , AC_MSG_ERROR([E-ANTIC library not found]), [-lgmp -lmpfr -lflint])
AX_CXX_CHECK_LIB([eanticxx], [eantic::renf_elem_class], , AC_MSG_ERROR([E-ANTIC library not found]), [-lgmp -lmpfr -lflint])

dnl Our Python library relies on cppyy. It can be built without since it is a
dnl pure Python package but we cannot test it if cppyy is not present.
AC_ARG_WITH([pytest], AS_HELP_STRING([--without-pytest], [Do not run Python tests]))
AS_IF([test "x$with_pytest" != "xno" && test "x$have_python" = "xyes"],
      [
       with_pytest=yes
       AS_IF([$PYTHON -c 'import pytest'], , AC_MSG_ERROR([pytest for make check not found; run --without-pytest to disable Python tests in make check]))
       AS_IF([$PYTHON -c 'import cppyy'], , AC_MSG_ERROR([cppyy for make check not found; run --without-pytest to disable Python tests in make check]))
      ], [])
AM_CONDITIONAL([HAVE_PYTEST], [test "x$with_pytest" = "xyes"])

AC_CONFIG_FILES([Makefile src/Makefile src/pyeantic/Makefile test/Makefile test/pyintervalxt/Makefile])

dnl Python's setuptools absolutely want to run in the source directory of the
dnl module. Since this is incompatible with out-of-tree builds of
dnl autoconfiscated packages, we have to copy all the Python bits over to the
dnl build dir manually so that Python can't tell the difference.
AC_CONFIG_LINKS([src/pyeantic/pyeantic/__init__.py:src/pyeantic/pyeantic/__init__.py
                 src/pyeantic/pyeantic/cppyy_eantic.py:src/pyeantic/pyeantic/cppyy_eantic.py])

AC_OUTPUT
