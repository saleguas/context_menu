if __name__ == '__main__':
    from context_menu import menus

    fc = menus.FastCommand('Example Fast Command 5', type='FILES', command='cd ? & mkdir hello', command_vars=['DIR'])
    fc.compile()
