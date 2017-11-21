import re
import os
from os.path import join
from inflection import camelize

import config


def param(method_name):
    return 'Query' if method_name == 'get' else 'Field'


def type_kt(type_name):
    return type_name.replace("Number", "Int").replace('Object', 'Any')


if __name__ == '__main__':
    files = next(os.walk('src'))[2]
    for file in files:
        with open(f'output/Data.kt', mode='a+', encoding='utf-8') as d:
            with open(join('src', file), encoding='utf-8') as f:
                # Get first apiGroup. It will be the output file name
                p = re.compile(r'\* @apiGroup (.+)')
                pf = p.findall(f.read())
                if len(pf) == 0:
                    continue
                apiGroup = pf[0]
                print(f'Writing {apiGroup}.kt')

                with open(f'output/{apiGroup}.kt', mode='w+', encoding='utf-8') as k:
                    k.write(f'package {config.PACKAGE}\n\n')
                    k.write('import retrofit2.http.*\n\n')
                    k.write(f'interface {apiGroup} {{\n')

                    f.seek(0)
                    p = re.compile(r'/\*\*[\s\S]+?\*/')
                    rp = p.findall(f.read())
                    for a in rp:
                        p = re.compile(r'\* @api {(.+)} (\S+)')
                        pf = p.findall(a)
                        if len(pf) == 0:
                            continue
                        rp = pf[0]
                        method, url = rp[0], rp[1]

                        p = re.compile(r'\* @apiName (.+)')
                        apiName = p.findall(a)[0]
                        print(apiName)

                        p = re.compile(r'\* @apiParam {(.+)} (\S+)')
                        apiParamAll = p.findall(a)
                        # Filter Objects
                        apiParam = filter(lambda aa: '.' not in aa[1], apiParamAll)

                        k.write(f'    @FormUrlEncoded\n' if method == 'post' else '')
                        k.write(f'    @{method.upper()}("{url}")\n')
                        k.write(f'    fun {camelize(apiName,False)}(')
                        k.write(', '.join(
                            [f'@{param(method)}("{p[1]}") {camelize(p[1], False)}: {type_kt(p[0])}' for p in apiParam]))
                        k.write('): Any\n\n')

                        p = re.compile(r'\* @apiSuccess {(.+)} (\S+)')
                        apiSuccessAll = p.findall(a)
                        # Filter Objects
                        apiSuccess = filter(lambda aa: '.' not in aa[1], apiSuccessAll)
                        print(apiSuccessAll)

                        d.write(f'data class {camelize(apiName)}Response(')
                        d.write(', '.join([f'val {camelize(s[1], False)}: {type_kt(s[0])}' for s in apiSuccess]))
                        d.write(')\n')
                    k.write('}\n')
