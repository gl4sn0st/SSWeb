def main(args):
    name = args['name']

    ret = "Witaj, %s" % name

    return {'sentence': ret}
