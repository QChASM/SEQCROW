#!/usr/bin/env python2

import re
import os

def integrate(fun, a, b, n=101):
    """numerical integration using Simpson's method
    fun - function to integrate
    a - integration starts at point a
    b - integration stops at point b
    n - number of points used for integration"""
    import numpy as np
    
    dx = float(b-a)/(n-1)
    x_set = np.linspace(a, b, num=n)
    s = -(fun(a) + fun(b))
    i = 1
    max_4th_deriv = 0
    while i < n:
        if i % 2 == 0:
            s += 2*fun(x_set[i])
        else:
            s += 4*fun(x_set[i])
        
        if i < n-4 and i >= 3:
            sg_4th_deriv = 6*fun(x_set[i-3]) + 1*fun(x_set[i-2]) - 7*fun(x_set[i-1]) - 3*fun(x_set[i]) - 7*fun(x_set[i+1]) + fun(x_set[i+2]) + 6*fun(x_set[i+3])
            sg_4th_deriv /= 11*dx**4
            
            if abs(sg_4th_deriv) > max_4th_deriv:
                max_4th_deriv = abs(sg_4th_deriv)
        
        i += 1
        
    s = s * dx/3.
    
    #close enough error estimate
    #AaronTools immediately discards the error estimate anyways
    e = (abs(b-a)**5)*max_4th_deriv/(180*n**4)
    
    return (s, e)
 
def proj(x, y):
    """projection of x onto y"""
    import numpy as np
    
    x = np.reshape(x, len(x))
    y = np.reshape(y, len(y))
    m = np.dot(x, y)/np.dot(y, y)
    
    return m*y
 
def gram_schmidt(current_basis):
    """returns vectors to expand the current basis to span R^n
    assumes the vectors already in current_basis are linearly independent"""
    import numpy as np
    from ChimAARON.backporter import proj
    
    full_basis = current_basis
    basis = []
    n = len(current_basis[0])
    for i in range(len(current_basis), n):
        vi = np.zeros(n)
        vi[i] += 1
        ui = vi - sum([proj(uj, vi) for uj in full_basis])
        basis.append(np.reshape(ui, (len(ui), 1)))
        full_basis.append(basis[-1])
     
    #transpose because this is used to replace null space, which we transpose
    return np.transpose(np.array(basis))

def backporter_main(directory):
    for root, dirs, files in os.walk(directory, topdown=True):
        for f in files:
            if f.endswith('.py'):
                filename = os.path.join(root, f)
                
                fix_isinstance_str(filename)
                #fix_scipy_integrate(filename)
                #fix_scipy_nullspace(filename)
                fix_filenotfounderror(filename)
                fix_jsondecodeerror(filename)
                fix_kwarg_order(filename)
                fix_json_dump(filename)
                fix_list_copy(filename)
                #fix_open_encoded_filename(filename) #it turns out this was an issue because I had AaronTools in a Dropbox folder...
                
                if 'test' in filename:
                    fix_unittest_results(filename)
                    
                if "atoms.py" in filename:
                    add_def_eq(filename)
                
def split_imports(file_contents):
    """returns a tuple of (list of lines before we stop importing, list of lines after we stop importing)"""
    from chimera import replyobj
    i = 0
    for line in file_contents:
        if line.startswith('import') or line.startswith('from') or line.startswith('#') or line.startswith('"') or not line.strip() or line.startswith('standard_library.install_aliases()'):
            i += 1
        else:
            break
    
    print(i)
    replyobj.status(str(i))
    imports = file_contents[:i]
    code = file_contents[i:]
    
    return (imports, code,)

def split_classes(code):
    classes = [[]]
    for line in code:
        if line.startswith('class'):
            classes.append([])
        classes[-1].append(line)

    return classes

def fix_isinstance_str(filename):
    """changes isinstance(x, str) to isinstance(x, basestring)"""
    import re
    
    isinstance_str = re.compile('(.*isinstance\(.*?, )str(\).*)')
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    s = ''
    for i in range(0, len(lines)):
        match = isinstance_str.match(lines[i])
        if match is not None:
            lines[i] = match.group(1) + 'basestring' + match.group(2) + '\n'
            
        s += lines[i]
        
    with open(filename, 'w') as f:
        f.write(s)
        
def fix_scipy_integrate(filename):
    """replaces scipy's integrate.quad with the crappy (good enough) one in ChimAARON.backporter"""
    import re
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    print(filename)
    imports, code = split_imports(lines)
    
    fix_integrate = False
    
    for i in range(0, len(imports)):
        if 'from scipy import integrate' in imports[i]:
            imports[i] = imports[i].replace('', '#', 1) + '\nfrom ChimAARON.backporter import integrate\n'
            fix_integrate = True
            
    if fix_integrate:
        #integrate is used to normalize interpolation stuff
        #interpolation stuff is used by 'follow'
        integrate_scipy = re.compile('(.*)(integrate\..*?\()(.*)')
    
        for i in range(0, len(code)):
            match = integrate_scipy.match(code[i])
            if match is not None:
                code[i] = match.group(1) + 'integrate(' + match.group(3) + '\n'

        s = ''
        
        for line in imports:
            s += line
            
        for line in code:
            s += line
            
        with open(filename, 'w') as f:
            f.write(s)

def fix_scipy_nullspace(filename):
    """there's some bs with scipy/numpy compatibility, so this replaces 
    from scipy.linalg import null_space 
    with
    from ChimAARON.backporter import gram_schmidt
    and replaces null_space calls with gram_schmidt calls
    gram_schmidt is not null_space, but the way null_space is used,
    it has the same effect
    ChimAARON should never need to use null_space anyways"""
    import re
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    print(filename)
    imports, code = split_imports(lines)
    
    fix_nullspace = False
    for i in range(0, len(imports)):
        if 'trajectory' in filename:
            print(imports[i])
        if 'from scipy.linalg import null_space' in imports[i]:
            imports[i] = imports[i].replace('', '#', 1) + '\nfrom ChimAARON.backporter import gram_schmidt\n'
            fix_nullspace = True
            print('fix null space')
            
    if fix_nullspace:
        #null_space is in the code, but  ChimAARON should never encounter it
        nullspace = re.compile('(.*)(null_space\()(.*)')
        
        for i in range(0, len(code)):
            match = nullspace.match(code[i])
            if match is not None:
                code[i] = match.group(1) + 'gram_schmidt(' + match.group(3) + '\n'
                
        s = ''
        
        for line in imports:
            s += line
            
        for line in code:
            s += line
            
        with open(filename, 'w') as f:
            f.write(s)
            
def fix_filenotfounderror(filename):
    """adds FileNotFoundError = IOError to files that need it
    NOTE: IOError is not the same thing as FileNotFoundError
    there are a number of other things that can throw IOError
    we should really be checked to see if the file exists instead of 
    trying to handle a FileNotFoundError"""
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    fix = False
    for line in lines:
        if 'FileNotFoundError' in line:
            fix = True
            
    if fix:
        imports, code = split_imports(lines)
        imports.append('\nFileNotFoundError = IOError\n')
        
        s = ''
        for line in imports:
            s += line
        
        for line in code:
            s += line
            
        with open(filename, 'w') as f:
            f.write(s)
            
def fix_jsondecodeerror(filename):
    """adds JSONDecodeError = ValueError to files that need JSONDecodeError defined"""
    jsondecodeerror = re.compile('(.*\s)(.*JSONDecodeError)(.*)')
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    imports, code = split_imports(lines)
    
    fix = False
    for i in range(0, len(code)):
        match = jsondecodeerror.match(code[i])
        if match is not None:
            code[i] = match.group(1) + 'JSONDecodeError' + match.group(3) + '\n'
            fix = True
            
    if fix:
        imports.append('\nJSONDecodeError = ValueError\n')
        
    s = ''
    
    for line in imports:
        s += line
        
    for line in code:
        s += line
        
    with open(filename, 'w') as f:
        f.write(s)
        
def fix_kwarg_order(filename):
    """this changes **kwargs to be last in function calls"""
    import re
    
    kwargs_first = re.compile('(.*\(.*)\*\*kwargs,\s(.*)\)(.*)')
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    s = ''
    for line in lines:
        match = kwargs_first.match(line)
        if match is not None and 'def' not in line:
            line = match.group(1) + match.group(2) + ', **kwargs)\n'
        
        s += line
        
    with open(filename, 'w') as f:
        f.write(s)
        
def fix_open_encoded_filename(filename):
    """whatever 'open' future's builtins module uses, it doesn't like to open some types of filenames?
    this converts some filename to raw strings"""
    import re
    
    open_re = re.compile('(.*\sopen\()(.*),(.*)')
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    s = ''
    for line in lines:
        match = open_re.match(line)
        if match is not None:
            name = match.group(2)
            name = "__builtins__['str'](r\"%%s\" %% %s)" % name
                
            s += "%s%s,%s\n" % (match.group(1), name, match.group(3))
            
        else:
            s += line
            
    with open(filename, 'w') as f:
        f.write(s)
        
def fix_json_dump(filename):
    """for some reason, when json puts together the content to the json file, it doesn't make sure
    the content is unicode before it tries to write to the file..."""
    import re
    
    json_dump = re.compile('(\s+?)json.dump\((.*),(.*)\)')
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    s = ''
    for line in lines:
        match = json_dump.match(line)
        if match is not None:
            name = match.group(3).strip()
            dict = match.group(2)
            
            s += "%s%s.write(unicode(json.dumps(%s)))\n" % (match.group(1), name, dict)
            
        else:
            s += line
            
    with open(filename, 'w') as f:
        f.write(s)

def fix_unittest_results(filename):
    """unittest changed the names of some things in 3.4"""
    import re
    
    unittest_outcome = re.compile('(.*)_outcome.result(.*)')
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    s = ''
    for line in lines:
        match = unittest_outcome.match(line)
        if match is not None: 
            print(filename, match)
            s += "%s_resultForDoCleanups%s\n" % (match.group(1), match.group(2))
        else:
            s += line
            
    with open(filename, 'w') as f:
        f.write(s)

def fix_list_copy(filename):
    """list.copy() was added after python 2.7 - change x = var.copy to
    if isinstance(var, list):
        x = var[:]
    else:
        x = var.copy()
    """
    import re
    
    json_dump = re.compile('(\s+?)([\S].*=\s+?[^A-Za-z]?)([A-Za-z]*)\.copy\(\)(.*)')
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    s = ''
    for line in lines:
        match = json_dump.match(line)
        if match is not None:
            inden = match.group(1)
            assign = match.group(2)
            var = match.group(3)
            end = match.group(4)
            
            s += "%sif isinstance(%s, list):\n" % (inden, var)
            s += "    %s%s %s[:]%s\n" % (inden, assign, var, end)
            s += "%selse:\n" % inden
            s += "    %s" % line            
            
        else:
            s += line
            
    with open(filename, 'w') as f:
        f.write(s)

def add_def_eq(filename):
    """Python 3's __eq__ just works with our object
    Python 2's __eq__... not so much"""
    
    print('add __eq__')
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    imports, code = split_imports(lines)

    classes = split_classes(code)
    
    for c in classes[1:]:
        if not any(['def __eq__' in line for line in c]) and any(['def __repr__' in line for line in c]):
            c.append("\n    def __eq__(self, other): return repr(self) == repr(other)\n")
            
    s = ''
    
    for line in imports:
        s += line
        
    for c in classes:
        for line in c:
            s += line
            
    with open(filename, 'w') as f:
        f.write(s)
    