project('browser', 'cpp',
  version : '0.1',
  default_options : ['warning_level=3', 'cpp_std=c++20'])

fmt = subproject('fmt')
fmt_dep = fmt.get_variable('fmt_dep')

sources = [
  'src/main.cpp',
  'src/url.cpp'
]

executable('browser',
           sources,
           install : true,
           dependencies : [fmt_dep])
