'''
   This library provides some simple routines for doing templating.
   Owain Kenway, 2017
'''

# Apply dictionary of key, replacements to string s.
def templatestring(s, keys):
    r = s
    for a in keys.keys():
        r = r.replace(a, str(keys[a]))
        
    return r

# Apply dictionary of key, replacements to file.
def templatefile(filename, keys):
    f = open(filename, 'r')
    s = f.read()
    f.close()

    return templatestring(s = s, keys = keys)
