# HTML generation module

def make_tag(tag_name, contents, args_dict=None):
        open_tag = make_open_tag(tag_name, args_dict)
        #open_tag[-1:3] = '>'
        return open_tag + contents + "</%s>" % tag_name

def make_open_tag(tag_name, args_dict=None):
        param_str = ''
        if args_dict:
                param_str_list = [ key + '="' + val + '"' for key, val in args_dict.items() ]
                param_str = ' '.join(param_str_list)

        return "<%s %s>" % (tag_name, param_str)

