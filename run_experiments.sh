#!/bin/sh

console=/home/ubuntu/pantheon-observatory/console.py
$console --schemes "default_tcp vegas" aws_california_1 286-blackmagic
$console --schemes "default_tcp vegas" aws_brazil_1 286-blackmagic
$console --schemes "default_tcp vegas" aws_india_1 286-blackmagic
$console --schemes "default_tcp vegas" aws_california_2 286-blackmagic
$console --schemes "default_tcp vegas" aws_brazil_2 286-blackmagic
$console --schemes "default_tcp vegas" aws_india_2 286-blackmagic
$console --schemes "default_tcp vegas" aws_korea 286-blackmagic
