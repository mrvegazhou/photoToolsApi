

def get_stock_type(stock_code) -> str:
    assert type(stock_code) is str, "stock code need str type"
    if stock_code.startswith(('600', '601', '603', '688')):
        return 'sh'
    elif stock_code.startswith(('000', '001', '002')):
        return 'sz'
    elif stock_code.startswith('300'):
        return 'sz'
    elif stock_code.startswith(('83', '87')):  # 注意：北交所代码可能有所变化，这里只是示例
        return 'bj'
    else:
        return ''