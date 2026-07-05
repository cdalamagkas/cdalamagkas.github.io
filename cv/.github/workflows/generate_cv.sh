#!/usr/bin/env bash

# remove pdf if present
[ -f "cv-en.pdf" ] && rm cv-en.pdf
[ -f "cdalamagkas-cv-en.pdf" ] && rm cdalamagkas-cv-en.pdf

[ -f "cv-gr.pdf" ] && rm cv-gr.pdf
[ -f "cdalamagkas-cv-gr.pdf" ] && rm cdalamagkas-cv-gr.pdf


# test if pdf is removed, fail if still present
[ -f "cv-en.pdf" ] && exit 1
[ -f "cdalamagkas-cv-en.pdf" ] && exit 1

[ -f "cv-gr.pdf" ] && exit 1
[ -f "cdalamagkas-cv-gr.pdf" ] && exit 1

# Compile texs
xelatex "cv-gr.tex"
pdflatex "cv-en.tex"

# exit if unoptimized pdf is not present
[ -f "cv-en.pdf" ] || exit 1
[ -f "cv-gr.pdf" ] || exit 1

# optimize pdf and final output
gs -sDEVICE=pdfwrite -dSAFER -dPDFSETTINGS=/ebook -dColorImageResolution=260 -dPrinted=false -dNOPAUSE -dBATCH -dFastWebView=true -sOutputFile=cdalamagkas-cv-en.pdf cv-en.pdf
gs -sDEVICE=pdfwrite -dSAFER -dPDFSETTINGS=/ebook -dColorImageResolution=260 -dPrinted=false -dNOPAUSE -dBATCH -dFastWebView=true -sOutputFile=cdalamagkas-cv-gr.pdf cv-gr.pdf

# exit successfully if optimized pdf is present or with error if not present
[ -f cdalamagkas-cv-gr.pdf ] && exit 0 || exit 1
[ -f cdalamagkas-cv-en.pdf ] && exit 0 || exit 1
