import sys, json
#------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
        try:
            file = open (name, 'r')
            string = file.read()
            print(f'File: {string}')
            param = json.loads(string)
            print(f'JSON: {param}')
            file.close()
        except Exception as e:
            print(f'Runtime error: {e}')
            exit(1)
    else:
        print(f'Usage:\n\
            python {__file__} <parameters file name>')