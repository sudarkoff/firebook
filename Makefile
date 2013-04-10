# make VERBOSE=1 if you wanna see the command lines
ifeq ($(VERBOSE),)
   export Q := @
endif

BUILD_DIR := book

# pandoc is a handy tool for converting between numerous text formats:
# http://johnmacfarlane.net/pandoc/installing.html
# To install pdflatex required for rendering PDFs:
# 
PANDOC := pandoc

# pandoc options
# Liberation fonts: http://en.wikipedia.org/wiki/Liberation_fonts
PANDOC_PDF_OPTS := --toc --chapters --base-header-level=1 --number-sections --template=virsto_doc.tex --variable mainfont="Liberation Serif" --variable sansfont="Liberation Sans" --variable monofont="Liberation Mono" --variable fontsize=12pt --variable documentclass=book
PANDOC_EBOOK_OPTS := --toc --epub-stylesheet=epub.css --epub-cover-image=cover.jpg --base-header-level=1

# download kindlegen from http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211
KINDLEGEN := kindlegen
KINDLEGEN_OPTS :=

# Only .markdown files are considered full documents. Any supporting notes and memos that are not
# to be converted should have a different extension (.md, .mdown, .txt and so on).
MARKDOWN := $(wildcard *.markdown)

BOOK_NAME := firebook
PDF := $(BOOK_NAME).pdf
EBOOK := $(BOOK_NAME).epub
# TODO: File per chapter, plus index or something.
HTML := $(patsubst %.markdown,$(BUILD_DIR)/%.html,$(MARKDOWN))

.PHONY: all pdf ebook html clean

all: $(PDF) $(EBOOK)

pdf: $(PDF)

ebook: $(EBOOK)

html: $(HTML)

# generate PDF
$(PDF): $(MARKDOWN)
	@echo " ** pdf     :" $@
	${Q}$(PANDOC) $(PANDOC_PDF_OPTS) --self-contained -o $@ title.txt $<

# generate both iBooks (.epub) and then Kindle (.mobi) formats
$(EBOOK): $(MARKDOWN)
	@echo " ** ebook   :" $@
	${Q}$(PANDOC) $(PANDOC_EBOOK_OPTS) --self-contained -o $@ title.txt $<
	${Q}$(KINDLEGEN) $(KINDLEGEN_OPTS) $@ > /dev/null

# generate HTML files
$(BUILD_DIR)/%.html: %.markdown
	@echo " ** html    :" $@
	${Q}$(PANDOC) --self-contained -o $@ $<

clean:
	${Q}rm -rf $(BUILD_DIR)

