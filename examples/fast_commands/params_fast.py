
def foo1(filenames, params):
    print(filenames)
    print(params)
    input()

if __name__ == '__main__':
    from context_menu import menus

    fc = menus.FastCommand('Example Fast Command 1', type='FILES', python=foo1, params='a b c d e f')
    fc.compile()
