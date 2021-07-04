import sys
from doc_converter.app_wrapper import DocConverter

if __name__ == '__main__':
    convert_to = "png"
    try:
        convert_to = sys.argv[1]
    except Exception:
        pass
    dc = DocConverter(convert_to=convert_to)
    dc.run()
    del dc
