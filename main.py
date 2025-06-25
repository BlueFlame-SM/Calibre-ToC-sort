from qt.core import QAction

from calibre.ebooks.oeb.polish.toc import TOC, get_toc, commit_toc
from calibre.gui2 import error_dialog, info_dialog
from calibre.ebooks.oeb.polish.container import Container

# The base class that all tools must inherit from
from calibre.gui2.tweak_book.plugin import Tool


class SortToc(Tool):
    """
    A tool to sort the Table of Contents in the order of the spine.
    """
    #: Set this to a unique name it will be used as a key
    name = 'sort-toc'

    #: If True the user can choose to place this tool in the plugins toolbar
    allowed_in_toolbar = True

    #: If True the user can choose to place this tool in the plugins menu
    allowed_in_menu = True

    def create_action(self, for_toolbar=True):
        # Create an action, this will be added to the plugins toolbar and
        # the plugins menu
        ac = QAction('Sort ToC by Spine', self.gui)  # noqa: F821
        if not for_toolbar:
            # Register a keyboard shortcut for this toolbar action. We only
            # register it for the action created for the menu, not the toolbar,
            # to avoid a double trigger
            self.register_shortcut(ac, 'sort-toc-by-spine')
        ac.triggered.connect(self.sort_toc)
        return ac

    def sort_toc(self):
        """
        Sort the Table of Contents in the order of the spine.
        """
        container = self.current_container
        if not isinstance(container, Container):
            error_dialog(self.gui, 'Error', 'This tool can only be used on a book container.', show=True)
            return

        # Get the current Table of Contents
        toc_root = get_toc(container)

        # Create a mapping from spine name to node (and level)
        toc_node_map = {node.dest: (node, lvl) for lvl, node in toc_root.iterdescendants(0)}

        # Remove all nodes from the TOC root
        for node in list(toc_root.iterdescendants()):
            node.remove_from_parent() # type: ignore

        # Loop through the spine and build a new TOC
        adjusted_lvls = []
        for name, _ in container.spine_names:
            if name in toc_node_map:
                # Retrieve the node from the mapping
                node, lvl = toc_node_map[name]
                # Navigate to the correct level in the TOC
                toc = toc_root
                for _ in range(lvl):
                    if toc.last_child is None:
                        adjusted_lvls.append(node)
                        break
                    toc = toc.last_child
                # Add the node to the TOC root
                toc.add(node.title, node.dest, node.frag)

        # Commit the new TOC
        commit_toc(container, toc_root)

        # Show a message to the user
        det_msg = "The following ToC entries had their depth adjusted:\n%s" % "\n".join(node.title for node in adjusted_lvls)
        info_dialog(self.gui, 'Success', 'The Table of Contents has been sorted in order of the spine.', det_msg=det_msg, show=True)
