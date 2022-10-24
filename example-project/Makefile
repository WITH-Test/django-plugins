PYTHON_BIN=./py

.PHONY: all
all: db.sqlite3

bin/python:
	@echo -e '#!/usr/bin/env bash\npoetry run python "$$@"\n' > py
	@chmod u+x py

db.sqlite3: bin/python
	$(PYTHON_BIN) manage.py migrate

.PHONY: run
run: bin/python
	$(PYTHON_BIN) manage.py runserver

tox: bin/python
	$(PYTHON_BIN) -m tox


.PHONY: clean
clean:
	rm -rf bin build var
	find -type f -iname '*.pyc' -exec rm {} +
