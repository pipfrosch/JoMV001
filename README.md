Journal of Mammalogy Volume 1
=============================

ePub3 project for Journal of Mammalogy Volume 1 (1919-1920) Issues 1-5.

Not affiliated with American Society of Mammalogists or the Journal of Mammalogy.

The content in Journal of Mammalogy Volume 1 has aged into the public domain.

The `tools/epubcheck.sh` shell script is specific to my environment, if you want
to use it you will either need to set up epubcheck the same way I do (which requires
a *nix system) or create a similar script for your own setup.

The `tools/mkepub.sh` does a fresh `git` clone, this is so that the ePub it
generates can update the modification time without needing to commit the change to
the OPF file.

The `tools/mkepub.sh` shell script has several things that are specific to my
environment, including the location of the font files that get embedded in the
ePub as I do not store the actual font files in git. Note that my copies of the
font files are a subset of the originals with only glyphs for the western Latin
languages, basically Windows Glyph List 4 maybe plus a few.

The `tools/mkepub.sh` shell script also assumes a *nix environment with `sed`
available, `python3` available, and the `ace` utility from
[Ace by Daisy](https://inclusivepublishing.org/toolbox/accessibility-checker/)
in your execution path though the script will run without it.

The `tools/mkepub.sh` shell script, when `ace` is available, is set to make a
git commit when it runs `ace`. If you forked this project into your own git
then make sure you are using the clone from your git.
