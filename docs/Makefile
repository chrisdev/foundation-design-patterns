# Makefile for site content
#
BUILDDIR = _build
INSTALLDIR= ../foundation_theme_site/templates/includes
MD_SRCS=$(shell find . -name "*.md")
MD_TARGETS=$(MD_SRCS:.md=.html)
.PHONY: help clean html install

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html       to make the HTML include files"
	@echo "  clean       deletes all html files "
	@echo "  install     copy the htmls to includes "
	
	
clean:
	rm *.html
	
$(MD_TARGETS): %.html: %.md
	markdown_py -x codehilite $< -f $@
	
html: $(MD_TARGETS)

install:
	cp *.html $(INSTALLDIR)
