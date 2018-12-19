DOT=dot -Tsvg
SVGS=\
	max.svg \
	dfg.svg \
	iter.svg \
	dfg_basic.svg \
	dfg_side.svg \
	dfg_cond.svg \
	dfg_loop.svg \
	dfg_break.svg

all: $(SVGS)

.SUFFIXES: .gv .svg .pdf .tex .dvi

.gv.svg:
	$(DOT) -o $@ $<
