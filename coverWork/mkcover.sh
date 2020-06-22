#!/bin/bash
inkscape cover.svg --export-png=cover.png
convert cover.png -quality 90 CoverImage.jpg
