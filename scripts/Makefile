SVNDIR  = $(HOME)/debian/qa.svn/trunk
SUBDIR  = dose
PYFILES = $(filter-out conf.py,$(wildcard *.py))
# conf.py is a symlink in git, and should not be installed
STAMP   = .upload.stamp

install: $(STAMP)

$(STAMP): $(PYFILES)
	cd $(SVNDIR)/$(SUBDIR) && svn update
	cp -a $(PYFILES) $(SVNDIR)/$(SUBDIR)
	@echo 'no svn commit done'
	touch $(STAMP)

.phony: install
