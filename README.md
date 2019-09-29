# timg
Display an image in terminal.

# Setup 
`timg` is available as a package on PyPI:

    $ pip install timg

Now you can use the `timg` command in your terminal.

# Screenshots
![](https://i.imgur.com/oJbbsEe.png)
![](https://i.imgur.com/E95M3SJ.png)

# Usage
        usage: timg [-h] [-V] [-i] [-m METHOD] [-r N] [-s W] [filename]

        print an image in terminal

        positional arguments:
          filename              filename of an image

        optional arguments:
          -h, --help            show this help message and exit
          -V, --version         print version and exit
          -i, --invert-background
                                invert grayscale in ASCII mode
          -m METHOD, --method METHOD
                                name of a rendering method (use `-m list` to list
                                available methods, the default is a24h)
          -r N, --reduce-colors N
                                reduce color palette of an input image (1-256)
          -s W, --size W        width of an image

# zsh completions
Add this line to `.zshrc`

    compdef _gnu_generic timg
