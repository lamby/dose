INSTALLDIR=/srv/qa.debian.org/web/dose
FILES=debcheck.html

install: $(INSTALLDIR)/debcheck.html

$(INSTALL)/debcheck.html: header.part footer.part debcheck.part
	cat header.part debcheck.part footer.part > $@
