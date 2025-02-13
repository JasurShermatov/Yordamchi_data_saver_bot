#!/bin/bash

export PYTHONPATH=/Users/jasur/Developer/bot

black .

python app/core/main.py
