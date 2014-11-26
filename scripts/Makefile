SVNDIR  = $(HOME)/debian/qa.svn/trunk
SUBDIR  = dose
FILES   = $(wildcard *.py)
STAMP   = .upload.stamp

install: $(STAMP)

$(STAMP): $(FILES)
	echo $(FILES)
	cd $(SVNDIR) && svn update
	cp -a $(FILES) $(SVNDIR)/$(SUBDIR)
	cd $(SVNDIR)/$(SUBDIR) && \
		rm -f conf-test.py conf.py && \
		mv conf-quantz.py conf.py && svn commit
	touch $(STAMP)

.phony: install
