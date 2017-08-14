import re
import os
from os.path import join


def lower(api_name):
    return api_name[0].lower() + api_name[1:]


def param(method_name):
    return 'Query' if method_name == 'get' else 'Field'


def type_kt(type_name):
    return type_name.replace("Number", "Int")


if __name__ == '__main__':
    files = next(os.walk('src'))[2]
    for file in files:
        with open(join('src', file), encoding='utf-8') as f:
            # Get first apiGroup. It will be the output file name
            p = re.compile(r'\* @apiGroup (.+)')
            apiGroup = p.findall(f.read())[0]
            print(f'Writing {apiGroup}.kt')

            with open(apiGroup + '.kt', mode='w+', encoding='utf-8') as k:
                k.write('import retrofit2.http.*\n\n')
                k.write(f'interface {apiGroup} {{\n')

                f.seek(0)
                p = re.compile(r'/\*\*[\s\S]+?\*/')
                rp = p.findall(f.read())
                for a in rp:
                    p = re.compile(r'\* @api {(.+)} (\S+)')
                    rp = p.findall(a)[0]
                    method, url = rp[0], rp[1]

                    p = re.compile(r'\* @apiName (.+)')
                    apiName = p.findall(a)[0]
                    print(apiName)

                    p = re.compile(r'\* @apiParam {(.+)} (\S+)')
                    apiParam = p.findall(a)

                    k.write(f'    @FormUrlEncoded\n' if method == 'post' else '')
                    k.write(f'    @{method.upper()}("{url}")\n')
                    k.write(f'    fun {lower(apiName)}(')
                    k.write(', '.join([f'@{param(method)}("{p[1]}") {lower(p[1])}: {type_kt(p[0])}' for p in apiParam]))
                    k.write('): Any\n\n')
