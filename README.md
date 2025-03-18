# Intro

This aims to create a pip package for iText 9 distribution


# Build 

To build the package, just run:

```
python -m build
```

which should create a file:

```
./dist/itext_python-9.1.0-py3-none-any.whl
```

that then you can install by using

```
pip install ./dist/itext_python-9.1.0-py3-none-any.whl --force-reinstall
```


# Limitations

* ~~You still need to download the DDLs file yourself (TODO)~~
```python itext_python/download-dlls.py```
* The way the packages are exposed, everything is under the same namespace, which can be confusing
* Not all packages/Classes are exposed, only the basic ones (check [here](https://github.com/avlemos/itext-python/blob/7678e0dbaaeed53c026f32ac3487f080aa710663/itext_python/__init__.py#L16) to change it)


# Needed DLLs
(you can use [download-dlls.py](itext_python/download-dlls.py) to get them)

* BouncyCastle.Cryptography.dll
* Microsoft.DotNet.PlatformAbstractions.dll
* Microsoft.Extensions.DependencyModel.dll
* Microsoft.Extensions.Logging.Abstractions.dll
* Microsoft.Extensions.Logging.dll
* Microsoft.Extensions.Options.dll
* itext.bouncy-castle-adapter.dll
* itext.bouncy-castle-connector.dll
* itext.commons.dll
* itext.io.dll
* itext.kernel.dll
* itext.layout.dll
