import lambda_function

def test_stock_changed_still_instock():
    assert lambda_function.stock_changed(True, True) == False

def test_stock_changed_still_out_of_stock():
    assert lambda_function.stock_changed(False, False) == False

def test_stock_changed_now_in_stock():
    assert lambda_function.stock_changed(True, False) == True

def test_stock_changed_now_out_of_stock():
    assert lambda_function.stock_changed(False, True) == True