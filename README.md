# 💻 context_menu 💻

A Python library to create and deploy cross-platform native context menus.

![build passing](https://travis-ci.com/saleguas/context_menu.svg?token=STF1haAqx5Xq2x9zdkHH&branch=master)   ![readthedocs](https://img.shields.io/readthedocs/context_menu) ![pip](https://img.shields.io/badge/pip-context__menu-blue) ![python version](https://img.shields.io/pypi/pyversions/context_menu)

* * *

![example usage](media/thumbnail2.gif)

# Quickstart

1.  Install the library via pip:


    python -m pip install context_menu

2.  Create and compile the menu:

-   You can create menus in as little as 3 lines:
    ```python
    from context_menu import menus
    fc = menus.FastCommand('Example Fast Command 1', type='FILES', command='echo Hello')
    fc.compile()
    ```
-   Or you can create much more complicated nested menus:

```Python
        def foo2(filenames, params):
            print('foo2')
            print(filenames)
            input()

        def foo3(filenames, params):
            print('foo3')
            print(filenames)
            input()

        if __name__ == '__main__':
            from context_menu import menus

            cm = menus.ContextMenu('Foo menu', type='FILES')
            cm2 = menus.ContextMenu('Foo Menu 2')
            cm3 = menus.ContextMenu('Foo Menu 3')

            cm3.add_items([
                menus.ContextCommand('Foo One', command='echo hello > example.txt'),
            ])
            cm2.add_items([
                menus.ContextCommand('Foo Two', python=foo2),
                cm3,
            ])
            cm.add_items([
                cm2,
                menus.ContextCommand('Foo Three', python=foo3)
            ])

            cm.compile()
```

3.  See the output!

-   First example

    ![first Example](media/first_example.png)

-   Second example

    ![second Example](media/second_example.png)

# Detailed Usage

## `ContextMenu` Class

The [ContextMenu](https://context-menu.readthedocs.io/en/latest/context_menu.html#context_menu.menus.ContextMenu) object holds other context objects. It expects a name, and the activation type if it is the root menu(the first menu). Only compile the root menu.

```Python
ContextMenu(name: str, type: str = None)
```

Menus can be added to menus, creating cascading context menus. You can use the [{MENU}.add_items{ITEMS}](https://context-menu.readthedocs.io/en/latest/context_menu.html#context_menu.menus.ContextMenu.add_items) function to add context elements together, for example:

```Python
cm = menus.ContextMenu('Foo menu', type='DIRECTORY_BACKGROUND')
cm.add_items([
    menus.ContextMenu(...),
    menus.ContextCommand(...),
    menus.ContextCommand(...)
])
cm.compile()
```

You have to call [{MENU}.compile()](https://context-menu.readthedocs.io/en/latest/context_menu.html#context_menu.menus.ContextMenu.compile) in order to create the menu.

## `ContextCommand` Class

The [ContextCommand](https://context-menu.readthedocs.io/en/latest/context_menu.html#context_menu.menus.ContextCommand) class creates the selectable part of the menu (you can click it). It requires a name, and either a Python function or a command **(but NOT both)** and has various other options

```Python
ContextCommand(name: str, command: str = None, python: 'function' = None, params: str=None, command_vars: list=None)
```

Python functions can be passed to this method, regardless of their location. **However, the function must accept only two parameters `filenames`, which is a list of paths\*, and `params`, the parameters passed to the function**. and if the function is in the same file as the menu, you have to surround it with `if __name__ == '__main__':`

Any command passed (as a string) will be directly ran from the shell.

## `FastCommand` Class

The [FastCommand](https://context-menu.readthedocs.io/en/latest/context_menu.html#context_menu.menus.FastCommand) class is an extension of the ContextMenu class and allows you to quickly create a single entry menu. It expects a name, type, and command/function.

```python
FastCommand(name: str, type: str, command: str = None, python: 'function' = None, params: str = '', command_vars: list = None)
```

```python
def foo1(filenames, params):
    print(filenames)
    input()

if __name__ == '__main__':
    from context_menu import menus

    fc = menus.FastCommand('Example Fast Command 1', type='FILES', python=foo1)
    fc.compile()
```

~~Admin privileges are required on windows, as it modifies the Registry. The code will automatically prompt for Admin rights if it is not sufficiently elevated.~~

# Advanced Usage

## `removeMenu` method

You can remove a menu easily as well. Simply call the ['menus.removeMenu()'](<>) method.

```python
removeMenu(name: str, type: str)
```

For example, if I wanted to remove the menu 'Foo Menu' that activated on type 'FILES':

```python
from context_menu import menus

menus.removeMenu('Foo Menu', 'FILES')
```


## `params` Command Parameter

In both the `ContextCommand` class and `FastCommand` class you can pass in a parameter, defined by the `parameter=None` variable. **This value MUST be a string!** This means instead of passing a list or numbers, pass it as a string separated by spaces or whatever to delimitate it.

```Python
fc = menus.FastCommand('Example Fast Command 1', type='FILES', python=foo1, params='a b c d e')
fc.compile()
```

For more information, [see this.](https://github.com/saleguas/context_menu/issues/4)

Works on the `FastCommand` and `ContextCommand` class.

## `command_vars` Command Parameter

If you decide to pass a shell command, you can access a list of special variables. For example, if I wanted to run a custom command with the file selected, I could use the following:

```Python
fc = menus.FastCommand('Weird Copy', type='FILES', command='touch ?x', command_vars=['FILENAME'])
fc.compile()
```

which would create a new file with the name of whatever I selected with an 'x' on the end. The `?` variable is interpreted from left to right and replaced with the selected values [(see this)](https://github.com/saleguas/context_menu/issues/3).

All of the preset values are as follows:

| Name          | Function                                |
| ------------- | --------------------------------------- |
| FILENAME      | The path to the file selected           |
| DIR/DIRECTORY | The directory the script was ran in.    |
| PYTHONLOC     | The location of the python interpreter. |

Works on the `FastCommand` and `ContextCommand` class.

## Opening on Files

Simply pass the extension of the file you want to open onto when creating the menu.

```Python
fc = menus.FastCommand('Weird Copy', type='.txt', command='touch ?x', command_vars=['FILENAME']) # opens on .txt files
fc.compile()
```

* * *

Check out the [examples folder](examples) for more complicated examples.

# Types

There are different locations where a context menu can fire (if you right click on a folder you'll get different options then if you right click on a file).  The `type` variable controls this behavior in the library, and you can reference this table to determine the `type`:

| Name                 | Location                                                           | Action                                   |
| -------------------- | ------------------------------------------------------------------ | ---------------------------------------- |
| FILES                | HKEY_CURRENT_USER\\Software\\Classes\\\*\\shell\\                  | Opens on a file                          |
| DIRECTORY            | HKEY_CURRENT_USER\\Software\\Classes\\Directory\\shell             | Opens on a directory                     |
| DIRECTORY_BACKGROUND | HKEY_CURRENT_USER\\Software\\Classes\\Directory\\Background\\shell | Opens on the background of the Directory |
| DRIVE                | HKEY_CURRENT_USER\\Software\\Classes\\Drive\\shell                 | Opens on the drives(think USBs)          |

# Important notes

-   ~~The code can sometimes be really weird when it comes to admin rights on Windows. The `compile()` method will automatically prompt for admin rights if required, but this can cause issues sometimes.~~ Admin rights no longer required as of version 1.2.0.

-   Almost all of the errors I've encountered in testing were when the code and the functions were in the same file. You should make a separate file for the code or surround it with `if __name__ == '__main__':`.

Feel free to check out a [file sorter](https://github.com/saleguas/freshen) I made that implements very complex usage of this library.

You can check out the official documentation [here](https://context-menu.readthedocs.io/en/latest/index.html).
