import lambda_function

from bs4 import BeautifulSoup

# run manually
# python3 -m pytest test_lambda_function.p


def test_stock_changed_still_instock():
    assert lambda_function.stock_changed(True, True) == False


def test_stock_changed_still_out_of_stock():
    assert lambda_function.stock_changed(False, False) == False


def test_stock_changed_now_in_stock():
    assert lambda_function.stock_changed(True, False) == True


def test_stock_changed_now_out_of_stock():
    assert lambda_function.stock_changed(False, True) == True


def test_in_stock_no_soup():
    assert lambda_function.in_stock(
        None, 'class', 'instock', 'outofstock') == False


def test_in_stock_no_button_class():
    assert lambda_function.in_stock(BeautifulSoup(
        ''), 'class', 'instock', 'outofstock') == False


def test_in_stock_product_in_stock():
    with open("test_resources/test_page1.html") as tp1:
        soup = BeautifulSoup(tp1, 'html.parser')
        assert lambda_function.in_stock(
            soup, 'stock-button', 'Add product to cart', 'Product out of stock') == True


def test_in_stock_product_out_of_stock():
    with open("test_resources/test_page2.html") as tp2:
        soup = BeautifulSoup(tp2, 'html.parser')
        assert lambda_function.in_stock(
            soup, 'stock-button', 'Add product to cart', 'Product out of stock') == False


def test_in_stock_not_sure():
    with open("test_resources/test_page3.html") as tp3:
        soup = BeautifulSoup(tp3, 'html.parser')
        assert lambda_function.in_stock(
            soup, 'stock-button', 'Add product to cart', 'Product out of stock') == False
