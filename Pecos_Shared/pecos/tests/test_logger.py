from nose.tools import *
import pandas as pd
import pecos

def test_initialize():
    pecos.logger.initialize()
    
    assert_equals(0, 0)
