import re

def extract_function_comments(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    functions = []
    comments = []
    current_comment = None
    nombres_completos = []

    for line in lines:
        function_match = re.match(r'^(.*) ?\(.*\) ?: .*', line)
        comment_match = re.match(r'^# *(.*)', line)

        if function_match:
            function = function_match.group(1)
            functions.append(function)
            nombres_completos.append(function_match.group(0))

            if current_comment:
                comments.append(current_comment.strip())
                current_comment = None

        elif comment_match:
            comment = comment_match.group(1)
            if current_comment:
                current_comment += '\n' + comment
            else:
                current_comment = comment

    # Add the last comment if it exists
    if current_comment:
        comments.append(current_comment.strip())

    function_comments = dict(zip(functions, comments))
    function_nombres = dict(zip(functions, nombres_completos))

    return function_comments, function_nombres


def write_list_to_file(lines, file_path):
    with open(file_path, 'w') as file:
        for line in lines:
            file.write(line + '\n')



comentarios, nombres_completos = extract_function_comments('comentarios.txt')

with open("views.py", 'r') as file:
    lines = file.readlines()

output = []

for line in lines:
    function_match = re.match(r'def (.*) ?\(.*\):', line)

    if function_match:
        function = function_match.group(1)

        # Adds the comment to the function
        if function in comentarios:
            comment = comentarios[function]
            
            # Removes the earlier comments
            i = len(output) - 1
            while output[i].startswith('#'):
                output.pop(i)
                i -= 1
          
            output.append("@csrf_exempt")
            output.append(line.replace('\n', ''))

            splitted_comment = comment.split('\n')

            output.append("    \"\"\"")
            for comment_line in splitted_comment:
                output.append("    "+comment_line)

            output.append("    Sintaxis de la función: " + nombres_completos[function]) 
            output.append("    \"\"\"") 
            output.append("")

        else:
            output.append("# La función " + function + " no está en la API")
            output.append("@csrf_exempt")
            output.append(line.replace('\n', ''))    
    else:
        csrf_exempt_match = re.match(r'@csrf_exempt *', line)
        if not csrf_exempt_match:
            output.append(line.replace('\n', ''))


write_list_to_file(output, 'views_prueba.py')
            

