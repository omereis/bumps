import json, sys, os
#------------------------------------------------------------------------------
def get_in_name (input_name):
    in_file_name = None
    if os.path.exists(input_name):
        in_file_name = input_name
    else:
        name,ext = os.path.splitext(input_name)
        if len(ext) == 0:
            tmp_name = os.getcwd() + os.sep + name + '.json'
            if os.path.exists(tmp_name):
                in_file_name = tmp_name
    return in_file_name
#------------------------------------------------------------------------------
def get_out_name (input_name, out_name):
    results_name = None
    if out_name:
        name,ext = os.path.splitext(out_name)
        if len(ext) == 0:
            results_name = name + '.txt'
        else:
            results_name = out_name
    if results_name == None:
        name,ext = os.path.splitext(input_name)
        results_name = name + '.txt'
    return results_name
#------------------------------------------------------------------------------
def get_files_names():
    if len(sys.argv) > 2:
        out_base = sys.argv[2]
    else:
        out_base = None
    json_name = get_in_name (sys.argv[1])
    results_name = get_out_name (sys.argv[1], out_base)
    return json_name, results_name
#------------------------------------------------------------------------------
def read_refl1d_json(json_name):
    try:
        f = open(json_name,'r')
        file_text = f.read()
        json_text = file_text.replace('Infinity','1e308')
        j_debug = open('debug.json', 'w')
        j_debug.write(json_text)
        j_debug.close()
        json_data = json.loads(json_text)
    except Exception as e:
        print(f'read_refl1d_json runtime error: {e}')
    finally:
        f.close()
    return json_data
#------------------------------------------------------------------------------
def extract_layer_line(layer_json):
    layer_line = ''
    try:
        layer_line = str(layer_json['thickness']['value']) + '\t'
        layer_line += str(layer_json['interface']['value']) + '\t'
        layer_line += str(layer_json['rho']['value']) + '\t'
        layer_line += str(layer_json['irho']['value'])
    except Exception as e:
        layer_line = ''
        print(f'extract_refl runtime error: {e}')
    return layer_line
#------------------------------------------------------------------------------
def extract_refl(json_data):
    results = ['thickness' + '\t' + 'sld' + '\t' + 'mu' + '\t' + 'roughness']
    try:
        layers = json_data['sample']['layers']
        for n in range(len(layers)):
            line = extract_layer_line(layers[n])
            results.append(line)
        print(f'got results:\n{results}')
    except Exception as e:
        print(f'extract_refl runtime error: {e}')
    return '\n'.join(results)
#------------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print_usage()
    else:
        json_name, results_name = get_files_names()
        json_data = read_refl1d_json(json_name)
        refl_table = extract_refl(json_data)
        try:
            f = open(results_name, 'w')
            f.write(str(refl_table))
            print(f'results file {results_name} written')
        except Exception as e:
            print(f'results writing run time error: {e}')
        finally:
            f.close()
        if json_name == None:
            print(f'Input name {json_name} not found')
        else:
            print(f'Input file name: {json_name}')
        print(f'Output file name: {results_name}')
    print('\nThank you, come again')
    print('---------------------')

#------------------------------------------------------------------------------
def print_usage():
    print('Usage:')
    print(f'    python {__file__} <input_file[.json]> [<out_file>[.txt]>')
if __name__ == '__main__':
    main()
#------------------------------------------------------------------------------
