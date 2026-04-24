# Building PIL

## Setup Dependencies

Check <https://github.com/python-pillow/Pillow/blob/main/winbuild/build.rst>
for what needs to be installed via Visual Studio Installer
`
python winbuild\build_prepare.py --no-fribidi --no-imagequant
`

## Optimization Flags

To get better performance than provided builds, you can use a newer instruction set.
I tried using AVX instructions but those broke the build step.
`
SET CL=/arch:SSE4.2
`

## Compilation

`
winbuild\build\build_dep_all.cmd
winbuild\build\build_env.cmd
pip install --no-cache-dir -v -C raqm=disabled -C fribidi=disabled .
`
