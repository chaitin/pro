import os
import jinja2

def process(raw, path=[], **ctx):
    path.append('.')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(path),
            line_comment_prefix='//', comment_start_string='/*',
            comment_end_string='*/')
    template = env.from_string(raw)
    ctx.update(__builtins__)
    return template.render(MODULES=set(), **ctx)

def process_file(script, path=[], **ctx):
    script_path = os.path.dirname(os.path.realpath(script))
    path.append(script_path)
    with open(script) as f:
        return process(f.read(), path, **ctx)
