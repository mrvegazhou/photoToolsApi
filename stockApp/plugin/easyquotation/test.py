# coding:utf8
import unittest
import api

if __name__ == "__main__":
    quotation = api.use("jsl")
    data = quotation.get_all_codes()
    print(data)