#!/bin/sh
zip -r intent-based-bot.zip Dockerfile requirements.txt setup.py intentbasedbot
# docker build -t intent-based-bot .
# docker run --rm -p 5000:5000 --name intent-based-bot intent-based-bot
# scp intent-based-bot.zip ec2-user@ec2-54-218-67-122.us-west-2.compute.amazonaws.com:/home/ec2-user/