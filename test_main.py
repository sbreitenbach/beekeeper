import main

# These two tests can be removed 
# They simply serve as inital environment setup checks
def test_plways_passes():
    a = 1
    assert(a==1) 

def test_calling_function():
    b = main.returns_true()
    assert(b)