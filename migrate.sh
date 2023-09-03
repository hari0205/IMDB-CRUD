#!/bin/bash

flask db init && flask db migrate -m $1 && flask db upgrade
