Welcome to context_menu's documentation!
========================================

  The most important information is on how **menus.py** works. Basic usage is as follows:

  1. Import the **ContextCommand** and **ContextMenu** Class from menus.py
  2. Create your menu and add sub_items using the **add_items()** command

    * You can nest this functionality (see example below)
    * For commands, either pass a command in a string or a function without the "()"

  3. Compile the model.

  .. code-block:: python

      def foo2(filenames):
          print('foo2')
          print(filenames)
          input()

      def foo3(filenames):
          print('foo3')
          print(filenames)
          input()


      if __name__ == '__main__':
          from context_menu import menus

          cm = menus.ContextMenu('Foo menu', type='DIRECTORY_BACKGROUND')
          cm.add_items([
              menus.ContextCommand('Foo One', command='echo hello > example.txt'),
              menus.ContextCommand('Foo Two', python=foo2),
              menus.ContextCommand('Foo Three', python=foo3)
          ])
          cm.compile()

  A **ContextCommand** is the item that is selectable on a menu, so the entry that actually runs a command. A **ContextMenu** simply holds the commands. Menus can be nested, so you can create subsubsubmenus if you really wanted to.
  Simply add them to a menu as you would a command. See examples for more information.

  You'll probably find some useful methods in the windows sub package, such as deleting keys and all their subkeys from the registry.

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   modules
