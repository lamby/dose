INSTALLDIR=/srv/qa.debian.org/web/dose
FILES=debcheck.html outdated.html file-overwrites.html index.html

all: $(FILES)

$(FILES): %.html: %.part header.part footer.part
	cat header.part $< footer.part > $@

clean:
	-rm *.html
