# timg
Display an image in terminal.

# Setup 
Clone or download this repository, `cd` into it and run:

    $ pip3 install .

Now you can use the `timg` command in your terminal.

# Screenshots
![](https://i.imgur.com/RJl8YrO.png)
![](https://i.imgur.com/PFEDitT.png)
![](https://i.imgur.com/sKueJiE.png)
![](https://i.imgur.com/q25M3YZ.png)
![](https://i.imgur.com/A99gCRC.png)
![](https://i.imgur.com/KggMZT5.png)

# Usage
        usage: timg [-h] [-b BLOCK] [-c STRING] [-r] [-R N] [-s N] [-w N] [-S] [-8]
                    [-x]
                    FILENAME

        Display an image in terminal.

        positional arguments:
          FILENAME              image file to be shown

        optional arguments:
          -h, --help            show this help message and exit
          -b BLOCK, --block BLOCK
                                use colors from a subset of 8-bit ANSI palette (works
                                only with -8 switch). BLOCK can be: "standard",
                                "intensive", "cube", "grayscale" or an expression in
                                form of ranges separated by a comma, e.g.
                                "0..10,20..40,128" or "0,231"
          -c STRING, --charset STRING
                                print image using characters from the provided STRING
          -r, --random-chars    print characters from the provided charset in a random
                                order
          -R N, --reduce-colors N
                                number of colors to be shown in sixel mode, the more
                                the slower the output
          -s N, --size N        width in pixels of an image in sixel mode
          -w N, --width N       number of characters to be printed horizontally
          -S, --sixel           use sixels
          -8, --8-bit           use 8-bit color palette (much slower (because it finds
                                the closest ANSI color code for each pixel) and uglier
                                (because it's just 256 colors) but allows a palette
                                subset to be given and supports dumb terminal
                                emulators)
          -x, --high-resolution
                                display image using half blocks

# zsh completions
Add this line to `.zshrc`

    compdef _gnu_generic timg
