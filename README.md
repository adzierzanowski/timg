# timg

Display an image in terminal.

# Screenshots
![](https://i.imgur.com/y8Uf8FV.png)
![](https://i.imgur.com/cgqjMmW.png)
![](https://i.imgur.com/JG7ATZO.png)
![](https://i.imgur.com/nNrcwBB.png)
![](https://i.imgur.com/hqQtFkC.png)

# usage
    usage: timg [-h] [-b BLOCK] [-c STRING] [-r] [-s N] [-8] [-x] FILENAME

    Display an image in terminal.

    positional arguments:
      FILENAME              image file to be shown

    optional arguments:
      -h, --help            show this help message and exit
      -b BLOCK, --block BLOCK
                            use colors from a subset of 8-bit ANSI pallette (works
                            only with -8 switch). BLOCK can be: "standard",
                            "intensive", "cube", "grayscale" or a python list or
                            range defining some numbers from 0 to 255 (e.g. "[n
                            for n in range(20, 120, 10) if n != 100]" or "[0,
                            231]" which prints image in black and white).
      -c STRING, --charset STRING
                            print image using characters from the provided STRING
      -r, --random-chars    print characters from the provided charset in a random
                            order
      -s N, --size N        number of characters to be printed horizontally
      -8, --8-bit           use 8-bit color pallette (much slower (because it
                            finds the closest ANSI color code for each pixel) and
                            uglier (because it's just 256 colors) but allows a
                            pallette subset to be given and supports dumb terminal
                            emulators)
      -x, --high-resolution
                            display image using half blocks
