# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXINTL    ?= sphinx-intl
SOURCEDIR     = .
BUILDDIR      = _build
# update-po で翻訳カタログ（.po）を更新するページ。既定は .po のあるページすべて。
# 新しく訳すページは make update-po EN_DOCS="hydrogen_chain/index hydrogen_chain/..." で .po を作る。
EN_DOCS       ?= $(patsubst locales/en/LC_MESSAGES/%.po,%,$(shell find locales/en/LC_MESSAGES -name '*.po' 2>/dev/null | sort))

# 手元のPythonにテーマが無ければ（apt版Sphinxなど）、requirements.txt の版を
# Git管理外の PYLIB に pip で入れて使う。requirements.txt を変えると入れ直す。
# GitHub Actions は先に pip install するので、こちらは使わない。
PYLIB ?= $(or $(XDG_CACHE_HOME),$(HOME)/.cache)/quloud-examples/pylib
ifneq ($(shell python3 -c "import sphinx, pydata_sphinx_theme" 2>/dev/null && echo ok),ok)
SPHINXBUILD = PYTHONPATH="$(PYLIB)" python3 -m sphinx
SPHINXINTL = PYTHONPATH="$(PYLIB)" python3 -m sphinx_intl
SPHINXDEPS  = $(PYLIB)/requirements.txt
endif

$(PYLIB)/requirements.txt: requirements.txt
	python3 -m pip install -q --upgrade --target "$(PYLIB)" -r requirements.txt --break-system-packages
	cp requirements.txt "$@"

# 末尾の「%: Makefile」がSphinxに渡さないよう、ソースファイルとして扱う。
requirements.txt: ;

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

.PHONY: help html gettext update-po html-en serve agent-link meta-link Makefile

# Always rebuild every page (-E). An incremental build rewrites only the pages whose
# source changed, so after the toctree changes the sidebar of the other pages stays stale.
html: $(SPHINXDEPS)
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" -E $(SPHINXOPTS) $(O)

gettext: $(SPHINXDEPS)
	@$(SPHINXBUILD) -b gettext -E -d "$(BUILDDIR)/doctrees-gettext" $(SPHINXOPTS) $(O) "$(SOURCEDIR)" "$(BUILDDIR)/gettext"

# Update only the catalogs of EN_DOCS; the other pages have no English translation yet.
update-po: gettext
	@set -e; catalog_dir=$$(mktemp -d "$(BUILDDIR)/gettext-selected.XXXXXX"); \
	trap 'rm -rf "$$catalog_dir"' EXIT; \
	for doc in $(EN_DOCS); do \
		install -D "$(BUILDDIR)/gettext/$$doc.pot" "$$catalog_dir/$$doc.pot"; \
	done; \
	$(SPHINXINTL) update -p "$$catalog_dir" -d locales -l en

# The English edition goes under /en/ (_ext/english_edition.py).
html-en: $(SPHINXDEPS)
	@QULOUD_DOC_LANGUAGE=en $(SPHINXBUILD) -b html -E -d "$(BUILDDIR)/doctrees-en" $(SPHINXOPTS) $(O) "$(SOURCEDIR)" "$(BUILDDIR)/html/en"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
