
OCAMLC=ocamlc
OCAMLOPT=ocamlopt
OCAMLDEP=ocamldep

OBJS = util.cmx common.cmx solver.cmx
OPTLINKFLAGS=unix.cmxa str.cmxa
BYTEOBJS=${OBJS:%.cmx=%.cmo}
BYTELINKFLAGS=${OPTLINKFLAGS:%.cmxa=%.cma}

all: debcheck 

byte: debcheck.byte rpmcheck.byte

rpmcheck: $(OBJS) rpm.cmx
	$(OCAMLOPT) -o $@  $(OPTLINKFLAGS) $^ $(LINKFLAGS)

debcheck: $(OBJS) deb.cmx
	$(OCAMLOPT) -o $@  $(OPTLINKFLAGS) $^ $(LINKFLAGS)
#	ocamlopt -o check unix.cmxa str.cmxa check.ml

#####

rpmcheck.byte: $(BYTEOBJS) rpm.cmo
	$(OCAMLC) -o $@  $(BYTELINKFLAGS) $^ $(LINKFLAGS)

debcheck.byte: $(BYTEOBJS) deb.cmo
	$(OCAMLC) -o $@  $(BYTELINKFLAGS) $^ $(LINKFLAGS)


clean::
	find . -regex ".*\\.\(cm[oix]\|o\)" | xargs rm -f

.SUFFIXES: .cmo .cmi .cmx .ml .mli .mly .mll .idl .o .c

.ml.cmx:
	$(OCAMLOPT) $(OPTCOMPFLAGS) $(COMPFLAGS) -c $<

.ml.cmo:
	$(OCAMLC) $(BYTECOMPFLAGS) $(COMPFLAGS) -c $<

.mli.cmi:
	$(OCAMLC) $(COMPFLAGS) -c $<

.idl.ml:
	$(OCAMLIDL) $<

.mly.ml:
	$(OCAMLYACC) $<

.mly.mli:
	$(OCAMLYACC) $<

.mll.ml:
	$(OCAMLLEX) $<

.c.o:
	$(OCAMLC) -ccopt "-o $@" $(COMPFLAGS) -ccopt "$(CFLAGS)" -c $<

depend:
	find . -regex ".*\\.mli?" | xargs \
	$(OCAMLDEP) $(DEPFLAGS) $$i \
	> .depend

-include .depend
