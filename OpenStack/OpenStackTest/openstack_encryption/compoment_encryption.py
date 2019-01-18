# coding: utf-8

def test_component_encryption():
    import re, os, random
    # os.system('tshark -i any -n -f "src port 5000" -a duration:60 -w ./openstack_encryption/test.txt')
    os.system('tshark -i any -n -f "src port 5000" -a duration:60 -w test.txt')
    html_data = []
    token_content = ''
    return_data = ''
    file = open('./openstack_encryption/test.txt')
    file = open('./test.txt')
    lines = file.readlines()
    data = reduce(lambda a, b: a+b, lines, '')
    for line in lines:
        if ('{' in line) and ('}' in line):
            html_data.append(line[:line.rfind('}')]+'\n\n')
        if token_content == '' and 'X-Subject-Token' in line:
            token_content = line

    heads = re.findall(r'Date:.+?\r\n\r\n', data, re.S)

    random.sample(range(0, len(html_data)-1), min(4, len(html_data)))

    for index in range(0, min(3, len(html_data))):
        return_data += 'HTTP/1.1 200 OK\n'+heads[index].strip('\n')+html_data[index]

    print return_data, token_content
    return return_data, token_content


# tshark -i any -R "tcp.port==5000" -T fields -e "http.file_data"

# tshark -i any -n -f "src port 5000" -a duration:60 -w test.txt
if '__name__' == '__main__':
    process_data()

