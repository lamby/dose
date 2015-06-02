SVNDIR  = $(HOME)/debian/qa.svn/trunk
SUBDIR  = dose
PYFILES = $(filter-out conf.py,$(wildcard *.py))
# conf.py is a symlink in git, and should not be installed
STAMP   = .upload.stamp

install: $(STAMP)

$(STAMP): $(PYFILES)
	cd $(SVNDIR) && svn update
	cp -a $(PYFILES) $(SVNDIR)/$(SUBDIR)
	cd $(SVNDIR)/$(SUBDIR) && svn commit
	touch $(STAMP)

.phony: install
