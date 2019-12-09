# The Snip #

Encrypted shared clipboard tool

## Usage ##

Generate "settings.conf" file with:
    
    the_snip.py --generate

Optionally change the output file with:

    the_snip.py --generate --conf "/path/to/settings.conf"

Copy the current contents of the clipboard into the shared channel

(will attempt to read "settings.conf" from current directory unless --conf argument is given)

    the_snip.py --copy --conf "/path/to/settings.conf"

Load the contents of the channel into the clipboard

    the_snip.py --paste --conf "/path/to/settings.conf"

Works best with keyboard shortcuts, example

Ctrl + Shift + C

    the_snip.py --copy --conf "/path/to/settings.conf"

Ctrl + Shift + V

    the_snip.py --paste --conf "/path/to/settings.conf"
