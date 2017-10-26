#!/bin/bash

nohup java -cp lib/*:lib/nlpserver.jar com.haizhi.nlp.server.NlpServer 51051 >> nohup.out &
