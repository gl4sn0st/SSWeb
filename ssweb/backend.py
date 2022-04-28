from importlib.machinery import SourceFileLoader

def run_backend(file, variables):
    backend_file = SourceFileLoader("main", file).load_module()
    data = backend_file.main(variables)

    return data
