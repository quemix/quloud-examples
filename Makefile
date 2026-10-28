# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Preview the local build at http://localhost:8000
serve:
	python3 -m http.server -d "$(BUILDDIR)/html" 8000

# Link the private workflow instructions for Codex and other agents.
agent-link:
	@test -f meta/codex/AGENTS.md || { echo "meta/ が無い。先に README.md の手順で clone する"; exit 1; }
	@test ! -e AGENTS.md -o -L AGENTS.md || { echo "AGENTS.md が実ファイルとして存在する。退避してから実行する"; exit 1; }
	ln -sfn meta/codex/AGENTS.md AGENTS.md

# Link the sibling private checkout at meta/ for agent instructions.
meta-link:
	@test -d ../quloud-examples-meta || { echo "../quloud-examples-meta が無い。README.md の手順で clone する"; exit 1; }
	@test ! -e meta -o -L meta || { echo "meta/ が実ディレクトリとして存在する"; exit 1; }
	ln -sfn ../quloud-examples-meta meta

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help serve agent-link meta-link Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
