TARGET=treinen@quantz.debian.org:/srv/qa.debian.org/web/dose
FILES=debcheck.html outdated.html file-overwrites.html index.html
DIRS=weathericons

html: $(FILES)

$(FILES): %.html: %.part header.part footer.part
	cat header.part $< footer.part > $@

install: $(FILES)
	scp $(FILES) $(TARGET)
	scp -r $(DIRS) $(TARGET)

clean:
	-rm *.html
