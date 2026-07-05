#!/usr/bin/env bash
# Locally render + compile the CV PDFs from the current data/{en,gr}/ YAML,
# without touching git or CI. Run after editing YAML to preview the result:
#
#   ./cv/generate/preview.sh
#
# Requires: python3, docker (the cdal/dockerimagelatex:latest image is
# pulled automatically on first run).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CV_DIR="$REPO_ROOT/cv"
VENV_DIR="$SCRIPT_DIR/.venv"
DOCKER_IMAGE="cdal/dockerimagelatex:latest"

if ! command -v python3 >/dev/null; then
  echo "error: python3 is required but not found on PATH" >&2
  exit 1
fi
if ! command -v docker >/dev/null; then
  echo "error: docker is required but not found on PATH" >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "error: docker is installed but not running (or not accessible)" >&2
  exit 1
fi

echo "==> Setting up Python environment (first run only)"
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

echo "==> Rendering cv-en.tex / cv-gr.tex from data/en/ and data/gr/"
"$VENV_DIR/bin/python" "$SCRIPT_DIR/render_cv.py" --lang en --out "$CV_DIR/cv-en.tex"
"$VENV_DIR/bin/python" "$SCRIPT_DIR/render_cv.py" --lang gr --out "$CV_DIR/cv-gr.tex"

echo "==> Pulling LaTeX image (skips if already present)"
docker pull --quiet "$DOCKER_IMAGE" >/dev/null

echo "==> Compiling PDFs"
if ! docker run --rm --user "$(id -u):$(id -g)" -v "$CV_DIR:/work" -w /work "$DOCKER_IMAGE" bash -c '
    set -e
    rm -f *.aux *.log *.out *.fls *.fdb_latexmk *.synctex.gz
    xelatex -interaction=nonstopmode cv-gr.tex
    pdflatex -interaction=nonstopmode cv-en.tex
    gs -sDEVICE=pdfwrite -dSAFER -dPDFSETTINGS=/ebook -dColorImageResolution=260 -dPrinted=false -dNOPAUSE -dBATCH -dFastWebView=true -sOutputFile=cdalamagkas-cv-en.pdf cv-en.pdf
    gs -sDEVICE=pdfwrite -dSAFER -dPDFSETTINGS=/ebook -dColorImageResolution=260 -dPrinted=false -dNOPAUSE -dBATCH -dFastWebView=true -sOutputFile=cdalamagkas-cv-gr.pdf cv-gr.pdf
  '; then
  echo
  echo "!! Compilation failed. Last 40 lines of each log:" >&2
  for f in cv-gr cv-en; do
    echo "--- $f.log ---" >&2
    if [ -f "$CV_DIR/$f.log" ]; then
      tail -n 40 "$CV_DIR/$f.log" >&2
    else
      echo "(no $f.log - compilation didn't reach this file)" >&2
    fi
  done
  exit 1
fi

echo
echo "==> Done"
echo "English CV: $CV_DIR/cdalamagkas-cv-en.pdf"
echo "Greek CV:   $CV_DIR/cdalamagkas-cv-gr.pdf"

if command -v xdg-open >/dev/null; then
  xdg-open "$CV_DIR/cdalamagkas-cv-en.pdf" >/dev/null 2>&1 &
  xdg-open "$CV_DIR/cdalamagkas-cv-gr.pdf" >/dev/null 2>&1 &
fi
