SVNDIR  = $(HOME)/debian/qa.svn/trunk
SUBDIR  = dose
PYFILES = $(filter-out $(wildcard conf*.py),$(wildcard *.py))
# configuration files are maintained in qa svn, not by us
STAMP   = .upload.stamp

install: $(STAMP)

$(STAMP): $(PYFILES)
	cd $(SVNDIR)/$(SUBDIR) && svn update
	cp -a $(PYFILES) $(SVNDIR)/$(SUBDIR)
	@echo 'no svn commit done'
	touch $(STAMP)

.phony: install
