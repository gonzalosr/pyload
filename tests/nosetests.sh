#!/usr/bin/env bash
NS=nosetests
which nosetests2 > /dev/null && NS=nosetests2
$NS tests/ --with-coverage --with-xunit --cover-package=module --cover-erase
coverage xml
