from calibre.customize import EditBookToolPlugin

class DemoPlugin(EditBookToolPlugin):
    name = 'Spine Sort Table of Contents'
    version = (1, 0, 0)
    author = 'Timo Post'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Sorts the current Table of Contents in the order of the spine.'
    minimum_calibre_version = (8, 5, 0)
