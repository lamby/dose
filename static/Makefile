INSTALLDIR=/srv/qa.debian.org/web/dose
FILES=debcheck.html outdated.html file-overwrites.html index.html
DIRS=weathericons

html: $(FILES)

$(FILES): %.html: %.part header.part footer.part
	cat header.part $< footer.part > $@

install: $(FILES)
	@ [ -d $(INSTALLDIR) ] || (echo "cannot find $(INSTALLDIR)"; exit 1)
	cp $(FILES) $(INSTALLDIR)
	cp -r $(DIRS) $(INSTALLDIR)

clean:
	-rm *.html
