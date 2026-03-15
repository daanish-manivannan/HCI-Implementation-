import traceback
try:
    import main
    print('imported ok')
except Exception as e:
    traceback.print_exc()
except BaseException as e:
    traceback.print_exc()
