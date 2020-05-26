import sys
import os
sys.path.append('../production')

print(os.getcwd())
import menus

def foo1(filenames):
    print(filenames)
    input()

if __name__ == '__main__':
    fastCom = menus.FastCommand('FooTest2', 'FILES', python=foo1)
    fastCom.compile()
