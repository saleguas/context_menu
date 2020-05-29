# <center> context_menu </center>

<Center> A Python library to create and deploy cross-platform native context menus.</center>


---


![build passing](https://travis-ci.com/saleguas/context_menu.svg?token=STF1haAqx5Xq2x9zdkHH&branch=master)   ![readthedocs](https://img.shields.io/readthedocs/context_menu) ![pip](https://img.shields.io/badge/pip-context__menu-blue)

---




![example usage](media/thumbnail.gif)

# Quickstart

1. Install the library via pip:
```
python -m pip install context_menu
```
2. Create and compile the menu:
  * You can create items in as little as 3 lines:
    ```python
    from context_menu import menus
    fc = menus.FastCommand('Example Fast Command 1', type='FILES', command='echo Hello')
    fc.compile()
    ```
  * Or you can create much more complicated nested menus:
```Python
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
3. See the output!
  * First example

  ![first Example](media/first_example.png)

  * Second example

  ![second Example](media/second_example.png)

# Detailed Usage

The [ContextMenu]() class expects a name, and the activation type if it is the root menu(the first menu). Only compile the root menu.

The [ContextCommand]() class expects a name, and either a python function, or a shell command, but not both. A ContextCommand is the selectable element of a context menu; you can click this part. Python functions can be passed to this method, regardless of their location. However, if the function is in the same file as the menu, you have to surround it with `if __name__ == '__main__':`

```python
def foo1(filenames):
    print(filenames)
    input()

if __name__ == '__main__':
    from context_menu import menus

    fc = menus.FastCommand('Example Fast Command 1', type='FILES', python=foo1)
    fc.compile()
```

Any command passed (as a string) will be directly ran from the shell.

The [FastCommand]() class is an extension of the ContextMenu class and allows you to quickly create a single entry menu. It expects a name, type, and command/function.

You can use the [{MENU}.add_items{ITEMS}]() function to add these elements together. Menus can be added to menus, creating cascading context menus. You have to call [{MENU}.compile()]() in order to create the menu. Admin privileges are required on windows, as it modifies the Registry. The code will automatically prompt for Admin rights if it is not sufficiently elevated.

Check out the [examples folder](examples) for more complicated examples.
