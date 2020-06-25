#!/bin/bash
inkscape cover.svg --export-png=cover.png
convert cover.png -quality 90 JoM-V001.cover.jpg
inkscape cover.svg --export-height=240 --export-png=thumbnail.png
convert thumbnail.png -quality 90 JoM-V001.thumbnail.jpg
