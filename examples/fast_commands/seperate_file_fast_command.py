if __name__ == '__main__':
    from context_menu import menus
    from foo1 import bar1

    fc = menus.FastCommand('Example Fast Command 2', type='FILES', python=bar1)
    fc.compile()
